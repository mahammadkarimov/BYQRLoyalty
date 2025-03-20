from calendar import monthrange

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import RestaurantDiscounts, Payment, Currency, UserFAQ
from base_user.models import Waiter
from restaurants.models import WaiterFeedback, Table
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from datetime import datetime
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
import uuid
from .functions import (
    get_data_and_signature,
    create_payment,
    get_signature,
    get_json,
    get_status_data_and_signature,
    check_status,
    get_card_reg_data_and_signature,
    card_register,
    get_pay_card_data_and_signature,
    get_apple_session_data_signature,
    get_apple_pay_data_signature,
    create_payment_with_card,
    create_payment_and_save_card,
    create_token_payment,
    get_pay_and_save_data_and_signature,
    get_refund_data_and_signature,
    create_refund,
    apple_pay_session,
    create_apple_payment,
    generate_epoint_token
)
from meals.serializers import RestaurantPackageSerializer
from .serializers import (
    RestaurantPostDiscountSerializer,
    RestaurantGetDiscountSerializer,
    PaymentCreateSerialzier,
    CurrencySerialzier,
    PaymentSuccessResponseSerializer,
    CallBackSeriazlier,
    PaymentStatusSerializer,
    PaymentStatusResponseSerialzier,
    CardRegisterSerialzier,
    CardRegisterResponseSerialzier,
    PayWithSavedCardSerialzier,
    PaymentWithSavedCardResponseSerialzier,
    PayAndSaveCardSerialzier,
    PayAndSaveCardResponseSerializer,
    CreateRefundSerialzier,
    PaymentListSerialzier,
    ApplePaySerialzier,
    UserFAQSerialzier, CorporativeWebsiteContactSerializer, EPointTokenSerializer
)

import logging


class DiscountView(ModelViewSet):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"
    queryset = RestaurantDiscounts.objects.all()
    serializer_class = RestaurantPostDiscountSerializer
    pagination_class = PageNumberPagination

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        date = datetime.strptime(request.data["expiration_date"], "%d.%m.%Y")
        request.data["expiration_date"] = date
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(created_from=request.user))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RestaurantGetDiscountSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = RestaurantGetDiscountSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        print(partial)
        instance = self.get_object()
        request.data._mutable = True
        try:
            date = datetime.strptime(request.data["expiration_date"], "%d.%m.%Y")
            request.data["expiration_date"] = date
            request.data._mutable = False
        except:
            pass

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = RestaurantGetDiscountSerializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrencyListView(ListAPIView):
    serializer_class = CurrencySerialzier
    permission_classes = [AllowAny]
    queryset = Currency.objects.all()


