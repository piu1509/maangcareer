import json
from urllib.parse import parse_qs
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import *
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from django.utils import timezone

from datetime import datetime
from rest_framework import serializers


class NotificationBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationBox
        fields = "__all__"



class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"notifications_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

        # Send initial data when connection is established
        self.send_initial_data()

    def send_initial_data(self):
        user = Room.objects.filter(name=self.room_name).first().user
        unread_noti_count = NotificationBox.objects.filter(room__name=self.room_name, notify_for=user, is_read=False).count()
        notifications = NotificationBox.objects.filter(room__name=self.room_name, notify_for=user).order_by("-id")
        # Serialize notifications
        notification_data = NotificationBoxSerializer(notifications, many=True)
        # Send the initial batch of notifications
        self.send(text_data=json.dumps({
            "all_notifications": notification_data.data,
            "unread_noti_count": unread_noti_count
        }))

    def receive(self, text_data):
        # Process incoming message from WebSocket client
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')

        # Handle different types of messages here based on your application's requirements
        if message == "new_message":
            # Handle new message received from client
            self.handle_new_message(text_data_json)
        else:
            # Handle other types of messages
            pass

    def send_notification(self, event):
        notification_data = event["notification"]
        print('data', notification_data)
        print("event", event)
        
        if notification_data.get("is_universal"):
            # Handle universal notifications separately
            self.send(text_data=json.dumps({
                "notification": notification_data,
                "unread_noti_count": None  # No unread count for universal notifications
            }))
        else:
            try:
                notification = NotificationBox.objects.get(id=notification_data.get("id"))
            except NotificationBox.DoesNotExist:
                return  # Exit if the notification does not exist

            room = Room.objects.filter(user=notification.notify_for).first()

            if room and room.name == self.room_name:
                unread_noti_count = NotificationBox.objects.filter(
                    room__name=self.room_name, notify_for=notification.notify_for, is_read=False
                ).count()

                self.send(text_data=json.dumps({
                    "notification": notification_data,
                    "unread_noti_count": unread_noti_count
                }))

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

