import json
import time
import jwt
from django.conf import settings
from user.models import UserProfile
import hashlib
from django.http import JsonResponse,HttpResponse
from django.shortcuts import render

# Create your views here.
def tokens(request):
    # 登录
    if not request.method == 'POST':
        result = {'code':10001,'error':'请使用post提交'}
        return JsonResponse(result)
    data = request.body
    json_obj = json.loads(data)
    username = json_obj.get('username')
    password = json_obj.get('password')
    #todo 检查参数是否存在
    #查询用户
    user = UserProfile.objects.filter(username=username)
    if not user:
        result = {'code':10002,'error':'用户名或密码错误'}
        return JsonResponse(result)
    user = user[0]
    uid = user.id
    img = settings.PIC_URL + str(user.profile_image_url)
    print(user)
    m = hashlib.md5()
    m.update(password.encode())
    if m.hexdigest() != user.password:
        result = {'code':10003,'error':'用户名或密码错误'}
        return JsonResponse(result)
    # 生成token
    token = make_token(username)
    result = {'code':200,'username':username,'uid':uid,'img':img,'data':{'token':token.decode()}}
    return JsonResponse(result)


def make_token(username, expire=3600 * 24):
    # 注册/登录成功后 签发token 默认一天有效期
    key = settings.JWT_TOKEN_KEY
    now = time.time()
    payload = {'username': username, 'exp': now + expire}
    return jwt.encode(payload, key, algorithm='HS256')