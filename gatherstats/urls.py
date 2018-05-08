"""
URL routing schema for IAR Stats Gatherer.

"""

from django.urls import path

from . import views

app_name = "gatherstats"

urlpatterns = [
    path('example', views.example, name='example'),
]
