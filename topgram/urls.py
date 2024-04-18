"""
URL configuration for topgram project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from home import views as home
from Oauth2 import views as Oauth2

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home.home, name = 'home'),
    path('home', home.home, name = 'home'),
    path('save_timezone/', home.save_timezone, name = 'save_timezone'),
    path('<slug:user>/', home.home, name = 'home'),
    path('<slug:user>', home.home, name = 'home'),
    path('settings/', home.home, name = 'home'),
    path('settings_error/', home.home, name = 'home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/registration', Oauth2.registration),
    path('error_search/', home.home, name = 'home')
]

handler404 = 'error_handler.views.error404'
handler500 = 'error_handler.views.error500'