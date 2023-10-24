from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def Oauth2(request):
    username = request.POST.get('u')
    password = request.POST.get('p')
    print(username, password)
    return render(request, 'auth.html')    