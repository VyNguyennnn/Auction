from django import forms
from django.forms import ModelForm
from django.forms.forms import DeclarativeFieldsMetaclass
from django.forms.models import ALL_FIELDS
from .models import *
from  . import models
from django_mongoengine.forms import DocumentForm
from django_mongoengine import fields

# class SignupForm(forms.Form):
#    account  = forms.CharField(label='Tên đăng nhập', max_length=100)
#    password = forms.CharField(max_length=100)
#    auth_password = forms.CharField(max_length=100)
#    email = forms.CharField(max_length=100)
#    auth_email = forms.CharField(max_length=100)

# 111
class AccountForm(forms.Form):
   account  = forms.CharField(label='Tài khoản', max_length=100)
   password = forms.CharField(label='Mật khẩu',
                              widget=forms.PasswordInput(attrs={'id':'password',
                              'placeholder': '****', 'title':"Vui lòng nhập mật khẩu"}))

   account.widget.attrs.update({'id':'username', 'placeholder': 'admin','title':"Vui lòng nhập tên đăng nhập"})

   def __init__(self, *args, **kwargs):
      super(AccountForm, self).__init__(*args, **kwargs)
      for visible in self.visible_fields():
         visible.field.widget.attrs['class'] = 'form-control'

class ChangePaswordForm(forms.Form):
   OldPassword  = forms.CharField(label='Mật khẩu cũ',
                              widget=forms.PasswordInput(attrs={'id': 'OldPwd',
                              'placeholder': '****', 'title':"Vui lòng nhập mật khẩu hiện tại"}))
   NewPassword = forms.CharField(label='Mật khẩu mới',
                              widget=forms.PasswordInput(attrs={'id':'NewPwd',
                              'placeholder': '****', 'title':"Vui lòng nhập mật khẩu mới"}))

   AuthPassword = forms.CharField(label='Xác nhận mật khẩu',
                                 widget=forms.PasswordInput(attrs={'id': 'AuthPwd',
                                                                   'placeholder': '****',
                                                                   'title': "Vui lòng nhập xác nhận mật khẩu mới"}))

   def __init__(self, *args, **kwargs):
      super(ChangePaswordForm, self).__init__(*args, **kwargs)
      for visible in self.visible_fields():
         visible.field.widget.attrs['class'] = 'form-control'




def get_values():
    list = []
    category_list = [(0,'---Chọn---')]

    for cate in models.category.objects:
        if cate.attributes_id == [] or cate.attributes_id[0].id == 0:
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

    for l in list:
        item = (l['id'], l['name'])
        category_list.append(item)

    return category_list

def get_list():
    ls = [(0,'---Chọn---')]
    for a in models.attributes.objects:
        item = (a['id'], a['name'])
        ls.append(item)
    return ls

class CategoryForm(DocumentForm):
    id = forms.CharField(label='Mã danh mục')
    category_parent = forms.ChoiceField(label='Danh mục cha', choices=get_values, initial=0)
    name = forms.CharField(label='Tên danh mục', max_length=100)
    # attributes_id = forms.ChoiceField(label='Tên thuộc tính', choices=attributes.objects.values_list('id','name'))
    attributes_id = forms.ChoiceField(label='Tên thuộc tính', choices=get_list, initial=0)

    def __init__(self, *args, **kwargs):
      super(CategoryForm, self).__init__(*args, **kwargs)
      self.fields['attributes_id'].widget.attrs.update({'style': 'width: 100%;'})
      for visible in self.visible_fields():
         visible.field.widget.attrs['class'] = 'form-control'

      # self.fields['category_parent'] = forms.ChoiceField(label='Danh mục cha', choices=category_list, initial='')
      self.fields['attributes_id'].widget.attrs.update({'class': 'form-control tt'})

    class Meta:
      document = models.category
      fields = ('__all__')


class AttributeGroupsForm(DocumentForm):
    name = forms.CharField(label='Tên nhóm thuộc tính', max_length=300, required=True)
    name.widget.attrs['name'] = 'name'
    def __init__(self, *args, **kwargs):
      super(AttributeGroupsForm, self).__init__(*args, **kwargs)
      for visible in self.visible_fields():
         visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
      document = attribute_groups
      fields = ('__all__')


def get_list_attr_group():
    l = [(0, '---Chọn---')]
    for a in models.attribute_groups.objects:
        item = (a['id'], a['name'])
        l.append(item)
    return l

class AttributesForm(DocumentForm):
    # attr_groups_list = []
    # for c in attribute_groups.objects:
    #     attr_groups = (c.id, c.name)
    #     attr_groups_list.append(attr_groups)


    name = forms.CharField(label='Tên thuộc tính', max_length=300)
    name.widget.attrs['name'] = 'name'
    attribute_groups_id = forms.ChoiceField(label='Nhóm thuộc tính',
                                            choices=get_list_attr_group, initial=0)
    # attribute_groups_id = forms.ChoiceField(label='Nhóm thuộc tính',choices=attribute_groups.objects.values_list('id','name'))

    def __init__(self, *args, **kwargs):
      super(AttributesForm, self).__init__(*args, **kwargs)
      for visible in self.visible_fields():
         visible.field.widget.attrs['class'] = 'form-control'

      self.fields['attribute_groups_id'].widget.attrs['class'] = 'form-control t'

    class Meta:
      document = attributes
      fields = ('__all__')
      # fields = ['id', 'name'] #attribute_groups_id will be handled in view

