from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User


# Create your views here.

def valid(username, password):
    if username == None and password == None:
        return 'Error', {'text' : ''}

    if len(username) > 30 and len(password) > 30:
        return 'Error', {'text': 'Логин и пароль не могут содержать больше 30 символов!'}
    
    if User.objects.filter(username = username):
        return 'Error', {'text' : 'Данный пользователь уже существует!'}

    return 'Accept', {'text' : 'Доступ получен!'}

def registration(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    print(username, password)

    code, content = valid(username, password)
    if code =='Accept':
        user = User.objects.create_user(username, '', password)
        user.save
        return HttpResponseRedirect('/accounts/login')
    
    else:
        print(content)
    
    return render(request, 'registration/registration.html', context=content)
  