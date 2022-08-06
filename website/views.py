from allauth.account.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

import datetime
import hashlib
import io
import json
import random
import os

from PIL import Image

from django.shortcuts import render, redirect
import check_permission
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.core.files.storage import FileSystemStorage
from django.forms.models import model_to_dict
from bson import ObjectId
from django.core import serializers

import website.models
from .forms import *
from .models import *
import json
import urllib.request
import urllib
import uuid
import requests
import hmac
import hashlib

from mtnmomo.collection import Collection
from ad.models import *
from .models import room as model_room
from .models import history_bidding as model_his
from .models import product as model_product
from .models import chat_room as model_chat_room
from .models import acc as model_acc
# Create your views here.

from website.models import *
import threading
from datetime import timedelta
from time import sleep


class HomeView(LoginView):
    template_name = "two_app/index.html"


class ShopLogin(LoginView):
    template_name = 'two_app/shop-login.html'


class CustomerLogin(LoginView):
    template_name = 'two_app/customer-login.html'


@login_required
def shopProfile(request, username):
    user = CSUser.objects.get(username=username)

    if Shop.objects.filter(user__username=username).exists():
        text = Shop.objects.filter(user__username=username).values_list('description', flat=True).get()
    else:
        text = Shop.objects.create(user=user, description="First Comment")
        text = text.description
    context = {
        'user': user,
        'text': 'shopppp'
    }
    template = "two_app/shop-profile.html"
    return render(request, template, context)


@login_required
def customerProfile(request, username):
    user = CSUser.objects.get(username=username)

    if Customer.objects.filter(user__username=username).exists():
        text = Customer.objects.filter(user__username=username).values_list('description', flat=True).get()
    else:
        text = Customer.objects.create(user=user, description="First Comment")
        text = text.description

    context = {
        'user': user,
        'text': text
    }
    template = "two_app/customer-profile.html"
    return render(request, template, context)

def register_form(request):
    form = SignupForm
    return render(request, 'website/sigup_form.html', {'form': form})

def registration(request):
    form = SignupForm
    message = ''
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        usr = request.POST.get('id')
        pwd = request.POST.get('password')
        pwd = hashlib.sha1(bytes(pwd, 'utf-8'))
        pwd = pwd.hexdigest()
        auth_pwd = request.POST.get('auth_password')
        auth_pwd = hashlib.sha1(bytes(auth_pwd, 'utf-8'))
        auth_pwd = auth_pwd.hexdigest()
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        district = request.POST.get('district')

        if pwd == auth_pwd:

            print(request.POST)
            user = account.objects.filter(pk=usr).first()
            if not user:
                form = SignupForm(request.POST)
                print(form.errors)
                if form.is_valid():
                    acc = form.save(commit=False)
                    acc.password = pwd
                    acc.role = 'user'
                    # acc.status = 'active'
                    if account.objects.filter(email=email).exists():
                        message = 'Email đã được sử dụng!'
                    else:
                        acc.save()
                        c_r = chat_room(host='admin', user=usr)
                        c_r.save()
                        return redirect('/')
                else:
                    message = 'Email không hợp lệ!'
            else:
                message = 'Thao tác thất bại!'

        else:
            message = 'Mật khẩu xác nhận không chính xác!'
        return render(request, 'website/sigup_form.html', {'form': form, 'message': message})
    else:
        return render(request, 'website/sigup_form.html', {'form': form})




@csrf_exempt
def login(request):
    form = AccountForm
    try:
        acc = account.objects(pk=request.session['auction_account'].get('username'),
                                     password=request.session['auction_account'].get('password'),
                                     role='user').first()
        if check_permission.permission(request, acc, 'user') == 'user' and acc.status == 'active':
            return redirect("/usr/0/information")
        else:
            del request.session['auction_account']
            return render(request, 'website/login_form.html', {'form': form})
    except:
        if request.is_ajax and request.method == "POST":
            # get the form data
            form = AccountForm(request.POST)
            if form.is_valid():
                Account = form.cleaned_data['account']
                password = form.cleaned_data['password']
                password = hashlib.sha1(bytes(password, 'utf-8'))
                password = password.hexdigest()
                print('TTTTTT')
                acc = account.objects(pk=Account, password=password, role='user').first()
                if acc:
                    if acc.status == 'active':
                        # my_image = open(r'C:\Users\ADMIN\Pictures\Screenshots\agg.png', 'rb')
                        # acc.image.replace(my_image, filename="conny.jpg")
                        # acc.save()
                        # print(acc.image.url)
                        kq = 1
                        request.session['auction_account'] = {'username': acc.pk, 'password': acc.password,
                                                              'role': 'user'}
                        print(request.session['auction_account'])
                    else:
                        kq = 'redirect'

                else:
                    kq = '0'
                return JsonResponse({"kq": kq}, status=200)
            else:
                # some form errors occured.
                return JsonResponse({"error": form.errors}, status=400)
        return render(request, 'website/login_form.html', {'form': form})

def change_password_form(request):
    form = ChangePaswordForm
    return render(request, 'website/change_password_form.html', {'form': form})

@csrf_exempt
def changepwd(request):
    try:
        usr = request.session['auction_account']['username']
        acc = account.objects(pk=usr).first()
        if check_permission.permission(request, acc, 'user') == 'user':
            if request.is_ajax and request.method == "POST":
                # get the form data
                form = ChangePaswordForm(request.POST)
                if form.is_valid():
                    OldPwd = form.cleaned_data['OldPassword']
                    OldPwd = hashlib.sha1(bytes(OldPwd, 'utf-8'))
                    OldPwd = OldPwd.hexdigest()
                    NewPwd = form.cleaned_data['NewPassword']
                    NewPwd = hashlib.sha1(bytes(NewPwd, 'utf-8'))
                    NewPwd = NewPwd.hexdigest()
                    AuthPwd = form.cleaned_data['AuthPassword']
                    AuthPwd = hashlib.sha1(bytes(AuthPwd, 'utf-8'))
                    AuthPwd = AuthPwd.hexdigest()
                    if OldPwd == acc.password:
                        if NewPwd == AuthPwd:
                            # d033e22ae348aeb5660fc2140aec35850c4da997
                            account.objects(pk=usr).update(__raw__={'$set': {'password': NewPwd}})
                            # acc.save()
                            message = 1
                            print(message)
                        else:
                            message = 'Mật khẩu xác nhận không chính xác!'
                    else:
                        message = 'Mật khẩu hiện tại không chính xác!'
                    # print(message)
                    return JsonResponse({"message": message}, status=200)
            else:
                return JsonResponse({"error": ''}, status=400)
        else:
            return JsonResponse({"message": 'Vui lòng đăng nhập!'}, status=200)
    except KeyError:
        return redirect('/')


