from django.shortcuts import HttpResponse


# Views
def index(request):
    HttpResponse("Index")
