import hashlib
import json

from django.shortcuts import render, redirect
import check_permission
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import website.models
from .forms import *
from .models import *
from website.models import account as web_acc
from website.models import chat_room as model_chat_room
from bson import ObjectId
# Create your views here.
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
# from rest_auth.registration.views import SocialLoginView
#
#
# class GoogleLogin(SocialLoginView):
#     adapter_class = GoogleOAuth2Adapter
#     client_class = OAuth2Client


def login_form(request):
    try:
        acc = account.objects(role='admin').first()
        if check_permission.permission(request, acc, 'admin') == 'admin':
            print(request.session['auction_account'])
            return redirect('/admin/index')
        else:
            form = AccountForm()
            return render(request, 'ad/login_form.html', {'form': form})
    except KeyError:
        print(request.session['auction_account'])
        form = AccountForm()
        return render(request, 'ad/login_form.html', {'form': form})



def category(request):
    list = []
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        user = acc.id
        user = user.split().pop(0)

        for cate in models.category.objects:
            list1 = [cate.name]
            pr = cate.category_parent

            while pr != 0:
                if pr != 0:
                    c = models.category.objects.get(id=pr)
                    pr = c.category_parent
                    list1.append(c.name)
            list1.reverse()
            s = ' > '.join([str(item) for item in list1])
            list.append({'id': cate.id, 'name': s})

        return render(request, 'ad/category.html', {'username': user, 'category_list': list})
    else:
        print(request.session.get('auction_account'))
        return redirect('/admin')


@csrf_exempt
def category_edit(request):
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        user = acc.id
        user = user.split().pop(0)

        message = 'Lỗi!'
        form = CategoryForm
        form_attribute = AttributesForm
        list_attrs_id = []
        if request.is_ajax and request.method == "POST":
            form = CategoryForm(request.POST)
            name = request.POST.get('name')
            category_parent = request.POST.get('category_parent')
            attrs_id = request.POST.getlist('attrs_id[]')
            if not models.category.objects(name=name):
                if form.is_valid():
                    message = ''
                    cate = form.save(commit=False)
                    print(request.POST)
                    if not models.category.objects.latest('id'):
                        cate.id = 1
                    else:
                        last_doc = models.category.objects.latest('id')
                        cate.id = int(last_doc.id) + 1
                    if request.POST['check_add_attr'] == 'True':
                       for l in attrs_id:
                          doc = models.attributes.objects(id=int(l)).first()
                          list_attrs_id.append(doc)
                    cate.attributes_id = list_attrs_id
                    cate.save()
            else:
                message = 'Thuộc tính đã tồn tại!'
            return JsonResponse({"message": message}, status=200)
        return render(request, 'ad/category_edit.html', {'username': user, 'form': form, 'form_attribute': form_attribute})
    else:
        print(request.session.get('auction_account'))
        return redirect('/admin')


@csrf_exempt
def category_update(request, id):
    form = CategoryForm
    print('snkshskhs')
    form_attribute = AttributesForm
    cate = models.category.objects(id=id).first()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        message = 'Lỗi!'
        ls_attr = request.POST.getlist('attributes[]')
        name = request.POST['name']
        cate_attr = []
        cate_attr_int = []
        if request.POST['check_add_attr'] == 'True':
           for x in ls_attr:
              cate_attr_int.append(models.attributes.objects(id=int(x)).first())
        if (name == cate.name) and (cate_attr == ls_attr):
            message = 'Các thông tin không có sự thay đổi!'
        else:
            form = CategoryForm(request.POST)
            f = form.save(commit=False)
            f.id = id
            f.name = name
            f.attributes_id = cate_attr_int
            f.save()
            message = 'Cập nhật thành công!'
        return JsonResponse({"message": message}, status=200)
    else:
        return render(request, 'ad/category_update.html', {'form': form, 'form_attribute': form_attribute, 'cate': cate})

def index(request):
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        s = acc.id
        s = s.split().pop(0)
        return redirect('/admin/room')
    else:
        print(request.session.get('auction_account'))
        return redirect('/admin')

def change_password_form(request):
    form = ChangePaswordForm
    return render(request, 'ad/change_password_form.html', {'form': form})


@csrf_exempt
def login(request):
    # request should be ajax and method should be POST.
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        # some error occured
        return JsonResponse({"kq": 3}, status=200)
    else:
        if request.is_ajax and request.method == "POST":
            # get the form data
            form = AccountForm(request.POST)
            if form.is_valid():
                Account = form.cleaned_data['account']
                password = form.cleaned_data['password']
                password = hashlib.sha1(bytes(password, 'utf-8'))
                password = password.hexdigest()
                if Account == acc.id and password == acc.password:
                    kq = 1
                    request.session['auction_account'] = {'username': acc.id, 'password': acc.password, 'role': 'admin'}
                    vd = request.session['auction_account']
                    print(vd['username'])
                else:
                    kq = 0
                return JsonResponse({"kq": kq}, status=200)
            else:
                # some form errors occured.
                return JsonResponse({"error": form.errors}, status=400)
        else:
            return redirect('/admin')
        return JsonResponse({"kq": 'redirect'}, status=200)

