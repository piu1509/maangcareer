# from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet
from rest_framework.serializers import ModelSerializer
from rest_framework.mixins import CreateModelMixin

from .models import contactInfo

class ContactInfoSerializer(ModelSerializer):
    class Meta:
        model = contactInfo
        fields = '__all__'
        
class ContactInfoViewSet(CreateModelMixin, GenericViewSet):
    queryset = contactInfo.objects.all()
    serializer_class = ContactInfoSerializer