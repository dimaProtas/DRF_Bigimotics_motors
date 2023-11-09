from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.utils import timezone
from .models import MessageModel, UserAbstract
from django.shortcuts import get_object_or_404


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Создание уникального канала для переписки
        chat_room_name = f"private_chat"
        await self.channel_layer.group_add(chat_room_name, self.channel_name)
        await self.accept()
        print(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        # Удаление из группы для переписки
        chat_room_name = f"private_chat"
        await self.channel_layer.group_discard(chat_room_name, self.channel_name)
        print(f"WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data=None):
        data = json.loads(text_data)
        message_text = data['text']
        recipient_id = data['recipient']
        sender = data['sender']
        print(data)

        if recipient_id != sender:
            chat_room_name = f"private_chat"
            print(sender, recipient_id, message_text, 'То что сохранил)')
            # Сохранение сообщения
            await self.save_message(sender, recipient_id, message_text)

            # Отправка сообщения обратно всем в группу
            await self.send_message_to_group(sender, recipient_id, message_text, chat_room_name)

    @database_sync_to_async
    def save_message(self, sender, recipient_id, message_text):
        sender_objects = UserAbstract.objects.get(id=sender)
        recipient_obj = UserAbstract.objects.get(id=recipient_id)
        message = MessageModel(sender=sender_objects, recipient=recipient_obj, text=message_text)
        message.save()
        print(message, 'То что сохранил)')

    # @database_sync_to_async
    async def send_message_to_group(self, sender, recipient_id, message_text, chat_room_name):
        # sender_objects = UserAbstract.objects.get(id=sender)
        # recipient_obj = UserAbstract.objects.get(id=recipient_id)
        formatted_datetime = timezone.localtime(timezone.now()).strftime('%d %B %Y г. %H:%M')
        await self.channel_layer.group_send(
            chat_room_name,
            {
                "type": "chat_message",
                "sender": sender,
                "sender_id": sender,
                "recipient_id": recipient_id,
                "message": message_text,
                "timestamp": formatted_datetime,
            },
        )
        print('SEND_MESSAGE_TO_GROUP')

    async def chat_message(self, event):
        print('На фронт', event)
        sender = event["sender"]
        sender_id = event["sender_id"]
        recipient_id = event["recipient_id"]
        message = event["message"]
        timestamp = event["timestamp"]
        await self.send(text_data=json.dumps({"sender": sender, "sender_id": sender_id, "recipient_id": recipient_id, "message": message, "timestamp": timestamp}))