def information(request):
    try:
        acc = account.objects.filter(pk=request.session['auction_account']['username'],
                                            password=request.session['auction_account']['password'],
                                            role='user').first()
        if check_permission.permission(request, acc, 'user') == 'user':
            img_url = None
            form = SignupForm
            # u = user.to_mongo()
            u = acc.to_json()
            if acc.img_url != "":
                img_url = acc.img_url

            # with open(r'C:\Users\ADMIN\Pictures\Screenshots\agg.png', 'rb') as fd:
            #     a.image.put(fd, content_type='image/png')
            # a.save()
            # photo = a.image.read()
            # content_type = a.image.content_type
            return render(request, 'website/information.html', {'form': form,
                                                                'user': u, 'img_url': img_url,
                                                                "username": request.session['auction_account'][
                                                                    'username']})
        else:
            return redirect("/")
    except KeyError:
        return redirect("/")


@csrf_exempt
def usr_logout(request):
    try:
        usr = request.session['auction_account']['username']
        pwd = request.session['auction_account']['password']
        rl = request.session['auction_account']['role']
        if usr != None and pwd != None and rl != None:
        # request.session.modified = True
            del request.session['auction_account']
            # request.session['auction_account'] = {'username': None, 'password': None, 'role': None}
        return redirect('/')
    except:
        return redirect('/')


@csrf_exempt
def update(request):
    if request.is_ajax and request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        img = request.FILES.get('image')
        email = request.POST['email']
        phonenb = request.POST['phonenb']
        address = request.POST['address']
        district = request.POST['district']
        city = request.POST['city']
        fs = FileSystemStorage()
        url = ''
        if img is not None:
            name = fs.save(img.name, img)
            url = fs.url(name)
        account.objects(pk=request.session['auction_account']['username']).update(__raw__={'$set': {'img_url': url, 'email':email, 'phonenb': phonenb, 'address': address, 'city':city, 'district': district, 'img_url': url}})
        return JsonResponse({"error": ''}, status=200)
    return redirect("/usr/0/information")

def home(request):
    try:
        usr = request.session['auction_account']['username']
        cate = category.objects()
        rm = room.objects()
        for r in rm:
            print(r.status)
        return render(request, 'website/room.html', {'cate': cate, 'room': rm, 'username': usr})
    except KeyError:
        return redirect('/')



def product(request):
    try:
        acc = account.objects(pk=request.session['auction_account'].get('username'),
                              password=request.session['auction_account'].get('password'),
                              role='user').first()
        if check_permission.permission(request, acc, 'user') == 'user':
            l = 3
            form = ProductForm(l)
            prd_att = ProductAttributesForm
            c = category.objects()
            cate = c.to_json()
            print(cate)
            if request.method == "POST":
                if request.is_ajax:
                    u = acc.to_json()
                    form = ProductForm(l, request.POST)
                    if form.is_valid():
                        category_id = form.cleaned_data['category']
                        print(category_id)
                        return JsonResponse({"message": category_id}, status=200)
                return render(request, 'website/detail_product.html',
                              {'form': form, 'user': u,'username':request.session['auction_account']['username'], 'prd_att': prd_att, 'cate': cate, 'c': c})
            else:
                return render(request, 'website/category_select.html', {'form': form, 'username':request.session['auction_account']['username']})

    except:
        return redirect('/')


def detail_product_form(request):
    if request.method == "POST":
        form = ProductForm
        return render(request, 'website/detail_product.html', {'form': form})
    return redirect("/seller/get_category")


def get_category(request):
    message = 'Lỗi!'
    if request.is_ajax and request.method == "POST":
        id = request.POST['id']
        category_list = category.objects.filter(id=id).first()
        d = category_list.attributes_id
        ls = []
        for item in d:
            item = model_to_dict(item)
            item['attribute_groups_id'] = model_to_dict(item['attribute_groups_id'])
            ls.append(item)
        print(ls)
        return JsonResponse({"message": ls}, status=200)
    return redirect('/')


def countdown(id, timer):
    global my_timer
    my_timer = timer
    kq = True
    while kq:
        print('----phong---'+ str(id) +'-----')
        print(timer)
        timer -= 1
        if timer < 0:
            kq = False

        time.sleep(1)
    countdown_thread = threading.Thread(target=countdown(id, 10))
    countdown_thread.start()
    print('chay custom timer thanh cong!')
    return JsonResponse({"message": ''}, status=200)

def custom_countdown(id, timer):
    print()
    countdown_thread = threading.Thread(target=countdown(id, 10))
    countdown_thread.start()
    print('chay custom timer thanh cong!')
    return JsonResponse({"message": ''}, status=200)

def save_product(request):
    usr = request.session['auction_account']['username']
    if request.is_ajax and request.method == "POST":
        form = ProductForm(3, request.POST, request.FILES)
        print(request.POST)
        if form.is_valid():
            category_id = form.cleaned_data['category']
            name = form.cleaned_data['name']
            c = category.objects(id=category_id).first()
            l = website.models.room.objects(seller_id=usr)
            check = 0
            for i in l:
                if str(i.product_id.name) == str(name) and str(i.product_id.category.pk) == str(category_id):
                    check = check + 1
                    break
            if check > 0:
                message = 'Thao tác không thành công do bạn có một sản phẩm tương tự đang được đăng bán.'
            else:
                f = form.save(commit=False)
                f.category = c
                f.startingbid = float(request.POST['startingbid'])
                f.seller = account.objects(pk=request.session['auction_account']['username']).first()
                p_id = f.save()

                for i in range(0, len(request.POST.getlist("content"))):
                    form_attr = ProductAttributesForm(request.POST)
                    print(request.POST)
                    form_attr = form_attr.save(commit=False)
                    form_attr.product_id = model_product.objects(id=ObjectId(p_id.id)).first()
                    form_attr.attributes = attributes.objects(id=request.POST.getlist('attributes')[i]).first()
                    form_attr.content = request.POST.getlist("content")[i]
                    form_attr.save()

                p = model_product.objects(id=ObjectId(p_id.id)).first()
                days = p.duration.split(" day")
                timestamp = str(datetime.datetime.now())
                timestamp = timestamp[:len(timestamp) - 7]
                print(timestamp)

                end = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(days=int(days[0]))

                room = model_room(product_id=model_product.objects(id=ObjectId(p_id.id)).first(), total=0,
                                  start=datetime.datetime.now(), end=end,
                                  seller_id=account.objects(pk=request.session['auction_account']['username']).first(),
                                  quantity_of_bidder=0, highestbidder=account.objects(
                        pk=request.session['auction_account']['username']).first(),
                                  current_bid=request.POST['startingbid'], status='opening',
                                  winner=[], highestbidder_bid=0.0)
                now = round(time.time() * 1000)
                print(now)
                end = end.timestamp() * 1000
                print(end)

                t = end - now
                # t > 0
                # phong dang mo
                # t < 0
                # phong da dong
                print('interval ' + str(t))
                id_room = room.save()

                # countdown_thread = threading.Thread(target=countdown(id_room.id, 10))
                # countdown_thread.start()
                message = ''

            return JsonResponse({"message": message}, status=200)
    return redirect('/home')



