import jwt
from django.conf import settings
from django.http import JsonResponse
from user.models import UserProfile


def logging_check(func):
    def wrapper(self,request,*args,**kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            result = {'code':10209,'error':'Please login'}
            print('logging check no token')
            return JsonResponse(result)
        try:
            res = jwt.decode(token,settings.JWT_TOKEN_KEY,algorithms='HS256')
        except Exception as e:
            print('---jwt error is %s'%e)
            result = {'code':10210,'error':'Please login'}
            return JsonResponse
        username = res['username']
        user = UserProfile.objects.get(username=username)
        request.myuser = user
        # 校验token
        return func(self,request,*args,**kwargs)
    return wrapper