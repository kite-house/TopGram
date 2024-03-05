from django.db import models

class Users(models.Model):
    username = models.CharField(max_length = 150)
    avatar = models.CharField(max_length = 1000, default = 'https://avatars.mds.yandex.net/i?id=d44d7c579e55f0bdfad006c09502bcb7168a8444-10889692-images-thumbs&n=13')
    chat_list = models.JSONField(default= {"recipient_name" : {}})
    messages = models.JSONField(default=dict)
