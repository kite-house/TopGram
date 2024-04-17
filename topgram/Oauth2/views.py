from django.http import HttpResponseRedirect
from Oauth2.models import User
from Oauth2.inspector import Valid

# Create your views here.

@Valid.registration
def registration(request, username, password):
    User.objects.create_user(username = username, password = password, display_name = username).save()
    return HttpResponseRedirect('/login')
  