class PaymentCreateView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=PaymentCreateSerialzier,
        responses={
            201: openapi.Response(
                description="Payment created successfully",
                schema=PaymentSuccessResponseSerializer
            ),
            400: "Bad Request"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = PaymentCreateSerialzier(data=request.data)
        if serializer.is_valid():
            currency_id = serializer.validated_data.get('currency')
            language = serializer.validated_data.get('language')
            amount = serializer.validated_data.get('amount')
            description = serializer.validated_data.get('description', '')
            table_id = serializer.validated_data.get('table_id')
            rate = serializer.validated_data.get('rate', None)
            net = amount * Decimal('0.95')

            table = get_object_or_404(Table, table_id=table_id)
            currency = get_object_or_404(Currency, id=currency_id)

            if rate:
                WaiterFeedback.objects.create(waiter=table.current_waiter, rate=rate, description=description,
                                              table=table)

            payment = Payment.objects.create(amount=amount, net=net, currency=currency, description=description,
                                             waiter=table.current_waiter)
            data, signature = get_data_and_signature(amount, currency.name, description, language, payment.order_id)

            try:
                response = create_payment(data, signature)
            except:
                return Response({"message": "Falied get reponse from epoint!"}, status=status.HTTP_400_BAD_REQUEST)

            if response.json()['status'] == "success":
                payment.transaction_id = response.json()['transaction']
                payment.save()
                return Response(response.json(), status=status.HTTP_201_CREATED)
            else:
                return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentCallBackView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=CallBackSeriazlier,
        responses={
            201: openapi.Response(
                description="Payment status is successfull",
                schema=CallBackSeriazlier
            ),
            400: "Bad Request"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = CallBackSeriazlier(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data.get('data')
            esignature = serializer.validated_data.get('signature')
            try:
                signature = get_signature(data)
            except:
                return Response({"message": "Falied get reponse from epoint!"}, status=status.HTTP_400_BAD_REQUEST)
            if esignature == signature:
                data_json = get_json(data)
                if data_json['status'] == 'success':
                    if data_json.get('order_id', None) != None:
                        order_id = data_json['order_id']
                        payment = Payment.objects.get(order_id=order_id)
                        waiter = payment.waiter
                        payment.is_successful = True
                        payment.card_name = data_json['card_name']
                        payment.card_mask = data_json['card_mask']
                        payment.save()

                        # Aggregate the total for 'IN' payments
                        balance = \
                            Payment.objects.filter(is_successful=True, is_completed=False, waiter=waiter).aggregate(
                                total=Sum('net'))['total'] or 0
                        # Aggregate the total for 'OUT' payments
                        # total_out = Payment.objects.filter(is_successful=True, is_completed=True, waiter=waiter).aggregate(total=Sum('net'))['total'] or 0
                        # Calculate the balance

                        waiter.balance = balance
                        waiter.save()
                    else:
                        card_id = data_json['card_id']
                        waiter = get_object_or_404(Waiter, card_id=card_id)
                        waiter.is_card_saved = True
                        waiter.card_id = waiter.card_id_update
                        waiter.card_name = data_json['card_name']
                        waiter.card_mask = data_json['card_mask']
                        waiter.save()
                return Response({"message": "Signature is safe!"}, status=status.HTTP_201_CREATED)
            return Response({"message": "Signature is not safe!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentStatusView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=PaymentStatusSerializer,
        responses={
            201: openapi.Response(
                description="Payment status is successfull",
                schema=PaymentStatusResponseSerialzier
            ),
            400: "Bad Request"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = PaymentStatusSerializer(data=request.data)
        if serializer.is_valid():
            transaction = serializer.validated_data.get('transaction')
            data, signature = get_status_data_and_signature(transaction)
            try:
                response = check_status(data, signature)
            except:
                return Response({"message": "Falied get reponse from epoint!"}, status=status.HTTP_400_BAD_REQUEST)
            if response.json()['status'] != "failed":
                return Response(response.json(), status=status.HTTP_200_OK)
            return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CardRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=CardRegisterSerialzier,
        responses={
            201: openapi.Response(
                description="Payment status is successfull",
                schema=CardRegisterResponseSerialzier
            ),
            400: "Bad Request"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = CardRegisterSerialzier(data=request.data)
        if serializer.is_valid():
            waiter = self.request.user.waiter
            language = serializer.validated_data.get('language')
            description = serializer.validated_data.get('description', '')
            success_redirect_url = serializer.validated_data.get('succes_redirect_url',
                                                                 'https://menu.byqr.az/az/tips-success')
            error_redirect_url = serializer.validated_data.get('error_redirect_url',
                                                               'https://menu.byqr.az/az/tips-error')
            data, signature = get_card_reg_data_and_signature(language, 1, description, success_redirect_url,
                                                              error_redirect_url)
            try:
                response = card_register(data, signature)
                print("Response", response.json())
            except:
                return Response({"message": "Falied get reponse from epoint!"}, status=status.HTTP_400_BAD_REQUEST)
            if response.json()['status'] == "success":
                waiter.card_id_update = response.json()['card_id']
                print(response.json())
                waiter.save()

                return Response(response.json(), status=status.HTTP_201_CREATED)
            return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PayWithSavedCardView(APIView):
    permission_classes = {AllowAny}

    @swagger_auto_schema(
        request_body=PayWithSavedCardSerialzier,
        responses={
            201: openapi.Response(
                description="Payment status is successfull",
                schema=PaymentWithSavedCardResponseSerialzier
            ),
            400: "Bad Request"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = PayWithSavedCardSerialzier(data=request.data)
        if serializer.is_valid():
            currency_id = serializer.validated_data.get('currency')
            card_id = serializer.validated_data.get('card_id')
            language = serializer.validated_data.get('language')
            amount = serializer.validated_data.get('amount')
            description = serializer.validated_data.get('description')
            waiter_id = serializer.validated_data.get('waiter_id')
            rate = serializer.validated_data.get('rate')

            waiter = get_object_or_404(Waiter, waiter_id=waiter_id)
            currency = get_object_or_404(Currency, id=currency_id)

            WaiterFeedback.objects.create(waiter=waiter, rate=rate)
            payment = Payment.objects.create(amount=amount, currency=currency, description=description, waiter=waiter)
            data, signature = get_pay_card_data_and_signature(amount, currency.name, description, language,
                                                              payment.order_id, card_id)

            try:
                response = create_payment_with_card(data, signature)
            except:
                return Response({"message": "Falied get reponse from epoint!"}, status=status.HTTP_400_BAD_REQUEST)

            if response.json()['status'] == "success":
                payment.transaction_id = response.json()['transaction']
                payment.save()
                return Response(response.json(), status=status.HTTP_201_CREATED)
            return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PayAndSaveCardView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=PayAndSaveCardSerialzier,
        responses={
            201: openapi.Response(
                description="Payment status is successfull",
                schema=PayAndSaveCardResponseSerializer
            ),
            400: "Bad Request"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = PayAndSaveCardSerialzier(data=request.data)
        if serializer.is_valid():
            currency_id = serializer.validated_data.get('currency')
            language = serializer.validated_data.get('language')
            amount = serializer.validated_data.get('amount')
            description = serializer.validated_data.get('description')
            waiter_id = serializer.validated_data.get('waiter_id')
            rate = serializer.validated_data.get('rate')
            success_redirect_url = serializer.validated_data.get('succes_redirect_url')
            error_redirect_url = serializer.validated_data.get('error_redirect_url')

            waiter = get_object_or_404(Waiter, waiter_id=waiter_id)
            currency = get_object_or_404(Currency, id=currency_id)

            WaiterFeedback.objects.create(waiter=waiter, rate=rate)
            payment = Payment.objects.create(amount=amount, currency=currency, description=description, waiter=waiter)
            data, signature = get_pay_and_save_data_and_signature(amount, currency.name, description, language,
                                                                  payment.order_id, success_redirect_url,
                                                                  error_redirect_url, type=type)

            try:
                response = create_payment_and_save_card(data, signature)
                print("RESPONSE FROM SAVING", response.json())
            except:
                return Response({"message": "Falied get reponse from epoint!"}, status=status.HTTP_400_BAD_REQUEST)

            if response.json()['status'] == "success":
                payment.transaction_id = response.json()['transaction']
                payment.save()
                return Response(response.json(), status=status.HTTP_201_CREATED)
            return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


logger = logging.getLogger('byqr')


class CreateRefundView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            201: openapi.Response(
                description="Payment status is successfull",
                schema=PaymentWithSavedCardResponseSerialzier
            ),
            400: "Bad Request"
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            one_week_ago = timezone.now() - timedelta(weeks=1)
            refunds = Payment.objects.filter(is_successful=True, is_completed=False, created_at__lte=one_week_ago)
            if refunds.count() == 0:
                return Response({"message": "No payments to refund!"}, status=status.HTTP_400_BAD_REQUEST)
            error_number = 0
            success_number = 0
            logger.info("Refunds", refunds)
            for refund in refunds:
                language = 'az'
                amount = refund.net
                description = refund.description
                card_id = refund.waiter.card_id
                print("ofisiantin card idsdi", card_id)
                currency = refund.currency
                refund_id = str(uuid.uuid4()).upper()

                data, signature = get_refund_data_and_signature(amount, currency.name, description, language, refund_id,
                                                                card_id)

                try:
                    print('test data and signature')
                    print("RESPONSE READ")
                    response = create_refund(data, signature)
                    logger.info("RESPONSE", response)

                except:
                    continue
                print(amount, currency.name)
                print(response.json())
                if response.json()['status'] == "success":
                    logger.info(response.json()['card_mask'])
                    refund.refund_transaction_id = response.json()['transaction']
                    refund.waiter_card_name = response.json()['card_name']
                    refund.waiter_card_mask = response.json()['card_mask']

                    refund.refund_id = refund_id
                    refund.is_completed = True
                    refund.save()
                    waiter = refund.waiter
                    # Aggregate the total for 'IN' payments
                    balance = Payment.objects.filter(is_successful=True, is_completed=False, waiter=waiter).aggregate(
                        total=Sum('net'))['total'] or 0

                    waiter.balance = balance
                    waiter.save()
                    success_number += 1
                else:
                    error_number += 1
            return Response({
                "message": f"{success_number} payments completed successfully and {error_number} payments are failed!"},
                status=status.HTTP_201_CREATED)
        except:
            return Response({"message": "Something went wrong!"}, status=status.HTTP_400_BAD_REQUEST)


class WaiterPaymentListView(ListAPIView):
    serializer_class = PaymentListSerialzier
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        time = self.request.GET.get('time')
        waiter = self.request.user.waiter
        today = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        queryset = waiter.tips.all()

        if time == 'today':
            queryset = Payment.objects.filter(
                waiter=waiter,
                created_at__date=today.date()
            )
        elif time == 'week':
            week_start = today - timezone.timedelta(days=today.weekday())
            week_end = week_start + timezone.timedelta(days=6, hours=23, minutes=59, seconds=59)
            queryset = Payment.objects.filter(
                waiter=waiter,
                created_at__range=[week_start, week_end]
            )
        elif time == 'month':
            month_start = today.replace(day=1)
            last_day = monthrange(today.year, today.month)[1]
            month_end = today.replace(day=last_day, hour=23, minute=59, second=59)
            queryset = Payment.objects.filter(
                waiter=waiter,
                created_at__range=[month_start, month_end]
            )

        return queryset


class TokenPaymentCreateView(APIView):

    @swagger_auto_schema(
        request_body=PaymentCreateSerialzier,
        responses={
            201: openapi.Response(
                description="Payment created successfully",
                schema=PaymentSuccessResponseSerializer
            ),
            400: "Bad Request"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = PaymentCreateSerialzier(data=request.data)
        if serializer.is_valid():
            currency_id = serializer.validated_data.get('currency')
            language = serializer.validated_data.get('language')
            amount = serializer.validated_data.get('amount')
            description = serializer.validated_data.get('description', '')
            table_id = serializer.validated_data.get('table_id')
            rate = serializer.validated_data.get('rate', None)

            table = get_object_or_404(Table, table_id=table_id)
            currency = get_object_or_404(Currency, id=currency_id)

            if rate:
                WaiterFeedback.objects.create(waiter=table.current_waiter, rate=rate, description=description,
                                              table=table)

            payment = Payment.objects.create(amount=amount, currency=currency, description=description,
                                             waiter=table.current_waiter)
            data, signature = get_data_and_signature(amount, currency.name, description, language, payment.order_id)
            try:
                response = create_token_payment(data, signature)
            except:
                return Response({"message": "Falied get reponse from epoint!"}, status=status.HTTP_400_BAD_REQUEST)

            if response.json()['status'] == "success":
                # payment.transaction_id = response.json()['transaction']
                # payment.save()
                # waiter = table.current_waiter
                # waiter.balance += amount
                # waiter.save()
                return Response(response.json(), status=status.HTTP_201_CREATED)
            else:
                return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplePaySessionView(APIView):

    def post(self, request, *args, **kwargs):
        data, signature = get_apple_session_data_signature()
        try:
            response = apple_pay_session(data, signature)
        except:
            return Response({"message": "Falied get reponse from epoint!"}, status=status.HTTP_400_BAD_REQUEST)
        if response.json()['status'] == "success":
            return Response(response.json(), status=status.HTTP_201_CREATED)
        else:
            return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)


class ApplePayView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=ApplePaySerialzier,
        responses={
            201: openapi.Response(
                description="Payment created successfully",
                schema=PaymentStatusResponseSerialzier
            ),
            400: "Bad Request"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = ApplePaySerialzier(data=request.data)
        if serializer.is_valid():
            id = serializer.validated_data.get('id')
            token = serializer._validated_data.get('token')
            billing_contact = serializer.validated_data.get('billing_contact')

            data, signature = get_apple_pay_data_signature(id, token, billing_contact)

            try:
                response = create_apple_payment(data, signature)
            except:
                return Response({"message": "Falied get reponse from epoint!"}, status=status.HTTP_400_BAD_REQUEST)
            if response.json()['status'] == "success":
                return Response(response.json(), status=status.HTTP_201_CREATED)
            else:
                return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserFAQLisView(ListAPIView):
    serializer_class = UserFAQSerialzier
    permission_classes = [AllowAny]
    queryset = UserFAQ.objects.all()


class ContactFormView(APIView):
    def post(self, request):
        serializer = CorporativeWebsiteContactSerializer(data=request.data)
        if serializer.is_valid():
            full_name = serializer.validated_data['full_name']
            phone_number = serializer.validated_data['phone_number']
            category = serializer.validated_data['category']

            # Email məzmunu
            email_subject = f"Yeni müraciət: {category}"
            email_body = f"""
            Yeni müraciət daxil olub:

            Ad Soyad: {full_name}
            Telefon: {phone_number}
            Kateqoriya: {category}
            """

            send_mail(
                subject=email_subject,
                message=email_body,
                from_email="quluzadintiqam@gmail.com",
                recipient_list=["byqraz@gmail.com", "contact@byqrapp.com", "ibrahimseyidov72@gmail.com"],
                fail_silently=False,
            )

            return Response({"message": "Müraciətiniz uğurla göndərildi!"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerateEPointTokenView(APIView):
    def post(self, request, format=None):
        serializer = EPointTokenSerializer(data=request.data)

        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            description = serializer.validated_data['description']
            waiter = serializer.validated_data['waiter']
            table_id = serializer.validated_data.get('table_id')
            rate = serializer.validated_data.get('rate', None)
            net = Decimal(str(amount)) * Decimal('0.95')
            currency_id = serializer.validated_data.get('currency')

            currency = get_object_or_404(Currency, id=currency_id)
            waiter_obj = get_object_or_404(Waiter, waiter_id=waiter)
            table = get_object_or_404(Table, table_id=table_id)

            if rate:
                WaiterFeedback.objects.create(waiter=waiter_obj, rate=rate, description=description,
                                              table=table)

            public_key = settings.PUBLIC_KEY
            private_key = settings.PRIVATE_KEY
            order_id = str(uuid.uuid4()).upper()

            token_response = generate_epoint_token(
                public_key, amount, order_id, description, private_key
            )

            payment = Payment.objects.create(
                order_id=order_id,
                amount=amount,
                description=description,
                waiter=waiter_obj,
                currency=currency,
                net=net,
            )
            payment.save()

            return Response(token_response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
