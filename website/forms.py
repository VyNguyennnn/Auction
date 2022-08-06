import re

from django import forms
from .models import *
from . import models
from datetime import timedelta
from django_mongoengine.forms import DocumentForm
from django.core.files.storage import FileSystemStorage


class SignupForm(DocumentForm):
   id = forms.CharField(label='Tên đăng nhập', max_length=100)
   password = forms.CharField(label='Mật khẩu',
                                 widget=forms.PasswordInput(attrs={'placeholder': '****',
                                                                   'title': "Vui lòng nhập mật khẩu"}), required=False)
   auth_password = forms.CharField(label='Xác nhận mật khẩu',
                                 widget=forms.PasswordInput(attrs={'placeholder': '****',
                                                                   'title': "Vui xác nhận mật khẩu"}),required=False)
   address = forms.CharField(label='Địa chỉ', max_length=100)
   city = forms.CharField(label='Tỉnh/ Thành phố', required=False, widget=forms.Select(choices=[]))
   district = forms.CharField(label='Quận/ Huyện', required=False, widget=forms.Select(choices=[]))
   email = forms.CharField(max_length=100)
   phonenb = forms.CharField(max_length=100, required=False)
   phonenb.widget.attrs.update({'placeholder': 'Số điện thoại'})
   # image = forms.ImageField(required=False)

   def __init__(self, *args, **kwargs):
      super(SignupForm, self).__init__(*args, **kwargs)
      for visible in self.visible_fields():
         visible.field.widget.attrs['class'] = 'form-control'


   class Meta:
      document = account
      fields = ['id', 'password', 'address', 'city', 'district', 'email', 'phonenb']

class AccountForm(forms.Form):
   account  = forms.CharField(label='Tài khoản', max_length=100)
   password = forms.CharField(label='Mật khẩu',
                              widget=forms.PasswordInput(attrs={'id':'password',
                              'placeholder': '****', 'title':"Vui lòng nhập mật khẩu"}))

   account.widget.attrs.update({'id':'username', 'placeholder': 'abc123','title':"Vui lòng nhập tên đăng nhập"})

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
    category_list = []

    for cate in models.category.objects:
        # if cate.attributes_id is None or cate.attributes_id[0].id != 0:
        if cate.attributes_id is not None:
            list1 = [cate.name]
            pr = cate.category_parent

            while pr != 0:
                if pr != 0:
                    c = models.category.objects.get(id=pr)
                    pr = c.category_parent
                    list1.append(c.name)
            list1.reverse()
            s = ' > '.join([str(item) for item in list1])
            try:
                field = cate.attributes_id[0]
                if field != 0:
                   list.append({'id': cate.id, 'name': s})
            except IndexError:
                g = 2


    for l in list:
        item = (l['id'], l['name'])
        category_list.append(item)

    return category_list

class RoomForm(DocumentForm):
    def __init__(self, *args, **kwargs):
      super(RoomForm, self).__init__(*args, **kwargs)
      for visible in self.visible_fields():
         visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
      document = models.room
      fields = ('__all__')



class ProductImageFieldWidget(forms.MultiWidget):
    widgets = (
        forms.widgets.ClearableFileInput(),
        forms.widgets.ClearableFileInput(),
        forms.widgets.ClearableFileInput(),
        forms.widgets.ClearableFileInput(),
        forms.widgets.ClearableFileInput(),
        forms.widgets.ClearableFileInput()
    )
    def decompress(self,value):
        if value:
            # return value.split("|")
            return [value[0], value[1], value[2], value[3]]
        return [None, None, None, None]


