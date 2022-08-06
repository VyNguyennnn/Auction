import json
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
from .models import messages, chat_room, account, product, order, room, history_bidding
from channels.db import database_sync_to_async
from bson import ObjectId
import datetime
from django.template.loader import render_to_string
from django.utils import timezone
# from ad.models import account as ad_account

# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#
#         self.accept()
#         # self.room_name = self.scope['url_route']['kwargs']['room_name']
#         # self.room_group_name = 'chat_%s' % self.room_name
#         self.send(text_data=json.dumps({
#             'type':'connection_established',
#             'message':'You are now connected!'
#         }))
#
#
#
#
    # def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json['message']
    #
    #     # async_to_sync(self.channel_layer.group_send)(
    #     #     self.room_group_name,
    #     #     {
    #     #         'type':'chat_message',
    #     #         'message':message
    #     #     }
    #     # )
    #     print('Message: ', message)
    #
    #     self.send(text_data=json.dumps({
    #         'type':'chat',
    #         'message':message
    #     }))
#
#     def chat_message(self, event):
#         message = event['message']
#
#         self.send(text_data=json.dumps({
#             'type':'chat',
#             'message':message
#         }))

class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'tester_message',
                'tester': 'tester',
            }
        )


    async def tester_message(self, event):
        tester = event['tester']

        await self.send(text_data=json.dumps({
            'tester': tester,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        usr = text_data_json['usr']
        receiver = text_data_json['receiver']
        room_id = text_data_json['room_id']

        await self.create_messages(usr, room_id, message, receiver)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chatroom_message',
                'message': message,
                'usr': usr,
                'receiver': receiver,
                'room_id': room_id,
                # 'tester': 'tester',
            }
        )
        print('Message: ', message)
        print('usr: ', usr)
        print('room_id: ', room_id)

    async def chatroom_message(self, event):
        message = event['message']
        usr = event['usr']
        receiver = event['receiver']
        room_id = event['room_id']
        # html_users = render_to_string("website/mes.html", {'mes': messages.objects(receiver=usr)})

        await self.send(text_data=json.dumps({
            'type':'chat',
            'message':message,
            'usr': usr,
            'timestamp': datetime.datetime.now().isoformat(),
            # 'html_users': html_users
        }))

    @database_sync_to_async
    def create_messages(self, usr, room_id, content, receiver):
        print(usr)
        print(receiver)
        r = chat_room.objects(pk=ObjectId(room_id)).first()
        re = account.objects(pk=receiver).first()
        acc = account.objects(pk=usr).first()
        m = messages(chat_room=r, sender=acc, receiver=re, content=content)
        return m.save()
    pass

# class ChatRoomConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = 'chat_%s' % self.room_name
#
#         #Join room
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         #Leave group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data['message']
#         username = data['username']
#         room = data['room']
#
#          # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#             'type': 'chat_message',
#             'message': message,
#             'username': username
#             }
#         )
#
#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event['message']
#         username = event['username']
#
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message,
#             'username': username
#         }))

class MessageConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            'users',
            self.channel_name
        )
        await self.accept()


        usr = self.scope['url_route']['kwargs']['usr']
        await self.show_message(usr)

        html_users = render_to_string("website/mes.html", {'mes': messages.objects(receiver=usr)})

        await self.send(text_data=json.dumps({

            # "type": "message",
            "event": "Change Status",
            "html_users": html_users,
        }))

        await self.channel_layer.group_send(
            'users',
            {
                'type': 'message',
                'usr': usr,
            }
        )



    async def disconnect(self, close_code):
        usr = self.scope['url_route']['kwargs']['usr']
        await self.channel_layer.group_discard(
            'users',
            self.channel_name
        )
        await self.show_message(usr)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        usr = text_data_json['usr']

        await self.channel_layer.group_send(
            'users',
            {
                'type': 'message',
                'usr': usr,
                # 'tester': 'tester',
            }
        )
        print('usr: ', usr)
        await self.show_message(usr)

    @database_sync_to_async
    def message(self, usr):
        return messages.objects(receiver=usr)

    async def show_message(self, usr):
        mes = messages.objects(receiver=usr)
        html_users = render_to_string("website/mes.html", {'mes': messages.objects(receiver=usr)})

        await self.send(text_data=json.dumps({

            # "type": "message",
            "event": "Change Status",
            "html_users": html_users,
        }))

    # async def user_update(self, event):
    #     await self.send_json(event)
    #     print('user_update', event)

    # async def show_message(self, event):
    #     print(event)
    #     usr = event['usr']
    #     mes = messages.objects(receiver=usr)
    #     html_users = render_to_string("website/mes.html", {'mes': mes})
    #
    #     await self.send(text_data=json.dumps({
    #         "html_users": html_users
    #     }))
    async def message(self, event):
        print(event)


class RoomEndConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = 'chat_%s' % self.room_id
        r = room.objects(pk=ObjectId(self.room_id)).first()
        winner = r.highestbidder.pk
        html_history = render_to_string("website/history.html", {'his': history_bidding.objects()})
        html_congra = render_to_string("website/congratulation.html", {'his': ''})
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print('connected')
        await self.accept()

        await self.send(text_data=json.dumps({
            "type": 'tester_message',
            "event": "Change Status",
            "html_history": html_history,
            "html_congra": html_congra,
            'winner': winner
        }))
        # await self.create_order(self.room_id, timeout)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'tester_message',
                'timeout': 0,
                'room_id': self.room_id,
            }
        )


    async def tester_message(self, event):

        time_out = event['timeout']
        room_id = event['room_id']

        await self.send(text_data=json.dumps({
            'time_out': time_out,
            'room_id': room_id,
        }))
        print('time out '+ str(time_out))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def receive(self, text_data):
        print('ncjccjcjcjcjcjcjcj')
        text_data_json = json.loads(text_data)
        room_id = text_data_json['room_id']
        timeout = text_data_json['timeout']
        print(timeout)

        # await self.create_order(room_id, timeout)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'create_order',
                'room_id': room_id,
                'timeout': timeout,
                # 'tester': 'tester',
            }
        )
        print('room_id: ', room_id)



    @database_sync_to_async
    def create_order(self, event):
        room_id = event['room_id']
        timeout = event['timeout']

        print(room_id)
        r = room.objects(pk=ObjectId(room_id)).first()
        seller = r.seller_id.pk
        buyer = r.highestbidder.pk
        product_id = r.product_id.pk
        prod = product.objects(pk=ObjectId(product_id)).first()
        quantity = prod.quantity
        if (r.current_bid <= r.highestbidder_bid):
            total = r.current_bid
        else:
            total = r.highestbidder_bid
        print('create order dang chay')
        if not order.objects(room_id=ObjectId(room_id)).exists():
            m = order(seller=seller, buyer=buyer, product_id=prod, quantity=quantity, total=total, room_id=r)
            t = m.save()
            room.objects(pk=ObjectId(room_id)).update(status='closed')
            print('Tao don hang thanh cong!')
        else:
            t = ''
        print('Don hang da ton tai!')
        return r.highestbidder.pk

    # pass

class UpdateBidConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        #Join room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        #Leave group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        room = data['room']

         # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
            'type': 'chat_message',
            'message': message,
            'username': username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))