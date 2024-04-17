from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from home.models import Users
from .data_inspector import valid_registration

# Create your views here.

@valid_registration
def registration(request, username, password):
    #  Создание таблицы в auth USER
    User.objects.create_user(username,'', password).save()

    # Создание таблицы в home User
    Users.objects.create(username = username, display_name = username).save()

    return HttpResponseRedirect('/accounts/login')
  