def get_balance(request):
    # # parameters send to MoMo get get payUrl
    # endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    # partnerCode = "MOMO"
    # accessKey = "F8BBA842ECF85"
    # secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    # orderInfo = "pay with MoMo"
    # redirectUrl = "http://127.0.0.1:8000/vd"
    # ipnUrl = "http://127.0.0.1:8000/vd"
    # amount = "50000"
    # orderId = str(uuid.uuid4())
    # requestId = str(uuid.uuid4())
    # requestType = "captureWallet"
    # extraData = ""  # pass empty value or Encode base64 JsonString
    #
    # # before sign HMAC SHA256 with format: accessKey=$accessKey&amount=$amount&extraData=$extraData&ipnUrl=$ipnUrl
    # # &orderId=$orderId&orderInfo=$orderInfo&partnerCode=$partnerCode&redirectUrl=$redirectUrl&requestId=$requestId
    # # &requestType=$requestType
    # rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl + "&requestId=" + requestId + "&requestType=" + requestType
    #
    # # puts raw signature
    # print("--------------------RAW SIGNATURE----------------")
    # print(rawSignature)
    # # signature
    # h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
    # signature = h.hexdigest()
    # print("--------------------SIGNATURE----------------")
    # print(signature)
    #
    # # json object send to MoMo endpoint
    #
    # data = {
    #     'partnerCode': partnerCode,
    #     'partnerName': "Test",
    #     'storeId': "MomoTestStore",
    #     'requestId': requestId,
    #     'amount': amount,
    #     'orderId': orderId,
    #     'orderInfo': orderInfo,
    #     'redirectUrl': redirectUrl,
    #     'ipnUrl': ipnUrl,
    #     'lang': "vi",
    #     'extraData': extraData,
    #     'requestType': requestType,
    #     'signature': signature
    # }
    # print("--------------------JSON REQUEST----------------\n")
    # data = json.dumps(data)
    # print(data)
    #
    # clen = len(data)
    # response = requests.post(endpoint, data=data,
    #                          headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
    #
    # # f.close()
    # print("--------------------JSON response----------------\n")
    # print(response.json())
    #
    # print(response.json()['payUrl'])

    config = {
        "ENVIRONMENT": 'sandbox',
        "BASE_URL": 'https://sandbox.momodeveloper.mtn.com',
        "CALLBACK_HOST": "https://webhook.site/6a073522-a7f0-475a-8c1c-cdbf4c527804",  # Mandatory.
        "COLLECTION_PRIMARY_KEY": '7d88edbf173f4f2a9d28a7fa7d5d09a5',
        "COLLECTION_USER_ID": 'cffad568-c3c0-4194-ad23-67fb1fb6a15b',
        "COLLECTION_API_SECRET": 'e197ad12de104901bf531fdbc8503759',
    }

    client = Collection({
        "ENVIRONMENT": 'sandbox',
        "BASE_URL": 'https://sandbox.momodeveloper.mtn.com',
        "CALLBACK_HOST": "https://webhook.site/6a073522-a7f0-475a-8c1c-cdbf4c527804",  # Mandatory.
        "COLLECTION_PRIMARY_KEY": '7d88edbf173f4f2a9d28a7fa7d5d09a5',
        "COLLECTION_USER_ID": '8ccc8c75-6508-41df-acba-310390d39dd0',
        "COLLECTION_API_SECRET": '7cb763e6f46a4025904e5da8ccf0f38b',
    })
    y = client.requestToPay(
       mobile="256782181656", amount="600", external_id="111", payee_note="dd", payer_message="dd", currency="EUR")
    t = client.getBalance()
    print(t)

    # import http.client, urllib.request, urllib.parse, urllib.error, base64
    # #
    # headers = {
    #     # Request headers
    #     'Authorization': '',
    #     'X-Target-Environment': 'sandbox',
    #     'Ocp-Apim-Subscription-Key': '7d88edbf173f4f2a9d28a7fa7d5d09a5',
    # }
    #
    # params = urllib.parse.urlencode({
    # })
    #
    # try:
    #     conn = http.client.HTTPSConnection('sandbox.momodeveloper.mtn.com')
    #     conn.request("GET", "/collection/v1_0/account/balance?%s" % params, "{body}", headers)
    #     response = conn.getresponse()
    #     data = response.read()
    #     print('sjkskjskjs')
    #     print(data)
    #     conn.close()
    # except Exception as e:
    #     print("[Errno {0}] {1}".format(e.errno, e.strerror))

    return HttpResponse('hello')

def thanhtoan_momo(request, room_id):
    try:
        usr = request.session['auction_account']['username']
        # parameters send to MoMo get get payUrl
        # endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
        # partnerCode = "MOMO"
        # accessKey = "F8BBA842ECF85"
        # secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
        # orderInfo = "pay with MoMo"
        # redirectUrl = "https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b"
        # ipnUrl = "https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b"
        # amount = "50000"
        # orderId = str(uuid.uuid4())
        # requestId = str(uuid.uuid4())
        # requestType = "captureWallet"
        # extraData = ""  # pass empty value or Encode base64 JsonString, rô
        ord = website.models.order.objects(room_id=ObjectId(room_id)).first()
        print(ord.total)
        endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
        # endpoint = 'https://test-payment.momo.vn/v2/gateway/api/query'

        # accessKey = "F8BBA842ECF85"
        # secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
        # partnerCode = "MOMO"
        partnerCode = 'MOMOBKUN20180529'
        accessKey = 'klm05TvNBzhg7h7j'
        secretKey = 'at67qH6mk8w5Y1nAyMoYKMWACiEi2bsa'
        orderInfo = "Thanh toán qua MoMo"
        amount = str(int(ord.total))
        orderId = str(uuid.uuid4())
        redirectUrl = "http://127.0.0.1:8000/usr/0/information"
        ipnUrl = 'http://127.0.0.1:8000/vd'
        extraData = ""
        requestId = str(uuid.uuid4())
        requestType = 'payWithATM'

        # before sign HMAC SHA256 with format: accessKey=$accessKey&amount=$amount&extraData=$extraData&ipnUrl=$ipnUrl
        # &orderId=$orderId&orderInfo=$orderInfo&partnerCode=$partnerCode&redirectUrl=$redirectUrl&requestId=$requestId
        # &requestType=$requestType

        rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl + "&requestId=" + requestId + "&requestType=" + requestType
        # puts raw signature
        print("--------------------RAW SIGNATURE----------------")
        print(rawSignature)
        # signature
        h = hmac.new(bytes(secretKey, 'utf-8'), bytes(rawSignature, 'utf-8'), hashlib.sha256)
        signature = h.hexdigest()
        print("--------------------SIGNATURE----------------")
        print(signature)

        # json object send to MoMo endpoint

        data = {
            'partnerCode': partnerCode,
            'partnerName': "Test",
            'storeId': 'MomoTestStore',
            'requestId': requestId,
            'amount': amount,
            'orderId': orderId,
            'orderInfo': orderInfo,
            'redirectUrl': redirectUrl,
            'ipnUrl': ipnUrl,
            'lang': 'vi',
            # 'autoCapture': autoCapture,
            'extraData': extraData,
            # 'paymentCode': paymentCode,
            # 'orderGroupId': orderGroupId,
            'requestType': requestType,
            'signature': signature
        }

        print("--------------------JSON REQUEST----------------\n")
        #     data = {
        #     "partnerCode": "123456",
        #     "requestId": "1527246504579",
        #     "orderId": "1527246478428",
        #     "signature": "13be80957a5ee32107198920fa26aa85a4ca238a29f46e292e8c33dd9186142a",
        #     "lang": "en"
        # }
        data = json.dumps(data)
        print(data)

        clen = len(data)
        response = requests.post(endpoint, data=data,
                                 headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})

        # f.close()
        print("--------------------JSON response----------------\n")
        print(response.json())

        payUrl = response.json()['payUrl']
        website.models.order.objects(room_id=ObjectId(room_id)).update(payURL=payUrl)
        return redirect(payUrl)
    except KeyError:
        redirect('/')


