from django.urls import path
from api_wh.views import (
    CustomTokenObtainPairView, CustomTokenRefreshView, ItemListCreateAPIView,
    ItemRetrieveUpdateDeleteAPIView, PurchaseListCreateAPIView,PurchaseRetrieveUpdateDeleteAPIView,
    PurchaseDetailListCreateAPIView, SellListCreateAPIView, SellDetailListCreateAPIView,
    SellRetrieveUpdateDeleteAPIView, ItemReportAPIView
)

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    # Item URLs
    path('items/', ItemListCreateAPIView.as_view(), name='item-list-create'),
    path('items/<str:code>/', ItemRetrieveUpdateDeleteAPIView.as_view(), name='item-detail'),

    # Purchase URLs
    path('purchase/', PurchaseListCreateAPIView.as_view(), name='purchase-list-create'),
    path('purchase/<str:code>/', PurchaseRetrieveUpdateDeleteAPIView.as_view(), name='purchase-detail'),
    path('purchase/<str:header_code>/details/', PurchaseDetailListCreateAPIView.as_view(), name='purchase-details'),

    # Sell URLs
    path('sell/', SellListCreateAPIView.as_view(), name='sell-list-create'),
    path('sell/<str:code>/', SellRetrieveUpdateDeleteAPIView.as_view(), name='purchase-detail'),
    path('sell/<str:header_code>/details/', SellDetailListCreateAPIView.as_view(), name='sell-details'),

    # Report
    path('report/<str:code>/', ItemReportAPIView.as_view(), name='report-item'),

]
