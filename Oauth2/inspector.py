from django.shortcuts import render
import requests
from django.http import HttpResponseRedirect
from Oauth2 import models
# ===============================================
class Valid():
    def registration(func):
        def wrapper(request):
            def output(text):
                return render(request, 'registration/registration.html', context={'text' : text})

            username = request.POST.get('username')
            password = request.POST.get('password')

            if username == None or password == None:
                return output(' ')
            
            if len(username) > 30 or len(password) > 30:
                return output('Логин и пароль не могут содержать больше 30 символов!')
            
            if len(username) < 4:
                return output('Логин должен содержать минимум 4 символа!')

            if len(password) < 5:
                return output('Пароь должен содержать минимум 5 символов!')

            if models.User.objects.filter(username = username):
                return output('Данный пользовател уже существует!')
            
            if False if all(char not in username for char in '!@"#№;$%^:&?*()_-=+<,. `~йцукенгшщз{[]}хъфывапролджэячсмитьбю') else True:
                return output('Логин не может содержать данные символы!')
            
            if False if all(char not in password for char in 'йцукенгшщзхъфывапролджэячсмитьбю') else True:
                return output('Пароль не должен содержать русские буквы!')
                
            return func(request, username, password)
        return wrapper

    def edit_user(func):
        def wrapper(self, request):
            def output(text):
                return HttpResponseRedirect(f'/settings_error/?error={text}')
            
            if request.POST.get("edit_avatar") != '':
                avatar = request.POST.get('edit_avatar')            

                if 'https://' not in avatar:
                    return output("Введите ссылку на аватарку!")

                try:
                    response = requests.head(avatar)
                    content_type = response.headers.get('content-type')
                    try:
                        if 'image' not in content_type:
                            return output('Некоректная ссылка!')
                    except Exception:
                        return output('Некоректная ссылка!')
                except Exception:
                    return output('Не удалось загрузить изображение!')

                self.avatar = avatar

            if request.POST.get("edit_display_name") != '':
                display_name = request.POST.get('edit_display_name')

                if len(display_name) < 4:
                    return output("Имя должно содержать минимум 4 символа!")
                
                if len(display_name) > 30:
                    return output("Имя не должно содержать больше 30 символов!")

                self.display_name = display_name

            func(self,request)
            return HttpResponseRedirect('/')
        return wrapper