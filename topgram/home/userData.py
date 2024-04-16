
from datetime import datetime
from home.models import Users
import pytz
from django.utils import timezone
from cryptography.fernet import Fernet
from topgram.settings import FERNET_SECRET_KEY

class UserData:
    ''' Класс для обработки запросов пользователя '''
    def __init__(self, request, user):
        try:
            recipient_user = Users.objects.get(username = user)
        except Exception:
            recipient_user = Users.objects.get(username = request.user)

        if 'user_timezone' in request.session:
            request.session['user_timezone']

        else:
            request.session['user_timezone'] = 'Europe/Dublin'

        self.request = request
        self.user = user
        self.recipient_user = recipient_user
        self.owner_user = Users.objects.get(username = request.user)
        self.owner_user.last_online = timezone.now()
        self.owner_user.save(update_fields=['last_online'])
        self.fernet = Fernet(FERNET_SECRET_KEY)
        
    def display_time(self, timeMsg):
        ''' Отображение времени '''
        if datetime.now(pytz.timezone(self.request.session['user_timezone'])).strftime("%d.%m.%Y %H:%M").split(' ')[0] == timeMsg.split(' ')[0]:
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
                    'sender_status' : sender_status,
                    "sender_avatar" : Users.objects.get(username = message['sender_name']).avatar,
                    "content" : self.fernet.decrypt(message['content']).decode()
                })


        chat_list = []
        for chat in self.owner_user.chat_list:
            chat_user = Users.objects.get(username = chat['name'])

            chat_list.append({
                "id" : chat['id'],
                'username' : chat['name'],
                'name' : Users.objects.get(username = chat['name']).display_name,
                "avatar" : chat_user.avatar,
                "is_online" : chat_user.is_online(),
                "last_msg" : self.fernet.decrypt(chat['last_msg']).decode(),
                "last_time_msg" : self.display_time(chat['last_time_msg'])
            })
        
        if self.recipient_user == None:
            self.recipient_user.username = "None"

        return {
            "owner_name" : self.owner_user.username,
            "display_owner_name" : self.owner_user.display_name,
            'recipient_name' : self.recipient_user.display_name,
            'recipient_avatar' : self.recipient_user.avatar,
            'is_online' : self.recipient_user.get_online_info(),
            "owner_avatar" :self.owner_user.avatar,
            "chat_list" : chat_list[::-1],
            "messages" : messages_edit
        }
    
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

        # обновляем все ид

        for idx, item in enumerate(self.owner_user.chat_list, start=1):
            item['id'] = idx

        for idx, item in enumerate(self.recipient_user.chat_list, start=1):
            item['id'] = idx

        # Изменение чат листа у отправителя.

        self.owner_user.chat_list.append({
            "id": len(self.owner_user.chat_list) + 1,
            "name": self.recipient_user.username,
            "avatar":self.recipient_user.avatar,
            "last_msg": self.fernet.encrypt(f'Вы: {msg}'.encode()).decode(),
            "last_time_msg": timeMsg
        })

        # Изменение чат листа у получателя

        self.recipient_user.chat_list.append({
            "id": len(self.recipient_user.chat_list) + 1,
            "name": self.owner_user.username,
            "avatar":self.owner_user.avatar,
            "last_msg": self.fernet.encrypt(msg.encode()).decode(),
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
        # encMessage = self.fernet.encrypt(input_message.encode())
        message.append({
            "id" : len(message) + 1,
            "time" : datetime.now(pytz.timezone(self.request.session['user_timezone'])).strftime("%d.%m.%Y %H:%M"),
            'content' : self.fernet.encrypt(input_message.encode()).decode(), # Шифрование
            'sender_name' : self.owner_user.username
        })

        try:
            message = self.recipient_user.messages['recipient_name'][self.owner_user.username]
        except Exception:
            self.recipient_user.messages['recipient_name'] = {self.owner_user.username : []}
            message = self.recipient_user.messages['recipient_name'][self.owner_user.username]

        message.append({
            "id" : len(message) + 1,
            "time" : datetime.now(pytz.timezone(self.request.session['user_timezone'])).strftime("%d.%m.%Y %H:%M"),
            'content' : self.fernet.encrypt(input_message.encode()).decode(), # Шифрование
            'sender_name' : self.owner_user.username
        })

        self.update_chat_list(input_message, datetime.now(pytz.timezone(self.request.session['user_timezone'])).strftime("%d.%m.%Y %H:%M"))

        self.owner_user.save()
        
        self.recipient_user.save()

        return message[-1]
    
    def delete_message(self):
        ''' Удаление сообщений '''
        message_id = int(self.request.POST.get("delete_message")) - 1
        owner_messages = self.owner_user.messages['recipient_name'][self.recipient_user.username]
        recipient_messages = self.recipient_user.messages['recipient_name'][self.owner_user.username]

        if message_id < len(owner_messages):
            owner_messages.pop(message_id)
            for idx, item in enumerate(owner_messages, start=1):
                item['id'] = idx
            self.owner_user.save()

        if message_id < len(recipient_messages):
            recipient_messages.pop(message_id)
            for idx, item in enumerate(recipient_messages, start=1):
                item['id'] = idx
            self.recipient_user.save()


        # Если сообщение последнее, то удаляем из чат листа.
        if message_id == len(owner_messages) and message_id  == len(recipient_messages) :
            if message_id > 0:
                self.update_chat_list(self.fernet.decrypt(owner_messages[message_id - 1]['content']).decode(), owner_messages[message_id - 1]['time'])
            else:
                self.update_chat_list(" ", " ")

            self.owner_user.save()
            self.recipient_user.save()
        

    def delete_chat(self):
        ''' Удаление чатов '''
        chat_id = int(self.request.POST.get("delete_chat")) - 1

        owner_chat = self.owner_user.chat_list[chat_id]


        recipient_chat = Users.objects.get(username = owner_chat['name']).chat_list
        
        try:
            index = next(index for index, item in enumerate(recipient_chat) if item["name"] == self.owner_user.username)
        except StopIteration:
            index = 0


        self.owner_user.chat_list.pop(chat_id)
        self.recipient_user.chat_list.pop(index)


        for idx, item in enumerate(self.owner_user.chat_list, start=1):
            item['id'] = idx

        for idx, item in enumerate(self.recipient_user.chat_list, start=1):
            item['id'] = idx


        del self.owner_user.messages['recipient_name'][self.recipient_user.username]
        del self.recipient_user.messages['recipient_name'][self.owner_user.username]

        self.owner_user.save()
        self.recipient_user.save()



