import requests
from django.http import JsonResponse
from .api_client import make_request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_view(request, organization_id, terminal_group_id, table_id, product_id):
    """
    Django view to create an order with given organization, terminal group, table, and product size.
    """
    payload = {
        "organizationId": organization_id,
        "terminalGroupId": terminal_group_id,
        "order": {
            "tableIds": [table_id],
            "items": [
                {
                    "amount": 1,
                    "productId": product_id,
                    "type": "Product"
                }
            ]
        }
    }

    try:
        response_data = make_request("order/create", "POST", payload)
        return JsonResponse(response_data, safe=False)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Failed to create order", "details": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_menu_view(request, organization_id, start_revision=0):
    """
    Django view to fetch the menu from the API for a specific organization.
    """
    payload = {
        "organizationId": organization_id,
        "startRevision": start_revision
    }

    try:
        response_data = make_request("nomenclature", "POST", payload)
        return JsonResponse(response_data, safe=False)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Failed to fetch menu", "details": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_available_tables(request, terminal_group_id):
    """
    Django view to fetch available restaurant sections (tables) for a specific terminal group.
    """
    payload = {
        "terminalGroupIds": [terminal_group_id],
        "returnSchema": True,
        "revision": 0
    }

    try:
        response_data = make_request("reserve/available_restaurant_sections", "POST", payload)
        return JsonResponse(response_data, safe=False)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Failed to fetch available tables", "details": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_orders_by_table(request, organization_id, table_id):
    """
    Django view to fetch orders for a specific table in a specific organization.
    """
    payload = {
        "organizationIds": [organization_id],
        "tableIds": [table_id]
    }

    try:
        response_data = make_request("order/by_table", "POST", payload)
        return JsonResponse(response_data, safe=False)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Failed to fetch orders by table", "details": str(e)}, status=500)