class ProductImageField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (
            forms.ImageField(),
            forms.ImageField(),
            forms.ImageField(),
            forms.ImageField(),
            forms.ImageField(),
            forms.ImageField()
        )
        list_widgets = (
            forms.widgets.ClearableFileInput(),
            forms.widgets.ClearableFileInput(),
            forms.widgets.ClearableFileInput(),
            forms.widgets.ClearableFileInput(),
            forms.widgets.ClearableFileInput(),
            forms.widgets.ClearableFileInput()
        )
        self.widget = ProductImageFieldWidget(widgets=[fields[0].widget, fields[1].widget, fields[2].widget, fields[3].widget, fields[4].widget, fields[5].widget])
        super(ProductImageField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            fs = FileSystemStorage()
            ls_img = []
            # fs.save(img.name, img)
            for i in range(0, 4):
               name = fs.save(data_list[i].name, data_list[i])
               url = fs.url(name)
               ls_img.append(models.OneImage(image=data_list[i], url=url))
            return ls_img

class ProductAttributesFieldWidget(forms.MultiWidget):
    widgets = (
        forms.widgets.TextInput(),
        forms.widgets.TextInput(),
        forms.widgets.TextInput(),
        forms.widgets.TextInput(),
    )
    def decompress(self, value):
        if value:
            # return value.split("|")
            ls = []
            for i in range(0, self.l):
                ls.append(value[i])
            return ls
        return [None, None, None]


class ProductAttributesField(forms.MultiValueField):
    def __init__(self, l, *args, **kwargs):
        self.l = l
        fields = []
        list_widgets = []
        for i in range(0, self.l):
            fields.append(forms.CharField())
            list_widgets.append(forms.TextInput(attrs={'placeholder': 'kjhkuhhk', 'required': False}))

        self.widget = ProductAttributesFieldWidget(widgets=list_widgets)
        # self.widget = ProductAttributesFieldWidget(widgets=[fields[0].widget, fields[1].widget, fields[2].widget, fields[3].widget])
        super(ProductAttributesField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            ls = []
            for i in range(0, self.l):
                m = models.item_specifics(attributes=1, content=data_list[i])
                ls.append(m)
            return ls

class ProductForm(DocumentForm):
    CHOICES = [(timedelta(days=1), '1 ngày'),
               (timedelta(days=3), '3 ngày'),
               (timedelta(days=5), '5 ngày'),
               (timedelta(days=7), '7 ngày'),
               (timedelta(days=10), '10 ngày')]

    condition_choices = [('new', 'Mới'),
               ('used', 'Đã sử dụng'),
               ('open box', 'Đã mở hộp')]

    duration = forms.ChoiceField(label='Diễn ra', choices=CHOICES, widget=forms.RadioSelect)
    startingbid = forms.FloatField(label='Giá khởi điểm', widget=forms.TextInput(attrs={'data-mask': "999999",'title':"Vui lòng nhập giá khởi điểm.",
                                                                                             'value': 11}))
    category = forms.ChoiceField(label='Danh mục', choices=get_values, widget=forms.Select(
        attrs={'class': 'form-control chosen-select'}))
    name = forms.CharField(label='Tiêu đề', widget=forms.TextInput(attrs={'value': 'Title here'}))
    quantity = forms.IntegerField(label='Số lượng', widget=forms.TextInput(attrs={'value': 1}))
    image = ProductImageField(label='Hình ảnh')
    decription = forms.CharField(label='Mô tả sản phẩm', widget=forms.Textarea(), initial='decription here')
    address = forms.CharField(label='Gửi từ địa chỉ', max_length=100)
    city = forms.CharField(label='Tỉnh/ Thành phố', required=False, widget=forms.Select(choices=[]))
    district = forms.CharField(label='Quận/ Huyện', required=False, widget=forms.Select(choices=[]))
    # shipping = forms.ChoiceField(label='Phí vận chuyển', choices=[('---Chọn---', '---Chọn---'),
    #     ('Giá sản phẩm đã bao gồm phí vận chuyển' ,'Giá sản phẩm đã bao gồm phí vận chuyển'),
    #     ('Người mua tự thanh toán phí vận chuyển', 'Người mua tự thanh toán phí vận chuyển')])
    condition = forms.ChoiceField(label='Điều kiện sản phẩm', choices=condition_choices)
    # specifics = ProductAttributesField(3, label='a')


    def __init__(self, l, *args, **kwargs):
      self.l = l
      super(ProductForm, self).__init__(*args, **kwargs)
      # self.fields['specifics'] = ProductAttributesField(self.l, label='Thuộc tính đặc trưng')
      for visible in self.visible_fields():
         visible.field.widget.attrs['class'] = 'form-control'
      self.fields['category'].widget.attrs['class'] = 'form-control chosen-select'
      self.fields['duration'].widget.attrs['class'] = 'i - checks pull - left'
      # print(self.l)

    class Meta:
      document = models.product
      fields = ['category', 'name', 'quantity', 'image', 'decription', 'address', 'district', 'city', 'duration', 'startingbid', 'condition']



class ProductAttributesForm(DocumentForm):
    attributes = forms.ChoiceField(choices=models.attributes.objects.values_list('id','name'))
    def __init__(self, *args, **kwargs):
      super(ProductAttributesForm, self).__init__(*args, **kwargs)
      for visible in self.visible_fields():
         visible.field.widget.attrs['class'] = 'form-control'
      self.fields['attributes'].widget.attrs['class'] = 'form-control att x'

    class Meta:
      document = models.product_attributes
      fields = ['attributes', 'content']