from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import requests
from base_user.models import Restaurant
from django.shortcuts import get_object_or_404
from iiko.api_client import make_request

"""
1. organizationId -> done
2. tableId -> done
3. terminalGroupId -> done
4. items:
    4.1. amount
    4.2. productId
    4.3. type = "product"
    4.4. customer = authenticated user
"""


"""
When creating order:
1. Getting organization id = with first_name of restaurant_user and catch organization_id
2. Getting table_id = from the url
3. terminalGroupId = restaurant's feature
4. 
"""


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print("salam")
        name = request.data.get("name")
        print(name)
        restaurant = get_object_or_404(Restaurant, user__first_name=name)
        print(restaurant)

        organization_id = restaurant.organization_id
        table_id = request.data.get("tableId")
        terminal_group_id = restaurant.terminal_group_id
        items = request.data.get("items")
        print(items)

        if not all([organization_id, table_id, terminal_group_id, items]):
            return Response({"error": "Missing required fields"}, status=400)

        user = request.user
        customer_id = getattr(user.client, "iiko_id", None)

        if not customer_id:
            return Response({"error": "Customer ID not found for authenticated user"}, status=400)

        external_payload = {
            "organizationId": organization_id,
            "terminalGroupId": terminal_group_id,
            "order": {
                "tableIds": [table_id],
                "items": [
                    {
                        "amount": item["amount"],
                        "productId": item["productId"],
                        "type": "Product",
                        "customer": customer_id,
                    }
                    for item in items
                ],
            },
        }

        # Make request to external API
        try:
            response_data = make_request(
                endpoint="order/create",
                method="POST",
                payload=external_payload,
            )
        except Exception as e:
            return Response({"error": f"Failed to create order: {str(e)}"}, status=500)

        return Response(response_data, status=200)


"""
User datalari doldurur ve save olur bizim dbya
O datalari get olarag verirem
Userin datalarina ve restorana uygun cardlar yaranir.

"""

