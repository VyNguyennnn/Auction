from django.urls import re_path
from . import consumers


# websocket_urlpatterns = [
#     re_path(r'ws/socket-server', consumers.ChatConsumer.as_asgi()),
# ]

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatRoomConsumer.as_asgi()),
    re_path(r'ws/messages/(?P<usr>\w+)/$', consumers.MessageConsumer.as_asgi()),
    re_path(r'ws/room/end/(?P<room_id>\w+)/$', consumers.RoomEndConsumer.as_asgi()),
]

# websocket_urlpatterns = [
#   re_path('ws/(?P<room_name>\w+)/', consumers.ChatRoomConsumer.as_asgi()), # Using asgi
# ]