from django.shortcuts import render
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
import json
# Create your views here.


class MarkNotificationAsRead(APIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = {"status":"", "message":""}
        try:
            notification_id = request.data.get('notification_id')
            user = request.user                  
            if notification_id:
                notification_id = json.loads(notification_id)
                for n_id in notification_id:
                    notification = NotificationBox.objects.filter(id=n_id, notify_for=user).first()
                    notification.is_read = True
                    notification.save()
            else:
                unread_notifications = NotificationBox.objects.filter(notify_for=user, is_read=False)
                for notification in unread_notifications:
                    notification.is_read = True
                    notification.save()
            data["status"] = status.HTTP_200_OK
            data["message"] = "Marked unread notifications as read."
            
        except Exception as e:
            data["status"] = status.HTTP_400_BAD_REQUEST
            data["message"] = f'{str(e)}'
        return Response(data)
    
