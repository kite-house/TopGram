
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

        request.session.setdefault('user_timezone', 'Europe/Dublin')

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
            messages_edit = [{
                "id": message['id'],
                "time": self.display_time(message['time']),
                'sender_status': 'owner' if message['sender_name'] == self.owner_user.username else '',
                "sender_avatar": Users.objects.get(username=message['sender_name']).avatar,
                "content": self.fernet.decrypt(message['content']).decode()
            } for message in messages]
        except Exception:
            messages_edit = {}


        chat_list = [{
            "id": chat['id'],
            'username': chat['name'],
            'name': Users.objects.get(username=chat['name']).display_name,
            "avatar": Users.objects.get(username=chat['name']).avatar,
            "is_online": Users.objects.get(username=chat['name']).is_online(),
            "last_msg": self.fernet.decrypt(chat['last_msg']).decode(),
            "last_time_msg": self.display_time(chat['last_time_msg'])
        } for chat in self.owner_user.chat_list]


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

        def remove_from_chat_list(user, target_user):
            user.chat_list = [chat for chat in user.chat_list if chat['name'] != target_user.username]

        def update_chat_list_ids(chat_list):
            for idx, item in enumerate(chat_list, start=1):
                item['id'] = idx

        def update_chat_list_entry(user, target_user, encrypted_msg, timeMsg):
            user.chat_list.append({
                "id": len(user.chat_list) + 1,
                "name": target_user.username,
                "avatar": target_user.avatar,
                "last_msg": self.fernet.encrypt(encrypted_msg.encode()).decode(),
                "last_time_msg": timeMsg
            })


        # Удаление из чат-листов
        remove_from_chat_list(self.owner_user, self.recipient_user)
        remove_from_chat_list(self.recipient_user, self.owner_user)
        
        # Обновление идентификаторов
        update_chat_list_ids(self.owner_user.chat_list)
        update_chat_list_ids(self.recipient_user.chat_list)
        
        # Изменение чат-листа у отправителя
        update_chat_list_entry(self.owner_user, self.recipient_user, f'Вы: {msg}', timeMsg)
        
        # Изменение чат-листа у получателя
        update_chat_list_entry(self.recipient_user, self.owner_user, msg, timeMsg)

    def send_message(self):
        ''' Отправка и получение сообщений '''
        input_message = self.request.POST.get('input_message')

        try:
            message = self.owner_user.messages['recipient_name'][self.recipient_user.username]
        except Exception:
            print('здесь!')
            self.owner_user.messages['recipient_name'][self.recipient_user.username] = []
            message = self.owner_user.messages['recipient_name'][self.recipient_user.username]

        message.append({
            "id" : len(message) + 1,
            "time" : datetime.now(pytz.timezone(self.request.session['user_timezone'])).strftime("%d.%m.%Y %H:%M"),
            'content' : self.fernet.encrypt(input_message.encode()).decode(), # Шифрование
            'sender_name' : self.owner_user.username
        })

        try:
            message = self.recipient_user.messages['recipient_name'][self.owner_user.username]
        except Exception:
            print('здесь 222!')
            self.recipient_user.messages['recipient_name'][self.owner_user.username] = []
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


        def delete_msg_and_update_id(user, message_id):
            if message_id < len(user):
                user.pop(message_id)
                for idx, item in enumerate(user, start=1):
                    item['id'] = idx

        delete_msg_and_update_id(owner_messages, message_id)
        delete_msg_and_update_id(recipient_messages, message_id)

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
        recipient_user = Users.objects.get(username = owner_chat['name'])

        try:
            index = next(index for index, item in enumerate(recipient_user.chat_list) if item["name"] == self.owner_user.username)
        except StopIteration:
            index = 0

        if len(self.owner_user.chat_list) >= 0 and len(self.owner_user.chat_list) > chat_id:
            self.owner_user.chat_list.pop(chat_id)
        if len(self.recipient_user.chat_list) >= 0 and len(self.owner_user.chat_list) > index:
            self.recipient_user.chat_list.pop(index)

        def update_id(user):
            for idx, item in enumerate(user.chat_list, start=1):
                item['id'] = idx

        update_id(self.owner_user)
        update_id(recipient_user)

        if recipient_user.username in self.owner_user.messages['recipient_name']:
            del self.owner_user.messages['recipient_name'][recipient_user.username]
        if self.owner_user.username in recipient_user.messages['recipient_name']:
            del recipient_user.messages['recipient_name'][self.owner_user.username]

        self.owner_user.save()
        recipient_user.save()



