# https://github.com/MongoEngine/django-mongoengine
from mongoengine import *
from django_mongoengine import fields, Document
import datetime
# Create your models here.

class auction_account(Document):
    account = fields.StringField(max_length=100)
    password = fields.StringField(max_length=100)

class account(Document):
    id = fields.StringField(max_length=100, primary_key=True)
    password = fields.StringField(max_length=100)
    email = fields.StringField(max_length=100)
    phonenb = fields.StringField(max_length=100, blank=True)
    address = fields.StringField(max_length=100, blank=True)
    city = fields.StringField(max_length=300, blank=True)
    district = fields.StringField(max_length=300, blank=True)
    role = fields.StringField(max_length=100, blank=True)
    img_url = fields.StringField(default=None, blank=True)
    status = fields.StringField(default='active')
    nb_bidcancel = fields.IntField(default=0)


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
    attributes_id = fields.ListField(ReferenceField('attributes', reverse_delete_rule=CASCADE), blank=True)


class chat_room(Document):
    host = fields.ReferenceField('account',reverse_delete_rule=CASCADE)
    user = fields.ReferenceField('account',reverse_delete_rule=CASCADE)

class messages(Document):
    chat_room = fields.ReferenceField('chat_room',reverse_delete_rule=CASCADE)
    sender = fields.ReferenceField('account',reverse_delete_rule=CASCADE)
    receiver = fields.ReferenceField('account',reverse_delete_rule=CASCADE)
    content = fields.StringField()
    time = fields.DateTimeField(default=datetime.datetime.utcnow)
    status = fields.StringField(default='received')

