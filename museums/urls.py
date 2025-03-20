from django.urls import path
from .views import ExhibitListView, ExhibitDetailView, ExhibitDetailQr, DownloadExhibitQRCodesView

urlpatterns = [
    path('exhibits/', ExhibitListView.as_view(), name='exhibit-list'),

    # path('exhibits/', ExhibitListView.as_view(), name='exhibit-list'), # <str:lang>/

    path('exhibits/<int:museum_id>/<int:exhibit_id>/', ExhibitDetailView.as_view(), name='exhibit-detail'),
    path('exhibits/<str:museum_username>/<int:exhibit_id>/', ExhibitDetailQr.as_view(), name='exhibit-detail-qr'),

    path('exhibits/<int:museum_id>/<int:exhibit_id>/', ExhibitDetailView.as_view(),
         name='exhibit-detail-lang'), # <str:lang>/

    path('download-exhibit-qrcodes/', DownloadExhibitQRCodesView.as_view(), name='download_exhibit_qrcodes'),

]
