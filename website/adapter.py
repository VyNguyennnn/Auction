from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from website.models import *
from django.http import HttpResponse


class AccountAdapter(DefaultAccountAdapter):
    def get_signup_redirect_url(self, request):
        shop_user = CSUser.objects.get(email=self.request.user)
        shop_user.is_shop = True
        shop_user.save()
        path = '/registration'
        return path

    def get_login_redirect_url(self, request):
        print('---------------------login request------------')
        print(request.user.username)
        path = '/registration'
        return path


# def email_domain(email):
#     """Extracts the domain from an email address.
#
#     Warning: this is simplified and you may want a true email address parser.
#     """
#     return email.split('@')[-1]
#
#
# # Note: this would be better in settings.py
# allowed_signup_domains = [
#     'student.ctuet.edu.vn',
# ]
#
#
# class SocialAccountAdapter(DefaultSocialAccountAdapter):
#
#     def is_open_for_signup(self, request, sociallogin):
#         if email_domain(sociallogin.user.email) not in allowed_signup_domains:
#             return False
#         return super(SocialAccountAdapter, self).is_open_for_signup(request, sociallogin)

    # def populate_user(self, request, sociallogin, data):
    #     print('jksslslklslskslks')
    #     print(data.get('last_name'))
    #     print(sociallogin.account.extra_data['picture'])
    #     print(sociallogin.account.extra_data)