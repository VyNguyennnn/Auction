from django.urls import path

from . import views
urlpatterns = [
    path('admin', views.login_form),
    path('admin/login', views.login),
    path('admin/logout', views.logout),
    path('admin/index', views.index),
    path('admin/changepassword_form', views.change_password_form),
    path('admin/changepassword', views.changepwd),
    path('admin/category', views.category),
    path('admin/category/edit', views.category_edit),
    path('admin/category/update=<int:id>', views.category_update),
    path('admin/category/delete=<int:id>', views.delete_category),
    path('admin/category/attributes_attrgroups', views.attributes_attrgroups),
    path('admin/attribute_groups', views.attribute_groups),
    path('admin/attribute_groups/delete=<int:id>', views.delete_attribute_groups),
    path('admin/attribute_groups/update=<int:id>', views.update_attribute_groups),
    path('admin/attributes', views.attributes),
    path('admin/all_account', views.all_account),
    path('admin/blocked_account', views.blocked_account),
    path('admin/unblock_account', views.unblock_account),
    path('admin/attributes/delete=<int:id>', views.delete_attributes),
    path('admin/attributes/update=<int:id>', views.update_attributes),
    path('admin/message', views.message),
    path('admin/message/room_id/<str:room_id>', views.message_inner),
    path('admin/room', views.room),
    path('admin/room/history_bidding/<str:room_id>', views.room_history),
    #huy gia
    path('admin/cancel/bid', views.find_cancel_bid_form),
    #load product
    path('admin/cancel/bid/load/product', views.load_product),
    #load reason_form
    path('admin/cancel/bid/load/reason_form/<str:room_id>', views.reason_form),
    #load confirm
    path('admin/cancel/bid/load/confirm/<str:room_id>/<str:bidder>', views.confirm_form),
    #cancel bid
    path('admin/cancel_bid', views.cancel_bid),
    ]