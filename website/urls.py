from allauth.account.views import LogoutView
from django.urls import path
from . import views
from .views import HomeView

app_name = 'website'

urlpatterns = [
    path('registration', views.registration),
    path('', views.login),
    path('logout', views.usr_logout),
    path('usr/0/changepassword_form', views.change_password_form),
    path('usr/0/changepassword', views.changepwd),
    path('usr/0/information', views.information),
    path('usr/0/information/update', views.update),
    path('home', views.home),
    path('seller/product', views.product),
    path('seller/detail_product/save', views.save_product),
    path('seller/detail_product_form', views.detail_product_form),
    path('seller/get_category', views.get_category),
    path('momo/<str:room_id>', views.thanhtoan_momo),
    path('room/<str:id>', views.room_detail),
    path('bidder/bid', views.bid),
    path('get_next_bids', views.get_next_bids),
    path('set_status_room', views.set_status_room),
    path('usr/0/history_bidding_list', views.history_bidding_list),
    path('usr/0/bidding/room/<str:room_id>', views.bidding_room),
    path('countdown/<str:id>/<str:timer>', views.countdown),
    path('congra', views.congratulation),
    path('reload_bid/<str:id>', views.reload_bid),
    path('usr/0/message', views.message),
    path('usr/0/orders', views.order_list),
    path('seller/room/list', views.seller_room),
    path('usr/0/message/room_id/<str:room_id>', views.message_inner),
    path('usr/cancel_bid', views.cancel_bid),
    path('seller/cancel_bid', views.seller_cancel_bid),
    #huy gia
    path('usr/0/cancel/bid', views.find_cancel_bid_form),
    path('seller/cancel/bid/form', views.seller_find_cancel_bid_form),
    #load product
    path('usr/0/cancel/bid/load/product', views.load_product),
    path('seller/cancel/bid/load/product', views.seller_load_product),
    #load reason_form
    path('usr/0/cancel/bid/load/reason_form/<str:room_id>', views.reason_form),
    path('seller/cancel/bid/load/reason_form/<str:room_id>', views.seller_reason_form),
    #load confirm
    path('usr/0/cancel/bid/load/confirm/<str:room_id>', views.confirm_form),
    path('seller/cancel/bid/load/confirm/<str:room_id>/<str:bidder>', views.seller_confirm_form),
    path('chat/id/usr/<str:usr_id>', views.chat_with_seller),
]
