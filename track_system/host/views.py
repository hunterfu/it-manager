# Create your views here.
from django.http import HttpResponse
 
def index(request):
    return HttpResponse('Hello')
 
def waypoints(request):
    return HttpResponse('Hello')
 
def search(request):
    return HttpResponse('Hello')
 
def search_near_roads(request):
    return HttpResponse('Hello')
