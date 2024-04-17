from django.contrib import admin
from home.models import Users
# Register your models here.

class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'display_name', 'last_online')
    

admin.site.register(Users, UsersAdmin)
