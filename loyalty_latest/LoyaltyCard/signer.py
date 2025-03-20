import os
import json
import hashlib
import random
import subprocess
from pathlib import Path
from io import BytesIO
from django.core.files import File
from storages.backends.azure_storage import AzureStorage
from loyalty_latest.models import Passes, UserCard
from django.core.files.storage import default_storage
from zipfile import ZipFile
import requests
# ---- ƏSAS FUNKSİYA ----

def delete_file_from_azure(file_name):
    try:
        # Try to delete the file from Azure Storage using the default storage system
        if default_storage.exists(file_name):
            default_storage.delete(file_name)
            print(f"File {file_name} deleted successfully.")
        else:
            print(f"File {file_name} does not exist.")
    except Exception as e:
        print(f"Error deleting file {file_name}: {str(e)}")

def generate_loyalty_card_and_pass(name, surname, level, card_number,download_hash, logo_url, icon_url, background_color, text_color, device_type, user_card_id):
    base_dir = Path("D:/BYQR/Byqr-back-main/loyalty_latest/LoyaltyCard")
    card_id = random.randint(100000, 999999)
    work_dir = base_dir / "signing_files" / f"card_{card_id}"
    work_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: JSON + şəkillər
    pass_json, logo_data, icon_data = generate_pass_json(name, surname, level, card_number, logo_url, icon_url, background_color, text_color)

    # Step 2: Manifest yaradılır
    assets = {
        
        "icon.png":icon_data,
        "strip.png":icon_data,
    }
    manifest = generate_manifest(assets, pass_json)

    # Step 3: Manifest imzalanır
    signature = sign_manifest(manifest, work_dir=work_dir)

    # Step 4: .pkpass faylı yaradılır
    pkpass_buffer = create_pkpass(pass_json, assets, manifest, signature)


    # Step 5: Retrieve the UserCard instance
    user_card = UserCard.objects.get(id=user_card_id)
    pass_delete = Passes.objects.filter(user_card=user_card).exists()
    # Step 6: Check and delete the previous pass file if it exists
    if pass_delete:
        try:
            delete_file_from_azure('pass_files/'+download_hash+".pkpass")
            pass_delete = Passes.objects.get(user_card=user_card)
            pass_delete.delete()
        except Exception as e:
            print(f"Error deleting the previous pass: {e}")

    # Step 7: Save the new file to Azure Storage
    file_name = f"{download_hash}.pkpass"
    azure_storage = AzureStorage()

    # Upload the file to Azure Blob Storage
    file = File(pkpass_buffer, name=file_name)

    # Create the new pass instance and link it to the user card
    pass_instance = Passes.objects.create(
        device_type=device_type,
        pass_file=file,  # Save the file directly to Azure Storage
        user_card=user_card
    )

    # Step 8: Update the UserCard with the new download hash
    user_card.download_hash = download_hash
    user_card.save()

    # Return the URL of the uploaded file in Azure Storage
    return pass_instance.pass_file.url

# ---- JSON və şəkil dummy məlumatları ----
'''
"headerFields": [
            
           {
                "key": "bonus",
                "label": "Bonus",
                "value": '150',
                "textColor": text_color.upper()
            },
            
        ],'''
def generate_pass_json(name, surname, level, card_number, logo_url, icon_url, background_color, text_color):
    
    pass_json = {
    "description": "BYQR Loyalty",
    "formatVersion": 1,
    "organizationName": "BYQR",
    "passTypeIdentifier": "pass.com.byqr.loyalty",
    "serialNumber": str(card_number),
    "teamIdentifier": "WZP44UK52K",
    "backgroundColor": background_color.upper(),
    "foregroundColor": text_color.upper(),
    "labelColor": text_color.upper(),
 
    "barcode": {
        "message": str(card_number),
        "format": "PKBarcodeFormatQR",
        "messageEncoding": "iso-8859-1"
    },
    "storeCard": {
       
        "primaryFields":[],
        "secondaryFields": [
           {
                "key": "level",
                "label": "Level",
                "value": level,
                "textColor": text_color.upper()
            },
             {
                

                "key": "name",
                "label": "Full Name",
                "value": f"{name} {surname}",
                "textColor":text_color.upper()
            },
             
        ]
    }
}

    def download_image(url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Şəkil yüklənə bilmədi ({url}): {e}")
            return b'\x89PNG\r\n\x1a\n...DUMMY_IMAGE...'

    logo_data = download_image(logo_url) if logo_url else b'\x89PNG\r\n\x1a\n...LOGO_DUMMY...'
    icon_data = download_image(icon_url) if icon_url else b'\x89PNG\r\n\x1a\n...ICON_DUMMY...'

    return pass_json, logo_data, icon_data

# ---- Manifest yaradıcı ----
def generate_manifest(assets: dict, pass_json: dict) -> dict:
    manifest = {}
    pass_json_bytes = json.dumps(pass_json, indent=4).encode("utf-8")
    manifest["pass.json"] = hashlib.sha1(pass_json_bytes).hexdigest()
    for filename, data in assets.items():
        manifest[filename] = hashlib.sha1(data).hexdigest()
    return manifest

# ---- Manifest imzalayıcı ----
def sign_manifest(manifest: dict, work_dir: Path) -> bytes:
    manifest_path = work_dir / "manifest.json"
    signature_path = work_dir / "signature"

    certificate_path = Path("D:/BYQR/Byqr-back-main/loyalty_latest/LoyaltyCard/certificate.pem")
    key_path = Path("D:/BYQR/Byqr-back-main/loyalty_latest/LoyaltyCard/key.pem")
    wwdr_path = Path("D:/BYQR/Byqr-back-main/loyalty_latest/LoyaltyCard/wwdr.pem")

    with open(manifest_path, "wb") as f:
        f.write(json.dumps(manifest, indent=4).encode("utf-8"))

    try:
        subprocess.check_call([
            "openssl", "smime", "-binary", "-sign",
            "-certfile", str(wwdr_path),
            "-signer", str(certificate_path),
            "-inkey", str(key_path),
            "-in", str(manifest_path),
            "-out", str(signature_path),
            "-outform", "DER",
        ], cwd=work_dir)
    except subprocess.CalledProcessError as e:
        raise Exception(f"OpenSSL sign error: {e}")

    with open(signature_path, "rb") as f:
        return f.read()

# ---- PKPASS yaradıcı ----
def create_pkpass(pass_json, assets, manifest, signature) -> BytesIO:
    buffer = BytesIO()
    with ZipFile(buffer, "w") as zip_file:
        zip_file.writestr("pass.json", json.dumps(pass_json, indent=4))
        for filename, data in assets.items():
            zip_file.writestr(f'{filename}', data)
        zip_file.writestr("manifest.json", json.dumps(manifest, indent=4))
        zip_file.writestr("signature", signature)
    buffer.seek(0)
    return buffer

# ---- Faylı saxlamaq ----
def save_pkpass(buffer: BytesIO, hash_str: str, output_dir: Path):
    file_path = output_dir / f"{hash_str}.pkpass"
    with open(file_path, "wb") as f:
        f.write(buffer.getvalue())
    return file_path


