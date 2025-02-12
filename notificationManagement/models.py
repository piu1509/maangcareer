from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from time import sleep

# Create your models here.
   

class Room(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="room_user",null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only modify the name if the instance is being created
            self.name = f"room_{self.user.id}"
        super(Room, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class NotificationBox(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="NotifiRoom", null=True, blank=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    notify_for = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_for",null=True, blank=True)
    is_universal = models.BooleanField(default=False)

    def __str__(self) :
        return f"{self.title}:-{self.content}, Read-status{self.is_read}"

    

    def save(self, *args, **kwargs):
        super(NotificationBox, self).save(*args, **kwargs)
        # Add a slight delay
        self.send_notification()

    def send_notification(self):
        
        channel_layer = get_channel_layer()
        
        
        group_name = f"notifications_{self.room.name}"
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "notification": {
                    "id": self.id,
                    "title": self.title,
                    "text_message": self.content,
                    "is_read": self.is_read,
                    "created_at": self.created_at.isoformat(),
                    "is_universal": self.is_universal,  # Include this to distinguish between universal and normal notifications
                }
            }
        )

class Notification(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    users = models.ManyToManyField(User, blank=True)
    is_universal = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} | {self.content}'
    
    