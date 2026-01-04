from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r'', ExpenseViewSet, basename='expense')

app_name = 'expenses'

urlpatterns = [
    path('', include(router.urls)),
]