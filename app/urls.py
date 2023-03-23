from django.urls import path
from . import views

urlpatterns = [
    path("connect", views.connect, name="connect"),
    path("selectAccount", views.selectAccount, name="selectAccount"),
    path("scope", views.scope, name="scope"),
    path("selectScope", views.selectScope, name="selectScope"),
    path("getAuthToken", views.getAuthToken, name="authToken"),
    path("getAccessToken", views.getAccessToken, name="accessToken"),
    path("getDetails", views.getDetails, name="getDetails"),
]
