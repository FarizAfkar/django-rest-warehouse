from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.db.models import Sum, F
from api_wh.utils import Render
from django.http import JsonResponse
from .models import Item, PurchaseHeader, PurchaseDetail, SellHeader, SellDetail
from .serializers import (
    ItemSerializer, PurchaseHeaderSerializer, PurchaseDetailSerializer,
    SellHeaderSerializer, SellDetailSerializer
)


# Create your views here.
class CustomTokenObtainPairView(APIView):
    """
    Token Authenctication Using Simple JWT
    request username & password
    authenticate user
    response token acccess & refresh
    """

    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class CustomTokenRefreshView(APIView):
    """
    Token Authenctication Using Simple JWT
    request token refresh
    response token acccess
    """

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            return Response({'access': str(access_token)})
        except Exception:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)


class ItemListCreateAPIView(APIView):
    """
    Items List View & Create View
    permission allow Get, permmsion protected Post, Patch, Put, Delete
    """

    def get_permissions(self):
        """Dynamically assign permissions based on request method."""
        if self.request.method == 'GET':
            return [AllowAny()]  # Public access
        return [IsAuthenticated()]  # Protected for POST, PUT, DELETE

    def get(self, request):
        items = Item.objects.filter(is_deleted=False).order_by('created_at')
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            serializer = ItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print('ERROR',e)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ItemRetrieveUpdateDeleteAPIView(APIView):
    """
    Items Update, Detail, Delete View
    permission protected
    Retrieve, update, or soft delete an item.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, code):
        try:
            return Item.objects.get(code=code, is_deleted=False)
        except Item.DoesNotExist:
            return None

    def get(self, request, code):
        item = self.get_object(code)
        if not item:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ItemSerializer(item)
        return Response(serializer.data)

    def put(self, request, code):
        item = self.get_object(code)
        if not item:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code):
        item = self.get_object(code)
        if not item:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        item.is_deleted = True
        item.save()
        return Response({'message': 'Item soft deleted'}, status=status.HTTP_204_NO_CONTENT)


class PurchaseListCreateAPIView(APIView):
    """
    Purchase List View & Create View
    permission permmsion protected
    Handles listing all purchases and creating a new purchase.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        purchases = PurchaseHeader.objects.filter(is_deleted=False)
        serializer = PurchaseHeaderSerializer(purchases, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PurchaseHeaderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseRetrieveUpdateDeleteAPIView(APIView):
    """
    Purchase Update, Detail, Delete View
    permission protected
    Retrieve, update, or soft delete a purchase.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, code):
        try:
            return PurchaseHeader.objects.get(code=code, is_deleted=False)
        except PurchaseHeader.DoesNotExist:
            return None

    def get(self, request, code):
        purchase = self.get_object(code)
        if not purchase:
            return Response({'error': 'Purchase not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PurchaseHeaderSerializer(purchase)
        return Response(serializer.data)

    def put(self, request, code):
        purchase = self.get_object(code)
        if not purchase:
            return Response({'error': 'Purchase not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PurchaseHeaderSerializer(purchase, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code):
        purchase = self.get_object(code)
        if not purchase:
            return Response({'error': 'Purchase not found'}, status=status.HTTP_404_NOT_FOUND)
        purchase.is_deleted = True
        purchase.save()
        return Response({'message': 'Purchase soft deleted'}, status=status.HTTP_204_NO_CONTENT)


class PurchaseDetailListCreateAPIView(APIView):
    """
    Purchase Details List View & Create View
    permission permmsion protected
    Handles listing all purchase details for a given purchase and creating new purchase details.
    Update Stock & Balance on Iteam Each purchase
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, header_code):
        try:
            details = PurchaseDetail.objects.filter(header_code=header_code)
            serializer = PurchaseDetailSerializer(details, many=True)
        except Exception as e:
            print('Error', e)
        return Response(serializer.data)

    def post(self, request, header_code):
        try:
            purchase_header = PurchaseHeader.objects.get(code=header_code)
            print(purchase_header.code)
        except PurchaseHeader.DoesNotExist:
            return Response({'error': 'Purchase header not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PurchaseDetailSerializer(data=request.data)
        if serializer.is_valid():
            purchase_detail = serializer
            purchase_detail.save()
            item = serializer.validated_data['item_code']
            item.stock += serializer.validated_data['quantity']
            item.balance += serializer.validated_data['quantity'] * serializer.validated_data['unit_price']
            item.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SellListCreateAPIView(APIView):
    """
    Sell List View & Create View
    permission permmsion protected
    Handles listing all sales and creating a new sale.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        sells = SellHeader.objects.filter(is_deleted=False)
        serializer = SellHeaderSerializer(sells, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SellHeaderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SellRetrieveUpdateDeleteAPIView(APIView):
    """
    Sell Update, Detail, Delete View
    permission protected
    Retrieve, update, or soft delete a sell.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, code):
        try:
            return SellHeader.objects.get(code=code, is_deleted=False)
        except SellHeader.DoesNotExist:
            return None

    def get(self, request, code):
        sell = self.get_object(code)
        if not sell:
            return Response({'error': 'Sell not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SellHeaderSerializer(sell)
        return Response(serializer.data)

    def put(self, request, code):
        sell = self.get_object(code)
        if not sell:
            return Response({'error': 'Sell not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SellHeaderSerializer(sell, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code):
        sell = self.get_object(code)
        if not sell:
            return Response({'error': 'Sell not found'}, status=status.HTTP_404_NOT_FOUND)
        sell.is_deleted = True
        sell.save()
        return Response({'message': 'Sell soft deleted'}, status=status.HTTP_204_NO_CONTENT)


class SellDetailListCreateAPIView(APIView):
    """
    Sell Details List View & Create View
    permission permmsion protected
    Handles listing all sell details for a given sell and creating new sell details.
    Update Stock & Balance on Iteam Each Sell
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, header_code):
        try:
            details = SellDetail.objects.filter(header_code=header_code)
            serializer = SellDetailSerializer(details, many=True)
        except Exception as e:
            print('Error', e)
        return Response(serializer.data)

    def post(self, request, header_code):
        try:
            sell_header = SellHeader.objects.get(code=header_code)
        except SellHeader.DoesNotExist:
            return Response({'error': 'Sell header not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SellDetailSerializer(data=request.data)
        if serializer.is_valid():
            sell_detail = serializer
            sell_detail.save()
            item = serializer.validated_data['item_code']
            list_items = PurchaseDetail.objects.filter(item_code=item)
            storage_stok= item.stock
            required_stok = sell_detail.data['quantity']

            # Check Treshhold Stock to Change Price
            if storage_stok > required_stok:
                while required_stok != 0:
                    for value in list_items:
                        if value.quantity > required_stok:
                            item.stock -= required_stok
                            item.balance -= required_stok * value.unit_price
                            item.save()
                            required_stok = 0
                        elif value.quantity <= required_stok:
                            item.stock -= value.quantity
                            item.balance -= value.quantity * value.unit_price
                            required_stok -= value.quantity
                            item.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'error': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemReportAPIView(APIView):
    """
    Handles Print Stock Report.
    Fetching Data as JSON (Reverse Transformation)
    Working on Progress PDF
    """

    permission_classes = [AllowAny]

    def get(self, request, code):
        # Get Date
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Get item with related purchase and sell details
        item = Item.objects.prefetch_related('pitemcode', 'sitemcode').get(code=code, is_deleted=False)

        # Get purchases and sales for the item within date range
        purchases = PurchaseHeader.objects.prefetch_related('details__item_code')\
                .filter(date__range=(start_date, end_date), details__item_code__code=code)\
                .order_by('date')
        sells = SellHeader.objects.prefetch_related('details__item_code')\
                .filter(date__range=(start_date, end_date), details__item_code__code=code)\
                .order_by('date')

        # Get detail purchases and sales from selected purchases and sales
        detail_purchase = PurchaseDetail.objects.filter(item_code=code, header_code_id__in=purchases\
                                                        .values_list('code')).order_by('id')
        detail_sell = SellDetail.objects.filter(item_code=code,header_code_id__in=sells\
                                                .values_list('code')).order_by('id')

        # Combine purchase and sell details in a single list
        transactions = []

        # Detail
        in_stock_qty = []
        in_stock_price = []
        in_stock_total = []
        in_balance_qty = 0
        out_stock_qty = []
        out_stock_price = []
        out_stock_total = []
        out_balance_qty = 0
        balance_qty = 0
        balance = 0

        # Details Purchase
        for detail in detail_purchase:

            # Calculate Each Transaction
            in_stock_qty.append(detail.quantity)
            in_stock_price.append(detail.unit_price)
            in_stock_total.append(detail.quantity * detail.unit_price)
            in_balance_qty += detail.quantity
            balance_qty += detail.quantity
            balance += detail.quantity * detail.unit_price

            transactions.append({
                'date': detail.header_code.date,
                'description': detail.header_code.description,
                'code': detail.header_code.code,
                'in_qty': detail.quantity,
                'in_price': detail.unit_price,
                'in_total': detail.quantity * detail.unit_price,
                'out_qty': 0,
                'out_price': 0,
                'out_total': 0,
                'stock_qty': in_stock_qty[:],
                'stock_price': in_stock_price[:],
                'stock_total': in_stock_total[:],
                'balance_qty': in_balance_qty,
                'balance': balance,
            })

        # Details Sell
        for detail in detail_sell:
            required_stok = detail.quantity

            # Check Treshhold Stock to Change Price
            while required_stok != 0:
                out_qty = 0
                out_price = 0
                out_total = 0
                for value in detail_purchase:
                    if value.quantity > required_stok:
                        out_qty = required_stok
                        out_price = value.unit_price
                        out_total = required_stok * value.unit_price
                        out_balance_qty += required_stok

                        out_stock_qty.append(balance_qty-out_qty)
                        out_stock_price.append((balance - out_total)/out_qty)
                        out_stock_total.append(balance-out_total)

                        balance_qty -= required_stok
                        balance -= required_stok * value.unit_price
                        required_stok = 0

                    elif value.quantity <= required_stok:
                        out_qty = value.quantity
                        out_price = value.unit_price
                        out_total = value.quantity * value.unit_price
                        out_balance_qty += value.quantity

                        out_stock_qty.append(balance_qty-out_qty)
                        out_stock_price.append((balance - out_total)/out_qty)
                        out_stock_total.append(balance-out_total)

                        balance_qty -= value.quantity
                        balance -= value.quantity * value.unit_price
                        required_stok -= value.quantity

                    transactions.append({
                        'date': detail.header_code.date,
                        'description': detail.header_code.description,
                        'code': detail.header_code.code,
                        'in_qty': 0,
                        'in_price': 0,
                        'in_total': 0,
                        'out_qty': out_qty,
                        'out_price': out_price,
                        'out_total': out_total,
                        'stock_qty': [0] + out_stock_qty,
                        'stock_price': [0] + out_stock_price,
                        'stock_total': [0] + out_stock_total,
                        'balance_qty': balance_qty,
                        'balance': balance,
                    })

                    out_stock_qty = []
                    out_stock_price = []
                    out_stock_total = []

        # Serialize data
        response_data = {
            'result': {
                'items': transactions,
                'item_code': item.code,
                'name': item.name,
                'unit': item.unit,
                'summary': {
                    'in_qty': in_balance_qty,
                    'out_qty': out_balance_qty,
                    'balance_qty': item.stock,
                    'balance': item.balance
                }
            }
        }

        return JsonResponse(response_data, safe=False)

        # Return Context to HTML
        context = {
            'item': item,
            }

        return  Render.render('report_pdf.html', context)