@csrf_exempt
def logout(request):
    try:
        usr = request.session['auction_account']['username']
        pwd = request.session['auction_account']['password']
        rl = request.session['auction_account']['role']
        if usr != None and pwd != None and rl != None:
        # request.session.modified = True
            del request.session['auction_account']
            # request.session['auction_account'] = {'username': None, 'password': None, 'role': None}
        return redirect('/admin')
    except:
        return redirect('/admin')

@csrf_exempt
def changepwd(request):
    # request should be ajax and method should be POST.
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
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
                        account.objects(pk='admin').update(__raw__={'$set': {'password': NewPwd}})
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


@csrf_exempt
def attribute_groups(request):
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        user = acc.id
        user = user.split().pop(0)

        message = 'Lỗi!'
        list = models.attribute_groups.objects
        form = AttributeGroupsForm
        if request.is_ajax and request.method == "POST":
            form = AttributeGroupsForm(request.POST)
            name = request.POST.get('name')
            if not models.attribute_groups.objects(name=name):
                if form.is_valid():
                    message = ''
                    attr = form.save(commit=False)
                    if not models.attribute_groups.objects.latest('id'):
                        attr.id = 1
                    else:
                        last_doc = models.attribute_groups.objects.latest('id')
                        attr.id = int(last_doc.id) + 1
                    attr.save()
            else:
                message = 'Thuộc tính đã tồn tại!'
            return JsonResponse({"message": message}, status=200)
        return render(request, 'ad/attribute_groups.html', {'attribute_groups': list, 'form': form, 'username': user})
    else:
        print(request.session.get('auction_account'))
        return redirect('/admin')



@csrf_exempt
def attributes(request):
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        user = acc.id
        user = user.split().pop(0)

        message = 'Lỗi!'
        list = models.attributes.objects
        form = AttributesForm
        if request.is_ajax and request.method == "POST":
            name = request.POST.get('name')
            attribute_groups_id = request.POST.get('attribute_groups_id')
            form = AttributesForm(request.POST)
            print(request.POST)
            if not models.attributes.objects(name=name):
                if form.is_valid():
                    message = ''
                    last_doc = models.attributes.objects.latest('id')
                    # atrg is refe..field in model so it just saves _id of corresponding attribute_groups documenent.
                    atrg = models.attribute_groups(id=attribute_groups_id)
                    attg = form.save(commit=False)
                    attg.attribute_groups_id = atrg
                    if not last_doc:
                        attg.id = 1
                    else:
                        attg.id = int(last_doc.id) + 1
                    attg.save()
            else:
                message = 'Thuộc tính đã tồn tại!'
            return JsonResponse({"message": message}, status=200)
        return render(request, 'ad/attributes.html', {'attributes': list, 'form': form, 'username': user})
    else:
        print(request.session.get('auction_account'))
        return redirect('/admin')



@csrf_exempt
def delete_attribute_groups(request, id):
    list = models.attribute_groups.objects
    form = AttributeGroupsForm
    if request.is_ajax and request.method == "POST":
        attr_grp = models.attribute_groups.objects(id=id)
        attr_grp.delete()
        return JsonResponse({"message": 'delete_atr_g'}, status=200)
    return render(request, 'ad/attribute_groups.html', {'attribute_groups': list, 'form': form})

@csrf_exempt
def delete_attributes(request, id):
    print(id)
    list = models.attributes.objects
    form = AttributesForm
    if request.is_ajax and request.method == "POST":
        attr = models.attributes.objects(id=id)
        attr.delete()
        return JsonResponse({"message": 'delete_attributes'}, status=200)
    return render(request, 'ad/attributes.html', {'attributes': list, 'form': form})

@csrf_exempt
def delete_category(request, id):
    print(id)
    form = CategoryForm
    form_attribute = AttributesForm
    if request.is_ajax and request.method == "POST":
        attr = models.category.objects(id=id).first()
        doc = models.category.objects(category_parent=id).first()
        if doc:
           doc.delete()

        attr.delete()
        return JsonResponse({"message": 'delete_category'}, status=200)
    return render(request, 'ad/category_edit.html', {'form': form, 'form_attribute': form_attribute})


