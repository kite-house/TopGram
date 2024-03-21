from django.shortcuts import render
from django import http
from django.contrib.auth.decorators import login_required
# Create your views here.
from home.models import Users


class Data_user:
    def __init__(self, request, user):
        try:
            recipient_user = Users.objects.get(username = user)
        except Exception:
            recipient_user = None
        owner_user = Users.objects.get(username = request.user)
        
        self.request = request
        self.user = user
        self.recipient_user = recipient_user
        self.owner_user = owner_user

    def data(self):
        try:
            messages = self.owner_user.messages['recipient_name'][self.recipient_user.username]
        except Exception:
            messages1 = {}
        else:
            messages1 = []
            for message in messages:
                if message['sender_name'] == self.owner_user.username:
                    sender_status = 'owner'

                else:
                    sender_status = ''
                messages1.append({
                    "id" : message['id'],
                    "time" : message['time'],
                    "sender_status" : sender_status,
                    "sender_avatar" : Users.objects.get(username = message['sender_name']).avatar,
                    "content" : message['content']
                })
        data = {
            "owner_name" : self.owner_user.username,
            'recipient_name' : self.recipient_user.username,
            'recipient_avatar' : self.recipient_user.avatar,
            "owner_avatar" : self.owner_user.avatar,
            "chat_list" : self.owner_user.chat_list,
            "messages" : messages1
        }
        return data
    
    def send_message(self):
        input_message = self.request.POST.get('input_message')
        try:
            message = self.owner_user.messages['recipient_name'][self.recipient_user.username]
        except Exception:
            self.owner_user.messages['recipient_name'] = {self.recipient_user.username : []}
            message = self.owner_user.messages['recipient_name'][self.recipient_user.username]

        message.append({
            "id" : len(message) + 1,
            "time" : "datetime_beta",
            'content' : input_message,
            'sender_name' : self.owner_user.username
        })

        self.owner_user.save()

        try:
            message = self.recipient_user.messages['recipient_name'][self.owner_user.username]
        except Exception:
            self.recipient_user.messages['recipient_name'] = {self.owner_user.username : []}
            message = self.recipient_user.messages['recipient_name'][self.owner_user.username]

        message.append({
            "id" : len(message) + 1,
            "time" : "datetime_beta",
            'content' : input_message,
            'sender_name' : self.owner_user.username
        })
        
        self.recipient_user.save()
        return self.recipient_user.username


@login_required
def home(request, user):
    if request.method == "POST":
        return http.HttpResponseRedirect(f'/{Data_user(request,user).send_message()}/')

    return render(request, 'home.html', context=Data_user(request,user).data())

