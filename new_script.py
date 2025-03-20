import os
import shutil

def delete_pycache_in_dir(root_dir):
    # Root qovluğunun içindəki bütün fayl və qovluqları gəz
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Hər bir qovluqda '__pycache__' varsa, onu sil
        if '__pycache__' in dirnames or 'migrations' in dirnames:
            pycache_dir = os.path.join(dirpath, '__pycache__')
            migration_dir = os.path.join(dirpath, 'migrations')
            print(f"Silinir: {pycache_dir}")
            shutil.rmtree(pycache_dir)  # __pycache__ qovluğunu sil
            shutil.rmtree(migration_dir)

# İstədiyiniz qovluğu daxil edin
root_directory = r"D:\BYQR\Byqr-back-main"  # Burada qovluğun yolunu göstər
delete_pycache_in_dir(root_directory)