@csrf_exempt
def update_attribute_groups(request, id):
    list = models.attribute_groups.objects
    form = AttributeGroupsForm
    if request.is_ajax and request.method == "POST":
        form = AttributeGroupsForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"name": "update_attribute_groups"}, status=200)
    return render(request, 'ad/attribute_groups.html', {'attribute_groups': list, 'form': form})

@csrf_exempt
def update_attributes(request, id):
    message = "Lỗi!"
    list = models.attributes.objects
    form = AttributesForm
    if request.is_ajax and request.method == "POST":
        form = AttributesForm(request.POST)
        if not models.attributes.objects(name=request.POST['name']):
            if form.is_valid():
                message = ''
                atrg = models.attribute_groups(id=request.POST['attribute_groups_id'])
                attg = form.save(commit=False)
                attg.attribute_groups_id = atrg
                attg.save()
        else:
            message = 'Thuộc tính này đã tồn tại!'

        return JsonResponse({"message": message}, status=200)
    return render(request, 'ad/attributes.html', {'attributes': list, 'form': form})

@csrf_exempt
def attributes_attrgroups(request):
    if request.is_ajax and request.method == "POST":
        id_attr = request.POST.get('id_attr')
        print(id_attr)
        doc = models.attributes.objects(id=int(id_attr)).first()
        return JsonResponse({"message": doc.attribute_groups_id.id}, status=200)
    return JsonResponse({"message": 'Lỗi!'}, status=400)

def all_account(request):
    acc = website.models.account.objects(role='user')
    return render(request, 'ad/all_account.html', {'acc': acc})

def blocked_account(request):
    blocked_acc = web_acc.objects(role='user', status='blocked')
    return render(request, 'ad/blocked_account.html', {'acc': blocked_acc})

@csrf_exempt
def unblock_account(request):
    if request.is_ajax and request.method == "POST":
        ls = request.POST.getlist('ls[]')
        for l in ls:
            models.account.objects(pk=l).update(__raw__={'$set': {'status': 'active'}})
        return JsonResponse({"message": 'Mở khóa thành công!'}, status=200)
    return JsonResponse({"message": 'Lỗi!'}, status=400)

# def login_form(request):
#     # ad = models.account(id='admin', password='d033e22ae348aeb5660fc2140aec35850c4da997', role='admin',
#     #                             email='nguyen01vy12@gmail.com')
#     # ad.save()
#     a = models.account.objects(id='admin').first()
#     print(a.password)
#     password = hashlib.sha1(bytes('admin', 'utf-8'))
#     password = password.hexdigest()
#     print(password)
#     form = AccountForm()
#     return render(request, 'ad/login_form.html', {'form': form})

def message(request):
    usr = request.session['auction_account']['username']
    img = account.objects(pk=usr).first()
    img = img.img_url
    print(img)
    r_chat = model_chat_room.objects.filter( (Q(host=usr)) | (Q(user=usr)))
    print('jjjjjjjjjjjjjjjjjjjjjjjjjjjjj')
    for r in r_chat:
        print(r.pk)
        print(r.host)

    mes = messages.objects(receiver=usr)
    return render(request, 'ad/message.html', {'chat_room': r_chat, 'username':usr, 'sender_img': img, 'mes':mes})

def message_inner(request, room_id):
    usr = request.session['auction_account']['username']
    img = account.objects(pk=usr).first()
    img = img.img_url
    print('room_id'+ room_id)

    his_mes = messages.objects(chat_room=ObjectId(room_id))
    # print(img)
    r_chat = model_chat_room.objects()
    print('admin klksks    '+room_id)
    return render(request, 'ad/message_inner.html', {'chat_room': r_chat, 'history': his_mes, 'room_id': room_id, 'username':usr, 'sender_img': img})

def room(request):
    try:
        usr = request.session['auction_account']['username']
        auction_room = website.models.room.objects()
        mes = messages.objects(receiver=usr)
        return render(request, 'ad/room.html', {'room': auction_room, 'mes':mes})
    except:
        return redirect('/admin')

def room_history(request, room_id):
    try:
        usr = request.session['auction_account']['username']
        his_room = website.models.history_bidding.objects(room_id=ObjectId(room_id))
        mes = messages.objects(receiver=usr)
        return render(request, 'ad/history_bidding.html', {'his_bid': his_room, 'mes':mes})
    except:
        return redirect('/admin')

def find_cancel_bid_form(request):
    try:
        usr = request.session['auction_account']['username']
        return render(request, 'ad/find_cancel_bid_form.html', {'username': usr})
    except KeyError:
        return redirect('/')

def load_product(request):
    try:
        usr = request.session['auction_account']['username']
        ls = website.models.room.objects(status='opening')
        return render(request, 'website/seller_list_product.html', {'username': usr, 'room': ls})
    except KeyError:
        return redirect('/')