def vd(request):
    return render(request, 'vd.html')

def room_detail(request, id):
    try:
        usr = request.session['auction_account']['username']
        room = model_room.objects(id=ObjectId(id)).first()
        pr_att = product_attributes.objects(product_id=ObjectId(room.product_id.id))

        try:
            bidder_id = request.session['auction_account'].get('username')

        except KeyError:
            bidder_id = ''
            usr = ''
        h = model_his.objects(room_id=ObjectId(id),
                              bidder_id=bidder_id)
        count = h.count()
        # print(count)
        try:
            history_bidding = h[count - 1]
        except IndexError:
            history_bidding = 0
        # print('checkseller'+ usr)
        return render(request, 'website/room_detail.html',
                      {'username': usr, 'room': room, 'pr_att': pr_att, 'hs_bidding': history_bidding,
                       'check_seller': usr})
    except KeyError:
        return redirect('/')


def get_auction_bid(current_price, currency):
    bid_increment = 0
    currency = float(currency)
    if (0.01 * currency) <= current_price or current_price <= (0.99 * currency):
        bid_increment = 0.05 * currency
    elif (0.1 * currency) <= current_price or current_price <= (4.99 * currency):
        bid_increment = 0.025 * currency
    elif (5.0 * currency) <= current_price or current_price <= (24.99 * currency):
        bid_increment = 0.5 * currency
    elif (25.00 * currency) <= current_price or current_price <= (99.99 * currency):
        bid_increment = 1.0 * currency
    elif (100.00 * currency) <= current_price or current_price <= (249.99 * currency):
        bid_increment = 2.50 * currency
    elif (250.00 * currency) <= current_price or current_price <= (499.99 * currency):
        bid_increment = 5.00 * currency
    elif (500.00 * currency) <= current_price or current_price <= (999.99 * currency):
        bid_increment = 10.00 * currency
    elif (1000.00 * currency) <= current_price or current_price <= (2499.99 * currency):
        bid_increment = 25.00 * currency
    elif (2500.00 * currency) <= current_price or current_price <= (4999.99 * currency):
        bid_increment = 50.00 * currency
    elif (5000.00 * currency) <= current_price:
        bid_increment = 100.00 * currency
    return bid_increment


@csrf_exempt
def bid(request):
    message = 'Lỗi!'
    if request.is_ajax and request.method == "POST":
        try:
            bidder = request.session['auction_account']['username']
        except KeyError:
            bidder = ''
        if bidder is None:
            return JsonResponse({"message": 'Lỗi!'}, status=200)
        bids = float(request.POST['bids'])
        print(bids)
        id = request.POST['id']
        room = model_room.objects(id=ObjectId(id)).first()
        exists = 0
        h = history_bidding.objects(room_id=ObjectId(id))
        for i in h:
            if i.bidder_id.pk == bidder:
                exists = exists + 1
                break
        if exists == 0:
            q = room.quantity_of_bidder + 1
            model_room.objects(id=ObjectId(id)).update(quantity_of_bidder=q)

        r_hb = room.highestbidder

        if room.highestbidder_bid == 0:
            message = 'Bạn đã trở thành người đặt giá cao nhất!'
            behb = 1
            hb_color = 'green'
            model_room.objects(id=ObjectId(id)).update(
                highestbidder=account.objects(pk=bidder).first(),
                highestbidder_bid=bids)
            history = model_his(bidder_id=bidder, room_id=room, bids=bids)
            history.save()
            rm = website.models.room.objects(id=ObjectId(id)).first()
            gtt = rm.highestbidder_bid + get_auction_bid(rm.highestbidder_bid, 23000)
        else:
            if bids >= (room.current_bid + get_auction_bid(room.current_bid, 23000)):
                if bidder == r_hb.pk:
                    if bids >= (room.highestbidder_bid + get_auction_bid(room.highestbidder_bid, 23000)):
                        model_room.objects(id=ObjectId(id)).update(highestbidder_bid=bids)
                        history = history_bidding(bidder_id=bidder, room_id=room, bids=bids)
                        history.save()
                        message = 'Bạn đang là người đặt cao nhất. Bạn đã tăng giá tối đa thành công!'
                        behb = 1
                        hb_color = 'green'
                        rm = website.models.room.objects(id=ObjectId(id)).first()
                        gtt = rm.highestbidder_bid + get_auction_bid(rm.highestbidder_bid, 23000)
                    else:
                        message = 'Người đặt cao nhất không thể hạ giá bid tối đa đã đặt hoặc giá tiền không hợp lệ!'
                        behb = 1
                        hb_color = 'green'
                        rm = website.models.room.objects(id=ObjectId(id)).first()
                        gtt = rm.highestbidder_bid + get_auction_bid(rm.highestbidder_bid, 23000)
                else:
                    behb = 0
                    hb_color = 'red'
                    rm = website.models.room.objects(id=ObjectId(id)).first()
                    gtt = rm.current_bid + get_auction_bid(room.highestbidder_bid, 23000)
                    if bids > room.highestbidder_bid:
                        # change hb and hb_bid
                        # new bidder becomes hb
                        if (room.highestbidder_bid == 0):
                            rm = website.models.room.objects(id=ObjectId(id)).first()
                            gtt = rm.current_bid + get_auction_bid(rm.current_bid, 23000)
                            model_room.objects(id=ObjectId(id)).update(
                                current_bid=float(room.current_bid + get_auction_bid(room.current_bid, 23000)),
                                highestbidder=account.objects(pk=bidder).first(),
                                highestbidder_bid=bids)
                            history = model_his(bidder_id=bidder, room_id=room, bids=bids)
                            history.save()
                        else:
                            rm = website.models.room.objects(id=ObjectId(id)).first()
                            gtt = rm.highestbidder_bid + get_auction_bid(rm.highestbidder_bid, 23000)
                            model_room.objects(id=ObjectId(id)).update(
                                current_bid=float(
                                    room.highestbidder_bid + get_auction_bid(room.highestbidder_bid, 23000)),
                                highestbidder=account.objects(pk=bidder).first(),
                                highestbidder_bid=bids)
                            history = model_his(bidder_id=bidder, room_id=room, bids=bids)
                            history.save()
                        message = 'Bạn đã trở thành người đặt giá cao nhất!'
                        behb = 1
                        hb_color = 'green'

                    elif bids == room.highestbidder_bid:
                        # new bidder don't becomes hb, current_bid = new bid and hb, but new bidder outbid and hb not
                        model_room.objects(id=ObjectId(id)).update(
                            current_bid=float(room.highestbidder_bid))
                        history = model_his(bidder_id=bidder, room_id=room, bids=bids)
                        history.save()
                        if bidder == room.highestbidder.id:
                            message = 'Bạn vẫn đang là người đặt giá cao nhất!'
                            behb = 1
                            hb_color = 'red'
                            rm = website.models.room.objects(id=ObjectId(id)).first()
                            gtt = rm.highestbidder_bid + get_auction_bid(rm.highestbidder_bid, 23000)
                        else:
                            message = 'Bạn đang bị trả giá cao hơn!'
                            behb = 0
                            hb_color = 'red'
                            rm = website.models.room.objects(id=ObjectId(id)).first()
                            gtt = rm.current_bid + get_auction_bid(room.highestbidder_bid, 23000)
                    else:
                        # new bidder not hb
                        message = 'Bạn đang bị vượt giá!'
                        # auto bid for hb
                        auto_bidding(id, bids, bidder)
                        behb = 0
                        hb_color = 'red'
                        rm = website.models.room.objects(id=ObjectId(id)).first()
                        gtt = rm.current_bid + get_auction_bid(room.highestbidder_bid, 23000)

            else:
                if bidder == r_hb.pk:
                    behb = 1
                    hb_color = 'green'
                    rm = website.models.room.objects(id=ObjectId(id)).first()
                    gtt = rm.highestbidder_bid + get_auction_bid(rm.highestbidder_bid, 23000)
                else:
                    behb = 0
                    hb_color = 'red'
                    rm = website.models.room.objects(id=ObjectId(id)).first()
                    gtt = rm.current_bid + get_auction_bid(room.highestbidder_bid, 23000)
                message = 'Giá tiền phải từ ' + str(
                    int(room.current_bid + get_auction_bid(room.current_bid, 23000))) + 'đ trở lên!'

        return JsonResponse({"message": message, 'behb': behb, 'gtt':gtt, 'hb_color': hb_color}, status=200)
    return redirect('/')



