from django.shortcuts import render
from rest_framework.serializers import ModelSerializer
from .models import FunnelDate
from rest_framework.generics import ListAPIView


# Create your views here.
class FunnelDateSerializer(ModelSerializer):
    class Meta:
        model = FunnelDate
        fields = '__all__'

class FunnelDateViewSet(ListAPIView):
    queryset = FunnelDate.objects.all()
    serializer_class = FunnelDateSerializer

