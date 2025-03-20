from django.forms import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from base_user.models import User
from django.http import FileResponse
from django.core.files.base import ContentFile
from loyalty_latest.LoyaltyCard.signer import generate_loyalty_card_and_pass
from loyalty_latest.models import UserCard, Layout, Passes
import hashlib
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from .serializers import UserCardSerializer , LayoutSerializer
import random
import requests

class CreateLayoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def download_image(self, image_url):
        try:
            # Download image from the URL
            response = requests.get(image_url)
            response.raise_for_status()  # Ensure we got a valid response

            # Create a file-like object from the downloaded content
            image_name = image_url.split("/")[-1]  
            return ContentFile(response.content, name=image_name)
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Failed to download image: {e}")

    def post(self, request, *args, **kwargs):
        try:
            # Extract data from the request
            layout_banner_url = request.data.get('layout_banner')  # URL of the banner image
            layout_logo_url = request.data.get('layout_logo')  # URL of the logo image
            layout_type = request.data.get('layout_type')
            layout_name = request.data.get('layout_name')
            layout_background_color = request.data.get('layout_background_color')
            text_color = request.data.get('text_color')

            # Validate the necessary fields
            if not all([layout_banner_url, layout_logo_url, layout_type, layout_background_color, text_color]):
                raise ValidationError("All fields are required: layout_banner, layout_logo, layout_type, layout_background_color, text_color")

            # Download images from the URLs
            layout_banner = self.download_image(layout_banner_url)
            layout_logo = self.download_image(layout_logo_url)

            # Prepare data for serializer
            data = {
                'layout_banner': layout_banner,
                'layout_logo': layout_logo,
                'layout_type': layout_type,
                'layout_name': layout_name,
                'layout_background_color': layout_background_color,
                'text_color': text_color,
                'user': request.user.id,  # Include the user
            }

            # Serialize the data
            serializer = LayoutSerializer(data=data)
            if serializer.is_valid():
                layout = serializer.save()  # Save the layout instance

                # Return the successful response with relevant data
                return Response({
                    'layout_id': layout.id,
                    'layout_banner': layout.layout_banner.url if layout.layout_banner else None,
                    'layout_logo': layout.layout_logo.url if layout.layout_logo else None,
                    'layout_type': layout.layout_type,
                    'layout_background_color': layout.layout_background_color,
                    'text_color': layout.text_color,
                    'layout_name': layout.layout_name
                }, status=status.HTTP_201_CREATED)

            # If serializer is not valid
            return Response({
                'error': 'Invalid data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class LoyaltyLayoutGetView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        queryset = Layout.objects.all()
        serializer = LayoutSerializer(queryset, many=True)
        return Response(serializer.data)


class LoyaltyLayoutDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        # Assuming you're passing the `id` of the layout to delete in the URL
        layout_id = kwargs.get('pk')  # or 'id' if using a different name in the URL pattern
        
        try:
            layout = Layout.objects.get(id=layout_id)
        except Layout.DoesNotExist:
            return Response({"detail": "Layout not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Delete the layout object
        layout.delete()
        
        return Response({"detail": "Layout deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class LoyaltyLayoutUpdateView(APIView):
    def put(self, request, pk, *args, **kwargs):
        return self.update_layout(request, pk, full_update=True)

    def patch(self, request, pk, *args, **kwargs):
        return self.update_layout(request, pk, full_update=False)

    def update_layout(self, request, pk, full_update=False):
        layout = get_object_or_404(Layout, pk=pk)

        layout_logo_url = request.data.get('layout_logo', None)
        layout_banner_url = request.data.get('layout_banner', None)

        # Köhnə şəkil adlarını saxla müqayisə üçün
        old_logo_name = layout.layout_logo.name if layout.layout_logo else None
        old_banner_name = layout.layout_banner.name if layout.layout_banner else None

        # Əgər yeni URL varsa və dəyişibsə, yeni şəkli yüklə
        if layout_logo_url and not old_logo_name.endswith(layout_logo_url.split('/')[-1]):
            layout.layout_logo = self.download_image(layout_logo_url)

        if layout_banner_url and not old_banner_name.endswith(layout_banner_url.split('/')[-1]):
            layout.layout_banner = self.download_image(layout_banner_url)

        # Form məlumatını kopyala və şəkil sahələrini çıxart
        mutable_data = request.data.copy()
        mutable_data.pop('layout_logo', None)
        mutable_data.pop('layout_banner', None)

        serializer = LayoutSerializer(layout, data=mutable_data, partial=not full_update)
        if serializer.is_valid():
            serializer.save()
            return Response(LayoutSerializer(layout).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def download_image(self, image_url):
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image_name = image_url.split("/")[-1]
            return ContentFile(response.content, name=image_name)
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Failed to download image: {e}")

class CreateLoyaltyCard(APIView):

    permission_classes = [IsAuthenticated]    
    def post(self, request, *args, **kwargs):
        data = request.data
        
        # Generate a random user_id and card_number
        data['card_user_id'] = random.randint(1000000000, 1000000000000)
        data['card_number'] = random.randint(100000000000000000, 999999999999999999)
        
        # Create a download hash using hashlib
        data['download_hash'] = hashlib.sha256(f"{data['card_number']}{data['card_user_id']}".encode('utf-8')).hexdigest()
        
        # Automatically set the user field from the authenticated user
        data['user'] = request.user.id
        
        # Serialize the data
        serializer = UserCardSerializer(data=data)
        
        if serializer.is_valid():
            user_card = serializer.save()
            
            # Retrieve layout or return an error
            try:
                layout = Layout.objects.get(id=data['layout']) if data.get('layout') else None
                if not layout:
                    return Response({"detail": "Layout is a mandatory field!"}, status=status.HTTP_400_BAD_REQUEST)
            except Layout.DoesNotExist:
                return Response({"detail": "Layout does not exist!"}, status=status.HTTP_404_NOT_FOUND)

            # Generate the loyalty card
            
            loyalty_card = generate_loyalty_card_and_pass(data['name'], data['surname'], data['loyalty_level'], data['card_number'],data['download_hash'], layout.layout_logo.url, layout.layout_banner.url,layout.layout_background_color,layout.text_color,data["device"],user_card.id)
            
            return Response({
                'message': 'Loyalty card created successfully',
                'download_link': f'https://byqr.az/passes/download/{data['download_hash']}'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class DownloadPassView(APIView):
    def get(self, request, download_hash, *args, **kwargs):
        try:
            user_card = UserCard.objects.get(download_hash=download_hash)
            pass_instance = Passes.objects.get(user_card=user_card)
        except Passes.DoesNotExist:
            raise Response({"detail":"Error 404"},status=status.HTTP_404_NOT_FOUND)

        # Open file from Azure storage
        pkpass_file = pass_instance.pass_file.open('rb')

        response = FileResponse(pkpass_file, content_type='application/vnd.apple.pkpass')
        response['Content-Disposition'] = f'attachment; filename="{pass_instance.device_type}.pkpass"'
        return response

class LoyaltyCardsGetView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        queryset = UserCard.objects.all().filter(user=request.user)
        serializer = UserCardSerializer(queryset, many=True)
        return Response(serializer.data)
    

class UpdateLoyaltyCard(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, card_id, *args, **kwargs):
        try:
            # Retrieve the user card by its ID and ensure it's the logged-in user's card
            user_card = UserCard.objects.get(id=card_id, user=request.user)
        except UserCard.DoesNotExist:
            return Response({"detail": "User card not found or you do not have permission."}, status=status.HTTP_404_NOT_FOUND)

        # Create a serializer with partial=True to update specific fields
        serializer = UserCardSerializer(user_card, data=request.data, partial=True)

        if serializer.is_valid():
            updated_user_card = serializer.save()

            # Retrieve layout related to this user card
            layout = updated_user_card.layout

            try:
                # Generate updated loyalty card if layout exists
                loyalty_card = generate_loyalty_card_and_pass(
                    updated_user_card.name,  # Update the name if provided
                    updated_user_card.surname,  # Update the surname if provided
                    updated_user_card.loyalty_level,  # Update loyalty level if provided
                    updated_user_card.card_number,
                    updated_user_card.download_hash,
                    layout.layout_logo.url,
                    layout.layout_banner.url,
                    layout.layout_background_color,  # Add other layout-related data
                    layout.text_color,
                    updated_user_card.device,  # Device information
                    updated_user_card.id  # Pass the user card ID for reference
                )
                
                # Assuming generate_loyalty_card_and_pass returns the generated card or a related file object
                return Response({
                    "message": "Loyalty card updated successfully.",
                    "download_link": f"https://byqr.az/passes/download/{updated_user_card.download_hash}"
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"detail": f"Error generating card: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return validation errors if serializer is not valid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class DeleteLoyaltyCard(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        # Get the user card ID from the URL parameters
        card_id = kwargs.get('card_id')
        
        if not card_id:
            return Response({"detail": "Card ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to find the user card by its ID
        try:
            user_card = UserCard.objects.get(id=card_id, user=request.user)
            pass_card = Passes.objects.get(user_card=user_card)
        except UserCard.DoesNotExist:
            return Response({"detail": "Loyalty card not found."}, status=status.HTTP_404_NOT_FOUND)

        # Delete the user card
        user_card.delete() 
        pass_card.delete()

        return Response({"message": "Loyalty card deleted successfully."}, status=status.HTTP_204_NO_CONTENT)