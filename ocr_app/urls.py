from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('result/<int:pk>/', views.ocr_result, name='ocr_result'),
    path('api/results/', views.get_ocr_results, name='api_results'),
]
