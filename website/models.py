from uuid import uuid4
from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser

from django.contrib.auth.base_user import BaseUserManager

import allauth
from allauth.socialaccount.models import SocialLogin
from allauth.account.utils import get_next_redirect_url
from allauth.utils import get_request_param
from bson import ObjectId

import datetime

from mongoengine import *
from django_mongoengine import fields, Document
from django.core.files.storage import FileSystemStorage
from django.conf import settings
# Create your models here.
from mongoengine import *
from django_mongoengine import fields, Document
import time
import sys
from threading import Timer
from time import sleep

@classmethod
def state_from_request(cls, request):
    state = {}
    next_url = get_next_redirect_url(request)
    # # add this statement is important. We get the query parameter we added to the template and store it here as a  session value.
    try:
        request.session["user_type"] = get_request_param(request, "user", None)
        # request.session["user_type"] = get_request_param(request, "user", None)
    except KeyError:
        print('user_type not exist')

    if next_url:
        state["next"] = next_url
        print('next: '+state["next"])
    state["process"] = get_request_param(request, "process", "login")
    print('process: '+state["process"])
    state["scope"] = get_request_param(request, "scope", "")
    print('scope: ' + state["scope"])
    state["auth_params"] = get_request_param(request, "auth_params", "")
    print('auth_params: ' + state["auth_params"])

    return state

allauth.socialaccount.models.SocialLogin.state_from_request = state_from_request

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('mail address is required')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email)

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):

        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