def reason_form(request, room_id):
    try:
        usr = request.session['auction_account']['username']
        r = website.models.room.objects(pk=ObjectId(room_id)).first()
        return render(request, 'ad/reason_form.html', {'username': usr, 'room': r})
    except KeyError:
        return redirect('/')

@csrf_exempt
def confirm_form(request, room_id, bidder):
    try:
        usr = request.session['auction_account']['username']
        print(room_id)
        if website.models.history_bidding.objects.filter(bidder_id=bidder, room_id=ObjectId(room_id)).exists():
            his = website.models.history_bidding.objects(bidder_id=bidder, room_id=ObjectId(room_id)).order_by('-bids')[0]
            if request.is_ajax and request.method == "POST":
                reason = request.POST['reason']
                return JsonResponse({"reason": reason}, status=200)
            return render(request, 'website/seller_confirm_form.html', {'his': his})
        else:
            print('kkk')
            return render(request, 'website/seller_confirm_form.html', {'room_id': room_id, 'his': ''})
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
def cancel_bid(request):
    try:
        usr = request.session['auction_account']['username']
        if request.is_ajax and request.method == "POST":
            room_id = request.POST['room_id']
            reason = request.POST['reason']
            buyer = request.POST['buyer']
            buyer_bid = request.POST['buyer_bid']
            room_cancel = website.models.room.objects(pk=ObjectId(room_id)).first()
            seller = room_cancel.seller_id.pk
            hb = room_cancel.highestbidder.pk
            print(buyer)
            if buyer == hb:
                his = website.models.history_bidding.objects(room_id=ObjectId(room_id), bidder_id=buyer).order_by('-bids')[0]
                bids = his.bids
                print('Số bid hủy là ' + str(bids))
                print(buyer_bid)
                acc = account.objects(pk=buyer).first()
                nb = acc.nb_bidcancel
                if int(buyer_bid) == int(bids):
                    bid_cl = website.models.bid_cancel(bidder=website.models.account.objects(pk=buyer).first(),
                                        bidding_time=his.time,
                                        time_cancel=datetime.datetime.now(),
                                        room_id=room_cancel,
                                        cancel_account='admin', reason=reason)
                    bid_cl.save()
                    website.models.history_bidding.objects.get(pk=his.pk).delete()
                    website.models.account.objects(pk=buyer).update(
                        __raw__={'$set': {'status': 'blocked', 'nb_bidcancel': nb + 1}})

                    if website.models.history_bidding.objects.filter(room_id=room_id).exists():
                        print('ffff')
                        max_bid = website.models.history_bidding.objects.filter(room_id=room_id).order_by('-bids')[0]
                        if website.models.history_bidding.objects.filter(room_id=room_id).count() > 1:
                            near_max_bid = \
                                website.models.history_bidding.objects.filter(room_id=room_id).order_by('-bids')[
                                    1]
                            print(22)
                            print(near_max_bid.bids)
                            cur_bid = near_max_bid.bids + get_auction_bid(near_max_bid.bids, 23000)
                            website.models.room.objects(pk=ObjectId(room_id.pk)).update(
                                __raw__={'$set': {'current_bid': cur_bid,
                                                  'highestbidder': max_bid.bidder_id.pk,
                                                  'highestbidder_bid': max_bid.bids}})
                            print(33)
                        else:
                            r = website.models.room.objects(pk=ObjectId(room_id)).first()
                            website.models.room.objects(pk=ObjectId(room_id)).update(
                                __raw__={'$set': {'current_bid': r.product_id.startingbid,
                                                  'highestbidder': max_bid.bidder_id.pk,
                                                  'highestbidder_bid': max_bid.bids}})
                    else:
                        print('Buyer này là người đặt giá đầu tiên')
                        cur_bid = website.models.room.objects(pk=ObjectId(room_id)).first()
                        website.models.room.objects(pk=ObjectId(room_id)).update(
                            __raw__={'$set': {'current_bid': cur_bid.product_id.startingbid,
                                              'highestbidder': cur_bid.seller_id.pk,
                                              'highestbidder_bid': 0}})

                    if nb > 1:
                        website.models.account.objects(pk=buyer).update(
                            __raw__={'$set': {'status': 'blocked', 'nb_bidcancel': nb + 1}})
                    else:
                        website.models.account.objects(pk=buyer).update(
                            __raw__={'$set': {'status': 'blocked', 'nb_bidcancel': nb + 1}})
                    message = ''
                    return JsonResponse({"message": message}, status=200)

                else:
                    message = 'Số tiền hủy không trùng khớp với form xác nhận. Vui lòng kiểm tra lại.'


            else:
                message = 'Người mua không hợp lệ'

            return JsonResponse({"message": message}, status=200)

    except KeyError:
        return redirect('/')
