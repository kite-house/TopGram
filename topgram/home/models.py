from django.db import models
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.translation import gettext as _
from django.utils import timezone

class Users(models.Model):
    username = models.CharField(max_length = 150)
    display_name = models.CharField(max_length = 150, default = username)
    avatar = models.CharField(max_length = 1000, default = 'https://avatars.mds.yandex.net/i?id=d44d7c579e55f0bdfad006c09502bcb7168a8444-10889692-images-thumbs&n=13')
    chat_list = models.JSONField(default=list)
    messages = models.JSONField(default=dict)
    last_online = models.DateTimeField(blank=True, null=True)
 
    def is_online(self):
        if self.last_online:
            if (timezone.now() - self.last_online) < timezone.timedelta(minutes=7):
                return 'online'
        return False
 

    def get_online_info(self):
        if self.is_online():
            return _('В сети')
        if self.last_online:
            return _('Был(а) в сети: {}').format(naturaltime(self.last_online))
        

        return _('Был недавно')