def auto_bidding(id_room, bid, bidder):
    new_current_bid = bid + get_auction_bid(bid, 23000)
    model_room.objects(id=ObjectId(id_room)).update(current_bid=new_current_bid)
    history = model_his(bidder_id=bidder, room_id = model_room.objects(id=ObjectId(id_room)).first(), bids=bid)
    history.save()


@csrf_exempt
def get_next_bids(request):
    if request.is_ajax and request.method == "POST":
        print(request.POST)
        try:
            bidder = request.session['auction_account']['username']
        except KeyError:
            bidder = ''
        id_room = request.POST['id_room']
        r = model_room.objects(id=ObjectId(id_room)).first()
        try:
            room_hb = r.highestbidder.id
        except:
            room_hb = ''
        if bidder == room_hb:
            hb = 'Bạn đang là người đặt giá cao nhất!'
            color = 'green'
            result = r.highestbidder_bid + get_auction_bid(r.highestbidder_bid, 23000)
        else:
            hb = 'Bạn đang bị trả giá cao hơn!'
            color = 'red'
            current_price = r.current_bid
            result = current_price + get_auction_bid(current_price, 23000)
        # try:
        #     room_hb = r.highestbidder.id
        #     if bidder == room_hb:
        #         hb = 'Bạn đang là người đặt giá cao nhất!'
        #         color = 'green'
        #         result = r.highestbidder_bid + get_auction_bid(r.highestbidder_bid, 23000)
        #     else:
        #         hb = 'Bạn đang bị trả giá cao hơn!'
        #         color = 'red'
        #         current_price = r.current_bid
        #         result = current_price + get_auction_bid(current_price, 23000)
        # except:
        #     hb = ''
        #     color = ''
        #     print(r.current_bid)
        #     result = r.current_bid + get_auction_bid(r.current_bid, 23000)
        return JsonResponse({"message": result, 'hb': hb, 'hb_color': color}, status=200)
    return redirect('/')

@csrf_exempt
def set_status_room(request):
    if request.is_ajax and request.method == "POST":
        id_room = request.POST['id_room']
        usr = request.session['auction_account']['username']
        print('dnkdldkdldkd')
        print(id_room)
        r = model_room.objects(id=ObjectId(id_room)).first()
        h = model_his.objects(room_id=ObjectId(id_room),
                              bidder_id=usr)
        count = h.count()
        total = r.current_bid
        try:
            hb = r.highestbidder.id
        except:
            hb = ''
        if hb == usr:
            kq = 1
            if r.highestbidder_bid < total:
                total = r.highestbidder_bid
        else:
            kq = 0
        model_room.objects(id=ObjectId(id_room)).update(status='closed')
        print('___________TOTAL__________')
        print(total)
        return JsonResponse({"message": 'Cập nhật status thành công!', 'kq':kq}, status=200)
    return redirect('/')


def history_bidding_list(request):
    try:
        usr = request.session['auction_account']['username']
        r = history_bidding.objects.aggregate([
            {"$match": {"bidder_id": usr}},
            {'$group': {'_id': '$room_id'}}])
        ls = []
        for t in r:
            h = history_bidding.objects(room_id=ObjectId(t['_id'])).first()
            ls.append(h)
        return render(request, 'website/history_bidding_list.html', {'username': usr, 'room': ls})
    except KeyError:
        return redirect('/')

def bidding_room(request, room_id):
    try:
       usr = request.session['auction_account']['username']
       r = history_bidding.objects(bidder_id=usr, room_id=room_id)
       return render(request, 'website/bidding_room.html', {'username': usr, 'room': r, 'room_id': room_id})
    except KeyError:
        return redirect('/')