class CSUser(AbstractBaseUser):
    userId = models.CharField(
        max_length=255, default=uuid4, primary_key=True, editable=False, unique=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    created = models.DateTimeField(default=timezone.now)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email

    def has_module_perms(self, app_label):
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        return self.is_superuser


class account(Document):
    id = fields.StringField(max_length=100, primary_key=True)
    password = fields.StringField(max_length=100)
    email = fields.StringField(max_length=100)
    phonenb = fields.StringField(max_length=100, blank=True)
    address = fields.StringField(max_length=100)
    city = fields.StringField(max_length=300)
    district = fields.StringField(max_length=300)
    role = fields.StringField(max_length=100, blank=True)
    # is_verify = fields.BooleanField(default=False, blank=True)
    # token = fields.StringField(default=None, blank=True)
    # image = fields.ImageField(upload_to='account', blank=True)
    img_url = fields.StringField(default=None, blank=True)
    status = fields.StringField(default='active')
    nb_bidcancel = fields.IntField(default=0)
    # image = fields.ImageField(upload_to='media', default=content_file_name, blank=True)


class attribute_groups(Document):
    id = fields.IntField(primary_key=True)
    name = fields.StringField(max_length=300)

class attributes(Document):
    attr_groups_list = []
    for c in attribute_groups.objects:
        attr_groups = (str(c.id), c.name)
        attr_groups_list.append(attr_groups)
    id = fields.IntField(primary_key=True)
    name = fields.StringField(max_length=300)
    # attribute_groups_id = fields.IntField(choices=attr_groups_list)
    # atrg is refe..field in model so it just saves _id of corresponding attribute_groups documenent. (see attributes in view)
    attribute_groups_id = fields.ReferenceField('attribute_groups',reverse_delete_rule=CASCADE)

class category(Document):
    id = fields.IntField(primary_key=True)
    category_parent = fields.IntField()
    name = fields.StringField(max_length=300)
    attributes_id = fields.ListField(ReferenceField('attributes', reverse_delete_rule=CASCADE))


class OneImage(EmbeddedDocument):
    image = fields.ImageField(upload='product')
    url = fields.StringField()


class product(Document):
    # usr = account.objects(pk='hhh').first()
    name = fields.StringField(max_length=300)
    category = fields.ReferenceField('category', reverse_delete_rule=CASCADE)
    decription = fields.StringField(max_length=500)
    quantity = fields.IntField(default=1)
    address = fields.StringField(max_length=200)
    city = fields.StringField(max_length=300)
    district = fields.StringField(max_length=300)
    image = fields.EmbeddedDocumentListField(OneImage)
    startingbid = fields.FloatField()
    duration = fields.StringField()
    condition = fields.StringField()
    # specifics = fields.EmbeddedDocumentListField(item_specifics)
    seller = fields.ReferenceField('account', reverse_delete_rule=CASCADE)


class product_attributes(Document):
    product_id = fields.ReferenceField('product', reverse_delete_rule=CASCADE)
    attributes = fields.ReferenceField('attributes', reverse_delete_rule=CASCADE)
    content = fields.StringField(max_length=500)


class room(Document):
    # Title = fields.StringField(max_length=500)
    product_id = fields.ReferenceField('product', reverse_delete_rule=CASCADE)
    total = fields.FloatField()
    start = fields.DateTimeField(default=datetime.datetime.now)
    end = fields.DateTimeField()
    seller_id = fields.ReferenceField('account', reverse_delete_rule=CASCADE)
    quantity_of_bidder = fields.IntField()
    # bidders = fields.ListField(ReferenceField('account', reverse_delete_rule=CASCADE), blank=True)
    highestbidder = fields.ReferenceField('account', reverse_delete_rule=CASCADE, blank=True)
    current_bid = fields.FloatField()
    status = fields.StringField(max_length=10)
    winner = fields.ReferenceField('account', reverse_delete_rule=CASCADE, blank=True)
    highestbidder_bid = fields.FloatField()



class history_bidding(Document):
    bidder_id = fields.ReferenceField('account', reverse_delete_rule=CASCADE, blank=True)
    room_id = fields.ReferenceField('room', reverse_delete_rule=CASCADE, blank=True)
    bids = fields.FloatField()
    time = fields.DateTimeField(default=datetime.datetime.now)



class UserTimer:
    def __init__(self, id=None, interval=None):
        self.id = id
        self.interval = interval

    def timeout(self):
        r = room.objects(id=ObjectId(self.id), status='opening').first()
        print('---------------------------')
        now = round(time.time() * 1000)
        print(now)
        end = r.end
        millisec = end.timestamp() * 1000
        print(millisec)
        room.objects(id=ObjectId(r.id)).update(status='closed')
        print('phong ' + str(r.id) + ' da dong!')

    def __call__(self):
        print('UserTimer dang chay....')
        self.timer_thread = Timer(self.interval, self.timeout)
        self.timer_thread.start()
        # sleep(0.2)


    def cancel(self):
        try:
            self.timer_thread.cancel()
        except AttributeError:
            raise RuntimeError("'UserTimer' object not started.")

class acc(Document):
    id = fields.StringField(primary_key=True)
    time = fields.IntField()

class chat_room(Document):
    host = fields.ReferenceField('account',reverse_delete_rule=CASCADE)
    user = fields.ReferenceField('account',reverse_delete_rule=CASCADE)

class messages(Document):
    chat_room = fields.ReferenceField('chat_room',reverse_delete_rule=CASCADE)
    sender = fields.ReferenceField('account',reverse_delete_rule=CASCADE)
    receiver = fields.ReferenceField('account',reverse_delete_rule=CASCADE)
    content = fields.StringField()
    time = fields.DateTimeField(default=datetime.datetime.now)
    status = fields.StringField(default='received')

class bid_cancel(Document):
    bidder = fields.ReferenceField('account',reverse_delete_rule=CASCADE)
    bidding_time = fields.DateTimeField()
    time_cancel = fields.DateTimeField(default=datetime.datetime.now)
    room_id = fields.ReferenceField('room',reverse_delete_rule=CASCADE)
    cancel_account = fields.ReferenceField('account',reverse_delete_rule=CASCADE)
    reason = fields.StringField(blank=True)

class order(Document):
    seller = fields.ReferenceField('account',reverse_delete_rule=CASCADE)
    buyer = fields.ReferenceField('account',reverse_delete_rule=CASCADE)
    product_id = fields.ReferenceField('product',reverse_delete_rule=CASCADE)
    quantity = fields.IntField()
    total = fields.FloatField()
    room_id = fields.ReferenceField('room',reverse_delete_rule=CASCADE)
    created = fields.DateTimeField(default=datetime.datetime.now)
    payURL = fields.StringField(default='')
    status = fields.StringField(default='opening')


