from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePage, name = 'home'),
    path('zhub/', views.HubPage, name = 'zhub'),
    path('generatedZipf/', views.generateChart, name = 'gZipf'),
]