@csrf_exempt
def cancel_bid(request):
    if request.is_ajax and request.method == "POST":
        room_id = request.POST['room_id']
        print(room_id)
        reason = request.POST['reason']
        his_bid = history_bidding.objects(room_id=ObjectId(room_id)).latest('time')
        room_id = his_bid.room_id
        print(room_id)
        time_bid = his_bid.time
        room_end = his_bid.room_id.end
        td = datetime.timedelta(hours=12)
        time = room_end - time_bid
        day = time.days
        hours = time.seconds // 3600
        minutes = (time.seconds // 60) % 60
        print(td)
        print(time)

        usr = request.session['auction_account']['username']
        print('Ban khong the huy gia')
        his = history_bidding.objects.filter(bidder_id=usr, room_id=room_id).order_by('time')  # ngay 01, ngay 02
        print('-------max time---------')
        max_time = history_bidding.objects(room_id=room_id).latest('time').time
        print(max_time)

        current_bidder = history_bidding.objects(room_id=room_id, time=max_time).first()
        print('-----------nguoi dat gan nhat---------')
        print(current_bidder.bidder_id.pk)
        print('-----------gia dat gan nhat----------')
        print(current_bidder.bids)
        nb = current_bidder.bidder_id.nb_bidcancel

        r = room.objects(pk=ObjectId(his_bid.room_id.pk)).first()
        if not bid_cancel.objects.filter(room_id=room_id, bidder=usr).exists():
            print(1100)
            if r.status == 'opening':
                print(1102)
                if time >= td:
                    print('Ban co the huy gia')
                    if current_bidder.pk == his_bid.pk:
                        bid_cl = bid_cancel(bidder=account.objects(pk=current_bidder.bidder_id.pk).first(),
                                            bidding_time=current_bidder.time,
                                            time_cancel=datetime.datetime.now(),
                                            room_id=room.objects(pk=room_id.pk).first(),
                                            cancel_account=account.objects(pk=usr).first(), reason=reason)
                        bid_cl.save()
                        history_bidding.objects.get(pk=current_bidder.pk).delete()
                        if nb > 1:
                            account.objects(pk=current_bidder.bidder_id.pk).update(
                                __raw__={'$set': {'status': 'blocked', 'nb_bidcancel': nb + 1}})
                            message = 'blocked'
                            if r.highestbidder.pk == usr:
                                print(1)
                                # tim hb tu cac usr con lai trong his_bidding cho room
                                if history_bidding.objects.filter(room_id=room_id.pk).exists():
                                    print('ffff')
                                    max_bid = history_bidding.objects.filter(room_id=room_id.pk).order_by('-bids')[0]
                                    if history_bidding.objects.filter(room_id=room_id.pk).count() > 1:
                                        near_max_bid = \
                                        history_bidding.objects.filter(room_id=room_id.pk).order_by('-bids')[
                                            1]
                                        print(22)
                                        print(near_max_bid.bids)
                                        cur_bid = near_max_bid.bids + get_auction_bid(near_max_bid.bids, 23000)
                                        room.objects(pk=ObjectId(room_id.pk)).update(
                                            __raw__={'$set': {'current_bid': cur_bid,
                                                              'highestbidder': max_bid.bidder_id.pk,
                                                              'highestbidder_bid': max_bid.bids}})
                                        print(33)
                                    else:
                                        r = room.objects(pk=ObjectId(room_id.pk)).first()
                                        room.objects(pk=ObjectId(room_id.pk)).update(
                                            __raw__={'$set': {'current_bid': r.product_id.startingbid,
                                                              'highestbidder': max_bid.bidder_id.pk,
                                                              'highestbidder_bid': max_bid.bids}})
                                else:
                                    print('Ban la nguoi dat dau tien')
                                    cur_bid = room.objects(pk=ObjectId(room_id.pk)).first()
                                    room.objects(pk=ObjectId(room_id.pk)).update(
                                        __raw__={'$set': {'current_bid': cur_bid.product_id.startingbid,
                                                          'highestbidder': cur_bid.seller_id.pk,
                                                          'highestbidder_bid': 0}})
                                    print(3)
                            else:
                                print('Bạn không phải người đặt giá cao nhất!')
                            return JsonResponse({"message": message}, status=200)
                        else:
                            if r.highestbidder.pk == usr:
                                print(1)
                                # tim hb tu cac usr con lai trong his_bidding cho room
                                if history_bidding.objects.filter(room_id=room_id.pk).exists():
                                    print('ffff')
                                    max_bid = history_bidding.objects.filter(room_id=room_id.pk).order_by('-bids')[0]
                                    if history_bidding.objects.filter(room_id=room_id.pk).count() > 1:
                                        near_max_bid = \
                                        history_bidding.objects.filter(room_id=room_id.pk).order_by('-bids')[
                                            1]
                                        print(22)
                                        print(near_max_bid.bids)
                                        cur_bid = near_max_bid.bids + get_auction_bid(near_max_bid.bids, 23000)
                                        room.objects(pk=ObjectId(room_id.pk)).update(
                                            __raw__={'$set': {'current_bid': cur_bid,
                                                              'highestbidder': max_bid.bidder_id.pk,
                                                              'highestbidder_bid': max_bid.bids}})
                                        print(33)
                                    else:
                                        r = room.objects(pk=ObjectId(room_id.pk)).first()
                                        room.objects(pk=ObjectId(room_id.pk)).update(
                                            __raw__={'$set': {'current_bid': r.product_id.startingbid,
                                                              'highestbidder': max_bid.bidder_id.pk,
                                                              'highestbidder_bid': max_bid.bids}})
                                else:
                                    print('Ban la nguoi dat dau tien')
                                    cur_bid = room.objects(pk=ObjectId(room_id.pk)).first()
                                    room.objects(pk=ObjectId(room_id.pk)).update(
                                        __raw__={'$set': {'current_bid': cur_bid.product_id.startingbid,
                                                          'highestbidder': cur_bid.seller_id.pk,
                                                          'highestbidder_bid': 0}})
                                    print(3)
                            else:
                                print('Bạn không phải người đặt giá cao nhất!')

                            message = ''
                    else:
                        print('Gia tien khong the huy')
                        message = 'Giá tiền hủy phải là giá gần nhất!'
                else:
                    print('-------lich su dat gia cu ban tai phong---------')
                    for i in his:
                        print(i.time)
                    if usr == current_bidder.bidder_id.pk:
                        print('..............Ban la nguoi dat gan nhat voi thgian')
                        print('room end:' + str(current_bidder.room_id.end))
                        print('gia dat gan nhat cua ban:' + str(current_bidder.time))
                        timdelta = room_end - current_bidder.time
                        print(timdelta)
                        one_hour = datetime.timedelta(hours=1)
                        print(one_hour)
                        if timdelta <= one_hour:
                            print('Ban la nguoi dat trong vong 1 tieng----->Co the huy bid')
                            bid_cl = bid_cancel(bidder=account.objects(pk=current_bidder.bidder_id.pk).first(),
                                                bidding_time=current_bidder.time,
                                                time_cancel=datetime.datetime.now(),
                                                room_id=room.objects(pk=room_id.pk).first(),
                                                cancel_account=account.objects(pk=usr).first(), reason=reason)
                            bid_cl.save()
                            history_bidding.objects.get(pk=current_bidder.pk).delete()
                            if nb > 1:
                                account.objects(pk=current_bidder.bidder_id.pk).update(
                                    __raw__={'$set': {'status': 'blocked', 'nb_bidcancel': nb + 1}})
                                message = 'blocked'
                                if r.highestbidder.pk == usr:
                                    print(1)
                                    # tim hb tu cac usr con lai trong his_bidding cho room
                                    if history_bidding.objects.filter(room_id=room_id.pk).exists():
                                        print('ffff')
                                        max_bid = history_bidding.objects.filter(room_id=room_id.pk).order_by('-bids')[
                                            0]
                                        if history_bidding.objects.filter(room_id=room_id.pk).count() > 1:
                                            near_max_bid = \
                                                history_bidding.objects.filter(room_id=room_id.pk).order_by('-bids')[
                                                    1]
                                            print(22)
                                            print(near_max_bid.bids)
                                            cur_bid = near_max_bid.bids + get_auction_bid(near_max_bid.bids, 23000)
                                            room.objects(pk=ObjectId(room_id.pk)).update(
                                                __raw__={'$set': {'current_bid': cur_bid,
                                                                  'highestbidder': max_bid.bidder_id.pk,
                                                                  'highestbidder_bid': max_bid.bids}})
                                            print(33)
                                        else:
                                            r = room.objects(pk=ObjectId(room_id.pk)).first()
                                            room.objects(pk=ObjectId(room_id.pk)).update(
                                                __raw__={'$set': {'current_bid': r.product_id.startingbid,
                                                                  'highestbidder': max_bid.bidder_id.pk,
                                                                  'highestbidder_bid': max_bid.bids}})
                                    else:
                                        print('Ban la nguoi dat dau tien')
                                        cur_bid = room.objects(pk=ObjectId(room_id.pk)).first()
                                        room.objects(pk=ObjectId(room_id.pk)).update(
                                            __raw__={'$set': {'current_bid': cur_bid.product_id.startingbid,
                                                              'highestbidder': cur_bid.seller_id.pk,
                                                              'highestbidder_bid': 0}})
                                        print(3)
                                else:
                                    print('Bạn không phải người đặt giá cao nhất!')
                                return JsonResponse({"message": message}, status=200)
                            else:
                                if r.highestbidder.pk == usr:
                                    print(1)
                                    # tim hb tu cac usr con lai trong his_bidding cho room
                                    if history_bidding.objects.filter(room_id=room_id.pk).exists():
                                        print('ffff')
                                        max_bid = history_bidding.objects.filter(room_id=room_id.pk).order_by('-bids')[
                                            0]
                                        if history_bidding.objects.filter(room_id=room_id.pk).count() > 1:
                                            near_max_bid = \
                                                history_bidding.objects.filter(room_id=room_id.pk).order_by('-bids')[
                                                    1]
                                            print(22)
                                            print(near_max_bid.bids)
                                            cur_bid = near_max_bid.bids + get_auction_bid(near_max_bid.bids, 23000)
                                            room.objects(pk=ObjectId(room_id.pk)).update(
                                                __raw__={'$set': {'current_bid': cur_bid,
                                                                  'highestbidder': max_bid.bidder_id.pk,
                                                                  'highestbidder_bid': max_bid.bids}})
                                            print(33)
                                        else:
                                            r = room.objects(pk=ObjectId(room_id.pk)).first()
                                            room.objects(pk=ObjectId(room_id.pk)).update(
                                                __raw__={'$set': {'current_bid': r.product_id.startingbid,
                                                                  'highestbidder': max_bid.bidder_id.pk,
                                                                  'highestbidder_bid': max_bid.bids}})
                                    else:
                                        print('Ban la nguoi dat dau tien')
                                        cur_bid = room.objects(pk=ObjectId(room_id.pk)).first()
                                        room.objects(pk=ObjectId(room_id.pk)).update(
                                            __raw__={'$set': {'current_bid': cur_bid.product_id.startingbid,
                                                              'highestbidder': cur_bid.seller_id.pk,
                                                              'highestbidder_bid': 0}})
                                        print(3)
                                else:
                                    print('Bạn không phải người đặt giá cao nhất!')

                                message = ''
                        else:
                            print('Ban khong phai nguoi dat trong 1 tieng')
                            message = 'Bạn không phải người đặt gần nhất trong 1h!'
                    else:
                        print('Ban khong phai nguoi dat gan nhat')
                        message = 'Bạn không phải người đặt gần nhất!'
            else:
                print(1224)
                message = 'Đã hết thời gian đấu giá!'
        else:
            print(1227)
            message = 'Bạn không thể hủy giá 2 lần trong cùng phòng đấu giá!'

        return JsonResponse({"message": message}, status=200)
    return redirect('/')


def find_cancel_bid_form(request):
    try:
        usr = request.session['auction_account']['username']
        return render(request, 'website/find_cancel_bid_form.html', {'username': usr})
    except KeyError:
        return redirect('/')

def seller_find_cancel_bid_form(request):
    try:
        usr = request.session['auction_account']['username']
        return render(request, 'website/seller_find_cancel_bid_form.html', {'username': usr})
    except KeyError:
        return redirect('/')

def load_product(request):
    try:
        usr = request.session['auction_account']['username']
        l = []
        ls = room.objects(highestbidder=usr)
        for i in ls:
            if i.seller_id.pk != usr:
                l.append(i)
        return render(request, 'website/list_product.html', {'username': usr, 'room': l})
    except KeyError:
        return redirect('/')

def seller_load_product(request):
    try:
        usr = request.session['auction_account']['username']
        ls = room.objects(seller_id=usr)
        return render(request, 'website/seller_list_product.html', {'username': usr, 'room': ls})
    except KeyError:
        return redirect('/')

def reason_form(request, room_id):
    try:
        usr = request.session['auction_account']['username']
        r = room.objects(pk=ObjectId(room_id)).first()
        return render(request, 'website/reason_form.html', {'username': usr, 'room': r})
    except KeyError:
        return redirect('/')

def seller_reason_form(request, room_id):
    try:
        usr = request.session['auction_account']['username']
        r = room.objects(pk=ObjectId(room_id)).first()
        return render(request, 'website/seller_reason_form.html', {'username': usr, 'room': r})
    except KeyError:
        return redirect('/')


@csrf_exempt
def confirm_form(request, room_id):
    try:
        usr = request.session['auction_account']['username']
        print(room_id)
        print(history_bidding.objects(bidder_id=usr, room_id=ObjectId(room_id)).first())
        his = history_bidding.objects(bidder_id=usr, room_id=ObjectId(room_id)).order_by('-bids')[0]
        if request.is_ajax and request.method == "POST":
            reason = request.POST['reason']
            return JsonResponse({"reason": reason}, status=200)
        return render(request, 'website/confirm_form.html', {'his': his})
    except KeyError:
        return redirect('/')

@csrf_exempt
def seller_confirm_form(request, room_id, bidder):
    try:
        usr = request.session['auction_account']['username']
        print(room_id)
        if history_bidding.objects.filter(bidder_id=bidder, room_id=ObjectId(room_id)).exists():
            his = history_bidding.objects(bidder_id=bidder, room_id=ObjectId(room_id)).order_by('-bids')[0]
            if request.is_ajax and request.method == "POST":
                reason = request.POST['reason']
                return JsonResponse({"reason": reason}, status=200)
            return render(request, 'ad/confirm_form.html', {'his': his})
        else:
            print('kkk')
            return render(request, 'ad/confirm_form.html', {'room_id': room_id, 'his': ''})
    except KeyError:
        return redirect('/')

@csrf_exempt
def seller_cancel_bid(request):
    try:
        usr = request.session['auction_account']['username']
        if request.is_ajax and request.method == "POST":
            room_id = request.POST['room_id']
            reason = request.POST['reason']
            buyer = request.POST['buyer']
            buyer_bid = request.POST['buyer_bid']
            room_cancel = room.objects(pk=ObjectId(room_id)).first()
            seller = room_cancel.seller_id.pk
            hb = room_cancel.highestbidder.pk
            if seller == usr:
                print('Bạn là người bán của phòng')
                if buyer == hb:
                   his = history_bidding.objects(room_id=ObjectId(room_id), bidder_id=buyer).order_by('-bids')[0]
                   bids = his.bids
                   print('Số bid hủy là ' + str(bids))
                   print(buyer_bid)
                   acc = account.objects(pk=buyer).first()
                   nb = acc.nb_bidcancel
                   if int(buyer_bid) == int(bids):
                       bid_cl = bid_cancel(bidder=account.objects(pk=buyer).first(),
                                           bidding_time=his.time,
                                           time_cancel=datetime.datetime.now(),
                                           room_id=room_cancel,
                                           cancel_account=account.objects(pk=usr).first(), reason=reason)
                       bid_cl.save()
                       history_bidding.objects.get(pk=his.pk).delete()
                       account.objects(pk=buyer).update(
                           __raw__={'$set': {'status': 'blocked', 'nb_bidcancel': nb + 1}})

                       if history_bidding.objects.filter(room_id=room_id).exists():
                           print('ffff')
                           max_bid = history_bidding.objects.filter(room_id=room_id).order_by('-bids')[0]
                           if history_bidding.objects.filter(room_id=room_id).count() > 1:
                               near_max_bid = \
                                   history_bidding.objects.filter(room_id=room_id).order_by('-bids')[
                                       1]
                               print(22)
                               print(near_max_bid.bids)
                               cur_bid = near_max_bid.bids + get_auction_bid(near_max_bid.bids, 23000)
                               room.objects(pk=ObjectId(room_id.pk)).update(
                                   __raw__={'$set': {'current_bid': cur_bid,
                                                     'highestbidder': max_bid.bidder_id.pk,
                                                     'highestbidder_bid': max_bid.bids}})
                               print(33)
                           else:
                               r = room.objects(pk=ObjectId(room_id)).first()
                               room.objects(pk=ObjectId(room_id)).update(
                                   __raw__={'$set': {'current_bid': r.product_id.startingbid,
                                                     'highestbidder': max_bid.bidder_id.pk,
                                                     'highestbidder_bid': max_bid.bids}})
                       else:
                           print('Buyer này là người đặt giá đầu tiên')
                           cur_bid = room.objects(pk=ObjectId(room_id)).first()
                           room.objects(pk=ObjectId(room_id)).update(
                               __raw__={'$set': {'current_bid': cur_bid.product_id.startingbid,
                                                 'highestbidder': cur_bid.seller_id.pk,
                                                 'highestbidder_bid': 0}})

                       if nb > 1:
                           account.objects(pk=buyer).update(
                               __raw__={'$set': {'status': 'blocked', 'nb_bidcancel': nb + 1}})
                       else:
                           account.objects(pk=buyer).update(
                               __raw__={'$set': {'status': 'blocked', 'nb_bidcancel': nb + 1}})
                       message = ''
                       return JsonResponse({"message": message}, status=200)

                   else:
                       message = 'Số tiền hủy không trùng khớp với form xác nhận. Vui lòng kiểm tra lại.'


                else:
                    message = 'Người mua không hợp lệ'
            else:
                message = 'Bạn không phải người bán. Không thể thay mặt người mua hủy giá!'

            return JsonResponse({"message": message}, status=200)

    except KeyError:
        return redirect('/')

def congratulation(request):
    return render(request, 'website/congratulation.html')


def message(request):
    try:
        usr = request.session['auction_account']['username']
        img = account.objects(pk=usr).first()
        img = img.img_url
        print(img)
        r_chat = model_chat_room.objects.filter((Q(host=usr)) | (Q(user=usr)))
        mes = messages.objects(receiver=usr)

        return render(request, 'website/message.html',
                      {'chat_room': r_chat, 'username': usr, 'sender_img': img, 'mes': mes})
    except KeyError:
        return redirect('/')


def message_inner(request, room_id):
    try:
        usr = request.session['auction_account']['username']
        img = account.objects(pk=usr).first()
        img = img.img_url
        his_mes = messages.objects(chat_room=ObjectId(room_id))
        print(img)
        r_chat = model_chat_room.objects()
        print('klksks    ' + room_id)
        return render(request, 'website/message_inner.html',
                      {'chat_room': r_chat, 'history': his_mes, 'room_id': room_id, 'username': usr, 'sender_img': img})
    except KeyError:
        return redirect('/')


def chat_with_seller(request, usr_id):
    try:
        usr = request.session['auction_account']['username']
        if (model_chat_room.objects.filter((Q(host=usr) & Q(user=usr_id)) | (Q(host=usr_id) & Q(user=usr))).exists()):
            if usr == 'admin':
                return redirect('/admin/message')
            else:
                return redirect('/usr/0/message')
        else:
            print('mjjjjjj')
            obj = chat_room(host=usr, user=usr_id)
            obj.save()
            if usr == 'admin':
                return redirect('/admin/message')
            else:
                return redirect('/usr/0/message')
    except KeyError:
        return redirect('/')


def reload_bid(request, id):
    try:
        room = model_room.objects(id=ObjectId(id)).first()
        pr_att = product_attributes.objects(product_id=ObjectId(room.product_id.id))
        try:

            bidder_id = request.session['auction_account'].get('username')
            usr = request.session['auction_account']['username']

        except KeyError:
            bidder_id = ''
            usr = ''
        h = model_his.objects(room_id=ObjectId(id),
                              bidder_id=bidder_id)
        count = h.count()
        try:
            history_bidding = h[count - 1]
        except IndexError:
            history_bidding = 0
        # print()
        return render(request, 'website/reload_bid.html',
                      {'username': usr, 'room': room, 'pr_att': pr_att, 'hs_bidding': history_bidding,
                       'check_seller': ''})
    except KeyError:
        return redirect('/')

def order_list(request):
    try:
        usr = request.session['auction_account']['username']
        ord = order.objects(buyer=usr)
        return render(request, 'website/order_list.html',
                      {'username': usr, 'ord': ord})
    except KeyError:
        return redirect('/')

def seller_room(request):
    try:
        usr = request.session['auction_account']['username']
        r = room.objects(seller_id=usr)
        return render(request, 'website/seller_room.html',
                      {'username': usr, 'room': r})
    except KeyError:
        return redirect('/')