from django.contrib import admin
from .models import *

# Register your models here.

class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')
    list_filter = ('user',)

class NotificationBoxAdmin(admin.ModelAdmin):
    list_display = ('title', 'room', 'notify_for', 'is_read', 'created_at', 'is_universal')
    search_fields = ('title', 'content', 'room__name', 'notify_for__username')
    list_filter = ('is_read', 'is_universal', 'created_at')

    def save_model(self, request, obj, form, change):
        # Only send notification when the instance is updated, not when created
        if change:
            obj.send_notification()
        super().save_model(request, obj, form, change)
        
class NotificationAdmin(admin.ModelAdmin):
    
    list_display = ('title', 'content')
    filter_horizontal = ('users',)

    def save_model(self, request, obj, form, change):
        super(NotificationAdmin, self).save_model(request, obj, form, change)

        if not change:  # New instance
            if form.cleaned_data['is_universal']:
                obj.users.set(User.objects.all())  # Assign all users for universal notifications
                for user in obj.users.all():
                    room, _ = Room.objects.get_or_create(user=user)
                    NotificationBox.objects.create(
                        room=room,
                        title=obj.title,
                        content=obj.content,
                        notify_for=user,
                        is_universal=True  # Mark as universal
                    )
            else:
                for user in form.cleaned_data['users']:
                    room, _ = Room.objects.get_or_create(user=user)
                    NotificationBox.objects.create(
                        room=room,
                        title=obj.title,
                        content=obj.content,
                        notify_for=user
                    )


admin.site.register(Room, RoomAdmin)
# admin.site.register(NotificationBox, NotificationBoxAdmin)
admin.site.register(Notification, NotificationAdmin)