from django.shortcuts import render
from django import http
from django.contrib.auth.decorators import login_required
# Create your views here.
from datetime import datetime
from home.models import Users
import pytz
from django.http import JsonResponse
import json



class Data_user:
    def __init__(self, request, user):
        try:
            recipient_user = Users.objects.get(username = user)
        except Exception:
            recipient_user = Users.objects.get(username = request.user)
        owner_user = Users.objects.get(username = request.user)
        
        self.request = request
        self.user = user
        self.recipient_user = recipient_user
        self.owner_user = owner_user


    def display_time(self, timeMsg):
        today = datetime.now(pytz.timezone(self.request.session['user_timezone'])).strftime("%d.%m.%Y %H:%M")
        if today.split(' ')[0] == timeMsg.split(' ')[0]:
            timeMsg = timeMsg.split(' ')[1]

        else:
            timeMsg = timeMsg.split(' ')[0] 

        return timeMsg

    def data(self):
        ''' Вывод данных в html шаблон '''

        try:
            messages = self.owner_user.messages['recipient_name'][self.recipient_user.username]
        except Exception:
            messages_edit = {}
        else:
            messages_edit = []
            for message in messages:
                if message['sender_name'] == self.owner_user.username:
                    sender_status = 'owner'

                else:
                    sender_status = ''
                messages_edit.append({
                    "id" : message['id'],
                    "time" : self.display_time(message['time']),
                    "sender_status" : sender_status,
                    "sender_avatar" : Users.objects.get(username = message['sender_name']).avatar,
                    "content" : message['content']
                })


        chat_list = []
        for chat in self.owner_user.chat_list:
            # проверка онлайна ---

            chat_list.append({
                "id" : chat['id'],
                'name' : chat['name'],
                "avatar" : chat['avatar'],
                "last_msg" : chat['last_msg'],
                "last_time_msg" : self.display_time(chat['last_time_msg'])
            })
        
        if self.recipient_user == None:
            self.recipient_user.username = "None"
        
        data = {
            "owner_name" : self.owner_user.username,
            'recipient_name' : self.recipient_user.username,
            'recipient_avatar' : self.recipient_user.avatar,
            "owner_avatar" : self.owner_user.avatar,
            "chat_list" : chat_list[::-1],
            "messages" : messages_edit
        }
        return data
    
    def update_chat_list(self, msg, timeMsg):
        ''' Обновление чат листа у отправителя и получателя сообщений '''
        # Проверка на присуствие в чат листе

        # Отправитель
        if list(map(lambda name: name['name'], self.owner_user.chat_list)).count(self.recipient_user.username) != 0:
            for chat in self.owner_user.chat_list:
                if self.recipient_user.username in chat['name']:
                    self.owner_user.chat_list.remove(chat)

        # Получатель
        if list(map(lambda name: name['name'], self.recipient_user.chat_list)).count(self.owner_user.username) != 0:
            for chat in self.recipient_user.chat_list:
                if self.owner_user.username in chat['name']:
                    self.recipient_user.chat_list.remove(chat)

        # Изменение чат листа у отправителя.

        self.owner_user.chat_list.append({
            "id": len(self.owner_user.chat_list) + 1,
            "name": self.recipient_user.username,
            "avatar":self.recipient_user.avatar,
            "last_msg": f"Вы: {msg}",
            "last_time_msg": timeMsg
        })

        # Изменение чат листа у получателя

        self.recipient_user.chat_list.append({
            "id": len(self.owner_user.chat_list) + 1,
            "name": self.owner_user.username,
            "avatar":self.owner_user.avatar,
            "last_msg": msg,
            "last_time_msg": timeMsg
        })

    def send_message(self):
        ''' Отправка и получение сообщений '''
        input_message = self.request.POST.get('input_message')
        try:
            message = self.owner_user.messages['recipient_name'][self.recipient_user.username]
        except Exception:
            self.owner_user.messages['recipient_name'] = {self.recipient_user.username : []}
            message = self.owner_user.messages['recipient_name'][self.recipient_user.username]

        message.append({
            "id" : len(message) + 1,
            "time" : datetime.now(pytz.timezone(self.request.session['user_timezone'])).strftime("%d.%m.%Y %H:%M"),
            'content' : input_message,
            'sender_name' : self.owner_user.username
        })

        self.update_chat_list(input_message, datetime.now(pytz.timezone(self.request.session['user_timezone'])).strftime("%d.%m.%Y %H:%M"))

        self.owner_user.save()

        try:
            message = self.recipient_user.messages['recipient_name'][self.owner_user.username]
        except Exception:
            self.recipient_user.messages['recipient_name'] = {self.owner_user.username : []}
            message = self.recipient_user.messages['recipient_name'][self.owner_user.username]

        message.append({
            "id" : len(message) + 1,
            "time" : datetime.now(pytz.timezone(self.request.session['user_timezone'])).strftime("%d.%m.%Y %H:%M"),
            'content' : input_message,
            'sender_name' : self.owner_user.username
        })
        
        self.recipient_user.save()
        return self.recipient_user.username

class Search_user:

    def __init__(self, request) -> None:
        self.request = request
        self.search = self.request.POST.get('search')

    def find(self):
        return self.valid_search()
    
    def valid_search(self):
        try:
            Users.objects.get(username = self.search)
        except Exception:
            return 'error_search'
        else:
            return self.search

def save_timezone(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request.session['user_timezone'] = data.get('timezone')

        return JsonResponse({'message': 'Timezone saved successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def home(request, user = None):
    if 'user_timezone' in request.session:
        request.session['user_timezone']

    else:
        request.session['user_timezone'] = 'Europe/Dublin'

    if request.method == "POST":
        if request.POST.get('search') != None:
            return http.HttpResponseRedirect(f'/{Search_user(request).find()}/')
        
        
        elif request.POST.get('input_message') != None:
            return http.HttpResponseRedirect(f'/{Data_user(request,user).send_message()}/')

    return render(request, 'home.html', context=Data_user(request,user).data())
