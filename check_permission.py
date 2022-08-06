import pymongo
from django.conf import settings
from django.shortcuts import render, redirect

def permission(request, user, role):
    #user la mot document
    result = None
    if role == 'admin':
        try:
            usr = request.session.get('auction_account')['username']
            pwd = request.session.get('auction_account')['password']
            rl = request.session.get('auction_account')['role']
            if user is not None:
                if usr == user.pk and pwd == user.password and rl == role:
                    result = role
            return result
        except:
            return redirect('/admin/logout')
    else:
        try:
            usr = request.session.get('auction_account')['username']
            pwd = request.session.get('auction_account')['password']
            rl = request.session.get('auction_account')['role']
            if user is not None:
                if usr == user.pk and pwd == user.password and rl == role:
                    result = role
            return result
        except:
            return redirect('/logout')


