from django.contrib import admin
from Oauth2.models import User
# Register your models here.

class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'display_name', 'last_online', 'is_staff')

admin.site.register(User, UsersAdmin)