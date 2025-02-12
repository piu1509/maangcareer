from .views import ContactInfoViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('create-contact', ContactInfoViewSet, basename='create-contact')
urlpatterns = router.urls