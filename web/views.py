# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import random
import string
import time

from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from json import JSONEncoder
from django.views.decorators.csrf import csrf_exempt
from web.models import User,Token, Expense, Income, Passwordresetcodes
from datetime import datetime
from django.contrib.auth.hashers import make_password
from postmark import PMMail

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def grecaptcha_verify(request): #Bestoon 9 18:02
    data = request.POST
    captcha_rs = data.get('g-recaptcha-response')
    url = "https://www.google.com/recaptcha/api/siteverify"
    params = {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': captcha_rs,
        'remoteip': get_client_ip(request)
    }
    verify_rs = requests.get(url, params=params, verify=True)
    verify_rs = verify_rs.json()
    return verify_rs.get("success", False)



random_str = lambda N: ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))
def register(request):
    if request.POST.has_key('requestcode'): #form is filled. if not spam, generate code and save in db, wait for email confirmation, return message
        #is this spam? check reCaptcha
        if not grecaptcha_verify(request): # captcha was not correct
            context = {'message': 'کپچای گوگل درست وارد نشده بود. شاید ربات هستید؟ کد یا کلیک یا تشخیص عکس زیر فرم را درست پر کنید. ببخشید که فرم به شکل اولیه برنگشته!'} #TODO: forgot password
            return render(request, 'register.html', context)

        if User.objects.filter(email = request.POST['email']).exists(): # duplicate email
            context = {'message': 'متاسفانه این ایمیل قبلا استفاده شده است. در صورتی که این ایمیل شما است، از صفحه ورود گزینه فراموشی پسورد رو انتخاب کنین. ببخشید که فرم ذخیره نشده. درست می شه'} #TODO: forgot password
            #TODO: keep the form data
            return render(request, 'register.html', context)

        if not User.objects.filter(username = request.POST['username']).exists(): #if user does not exists
                code = random_str(28)
                now = datetime.now()
                email = request.POST['email']
                password = make_password(request.POST['password'])
                username = request.POST['username']
                temporarycode = Passwordresetcodes (email = email, time = now, code = code, username=username, password=password)
                temporarycode.save()
                message = PMMail(api_key = settings.POSTMARK_API_TOKEN,
                                 subject = "activating Bestoon account",
                                 sender = "babelian_mahan@ee.sharif.ir",
                                 to = email,
                                 text_body = "click the link below to activate your account: http://127.0.0.1:9000/accounts/register/?email={}&code={}".format(email, code),
                                 tag = "account request")
                message.send()
                context = {'message': 'click the activation link thats been sent to your email address'}
                return render(request, 'login.html', context)
        else:
            context = {'message': 'this username has been used before, try a new one'} #TODO: forgot password
            #TODO: keep the form data
            return render(request, 'register.html', context)
    elif request.GET.has_key('code'): # user clicked on code
        email = request.GET['email']
        code = request.GET['code']
        if Passwordresetcodes.objects.filter(code=code).exists(): #if code is in temporary db, read the data and create the user
            new_temp_user = Passwordresetcodes.objects.get(code=code)
            newuser = User.objects.create(username=new_temp_user.username, password=new_temp_user.password, email=email)
            this_token = random_str(48)
            token = Token.objects.create(user=newuser, token=this_token)
            Passwordresetcodes.objects.filter(code=code).delete() #delete the temporary activation code from db
            context = {'message': 'BRAVO! activated, your token is : {}'.format(this_token)}
            return render(request, 'login.html', context)
        else:
            context = {'message': 'activation code expired, try a new one'}
            return render(request, 'login.html', context)
    else:
        context = {'message': ''}
        return render(request, 'register.html', context)





@csrf_exempt
def submit_expense(request):
    """user submits an expense"""
    #TODO; validate data, user migfht be fake, token might be fake, amount..
    this_token = request.POST['token']
    this_user = User.objects.filter(token__token= this_token).get()
    if 'date' not in request.POST:
        date = datetime.now()
    now =datetime.now()
    Expense.objects.create(user = this_user, amount = request.POST['amount']
            , text = request.POST['text'],date = now)
    return JsonResponse({
        'status' : 'ok'
    }, encoder=JSONEncoder)

@csrf_exempt
def submit_income(request):
    """user submits an income"""

    #TODO; validate data, user migfht be fake, token might be fake, amount..
    this_token = request.POST['token']
    this_user = User.objects.filter(token__token= this_token).get()
    if 'date' not in request.POST:
        date = datetime.now()
    now =datetime.now()
    Income.objects.create(user = this_user, amount = request.POST['amount']
            , text = request.POST['text'],date = now)

    return JsonResponse({
        'status' : 'ok'
    }, encoder=JSONEncoder)
