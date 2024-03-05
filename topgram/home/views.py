from django.shortcuts import render
from django import http
from django.contrib.auth.decorators import login_required
# Create your views here.
from home.models import Users


@login_required
def home(request, user):
    try:
        recipient_user = Users.objects.get(username = user)
    except Exception:
        recipient_user = None
    owner_user = Users.objects.get(username = request.user)
    
    try:
        messages = owner_user.messages['recipient_name'][recipient_user.username]
    except Exception:
        messages1 = {}
    else:
        messages1 = []
        for message in messages:
            if message['sender_name'] == owner_user.username:
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
        "owner_name" : owner_user.username,
        'recipient_name' : recipient_user.username,
        'recipient_avatar' : recipient_user.avatar,
        "owner_avatar" : owner_user.avatar,
        "chat_list" : owner_user.chat_list,
        "messages" : messages1
    }

    if request.method == "POST":
        input_message = request.POST.get('input_message')
        try:
            message = owner_user.messages['recipient_name'][recipient_user.username]
        except Exception:
            owner_user.messages['recipient_name'] = {recipient_user.username : []}
            message = owner_user.messages['recipient_name'][recipient_user.username]

        message.append({
            "id" : len(message) + 1,
            "time" : "datetime_beta",
            'content' : input_message,
            'sender_name' : owner_user.username
        })

        owner_user.save()

        try:
            message = recipient_user.messages['recipient_name'][owner_user.username]
        except Exception:
            recipient_user.messages['recipient_name'] = {owner_user.username : []}
            message = recipient_user.messages['recipient_name'][owner_user.username]

        message.append({
            "id" : len(message) + 1,
            "time" : "datetime_beta",
            'content' : input_message,
            'sender_name' : owner_user.username
        })
        
        recipient_user.save()
        return http.HttpResponseRedirect(f'/{recipient_user.username}/')

    return render(request, 'home.html', context=data)

