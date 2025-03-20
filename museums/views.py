from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from base_user.models import Museum
from .models import Exhibit
from .serializers import ExhibitSerializer
from django.utils.translation import activate
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
import zipfile
from io import BytesIO
import requests
from django.db.models import Q


class ExhibitListView(APIView):
    permission_classes = [permissions.IsAuthenticated]


    def get(self, request):  # lang=None
        """
        List all exhibits based on the logged-in user.
        """
        user = request.user
        try:
            museum = Museum.objects.get(user=user)
        except Museum.DoesNotExist:
            return Response(
                {"detail": "User is not associated with any museum."},
                status=status.HTTP_404_NOT_FOUND
            )

        name = request.query_params.get('name', None)

        # Filter exhibits by name if a name is provided, otherwise return all
        if name:
            exhibits = Exhibit.objects.filter(
                museum=museum
            ).filter(
                Q(name_az__icontains=name) |
                Q(name_en__icontains=name) |
                Q(name_ru__icontains=name) |
                Q(name_ar__icontains=name) |
                Q(name_ko__icontains=name)
            )
        else:
            exhibits = Exhibit.objects.filter(museum=museum)

        serializer = ExhibitSerializer(exhibits, many=True)  # , context={'lang': lang}
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new exhibit with multiple images.
        """
        exhibit_serializer = ExhibitSerializer(data=request.data, context={'request': request})
        if exhibit_serializer.is_valid():
            exhibit = exhibit_serializer.save()
            return Response(exhibit_serializer.data, status=status.HTTP_201_CREATED)
        return Response(exhibit_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExhibitDetailView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, museum_id=None, exhibit_id=None):  # lang=None,
        """
        Retrieve a single exhibit based on the specified language and IDs.
        """
        # if lang:
        #     activate(lang)

        try:
            exhibit = Exhibit.objects.get(museum_id=museum_id, id=exhibit_id)
        except Exhibit.DoesNotExist:
            return Response({"error": "Exhibit not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExhibitSerializer(exhibit)  # , context={'lang': lang}
        return Response(serializer.data)

    def patch(self, request, museum_id, exhibit_id):
        """
        Partially update a specific exhibit.
        """
        try:
            exhibit = Exhibit.objects.get(id=exhibit_id, museum_id=museum_id)
        except Exhibit.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExhibitSerializer(exhibit, data=request.data, partial=True)  # Note: partial=True for PATCH
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, museum_id, exhibit_id):  # , lang=None
        """
        Delete a specific exhibit.
        """
        # if lang:
        #     activate(lang)

        try:
            exhibit = Exhibit.objects.get(id=exhibit_id, museum_id=museum_id)
        except Exhibit.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        exhibit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExhibitDetailQr(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, museum_username=None, exhibit_id=None):  # lang=None,
        """
        Retrieve a single exhibit based on the specified language and IDs.
        """
        # if lang:
        #     activate(lang)

        try:
            exhibit = Exhibit.objects.get(museum__user__username=museum_username, id=exhibit_id)
        except Exhibit.DoesNotExist:
            return Response({"error": "Exhibit not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExhibitSerializer(exhibit)  # , context={'lang': lang}
        return Response(serializer.data)


class DownloadExhibitQRCodesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        exhibits = Exhibit.objects.filter(museum__user=user)

        if not exhibits.exists():
            return HttpResponse("No exhibits found for this user.", status=404)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for exhibit in exhibits:
                if exhibit.qr_code:
                    file_url = exhibit.qr_code.url
                    file_name = f"{exhibit.name}_qr_code.png" if exhibit.name else "qr_code.png"
                    response = requests.get(file_url)
                    if response.status_code == 200:
                        zip_file.writestr(file_name, response.content)

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type="application/zip")
        response['Content-Disposition'] = 'attachment; filename="user_exhibit_qr_codes.zip"'
        return response


# WALLET meselesi restoranlar ucun.

"""
Coffeshoplar ucun endirim meselesi,
tripadvisor ve googleda comment atsa ona barcode generate olunur. 
"""

"""
Muzeyler, yazilan sozu seslendirmek 5 dilde.
"""

"""

"""
