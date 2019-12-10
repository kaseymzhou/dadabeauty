import base64
import hashlib
import json
import random
import time
from urllib.parse import urlencode
import redis
import jwt
import requests
from django.core.mail import send_mail
from django.db import transaction
from django.views.generic.base import View
from django.http import HttpResponse, JsonResponse,Http404
from django.shortcuts import render
from .models import UserProfile,WeiboUser,Interests,Interests_User,Follow,Fans
from django.conf import settings
import os
from dtoken.views import make_token
from .tasks import send_active_email
from tools.logging_check import logging_check

# Create your views here.

r = redis.Redis(host='127.0.0.1',port=6379,db=0)

# 用户注册
class Users(View):
    def get(self, request):
        return JsonResponse({'code': 200})
    def post(self, request):
        data = request.body
        if not data:
            result = {'code': '10101', 'error': '请提供完整的注册信息'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        username = json_obj.get('uname')
        password = json_obj.get('password')
        email = json_obj.get('email')
        phone = json_obj.get('phone')
        gender = json_obj.get('gender')
        birthday = json_obj.get('birthday')

        # 检查用户名是否可用
        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {'code': '10102', 'error': '用户名已存在!'}
            return JsonResponse(result)
        # 生成密码哈希
        m = hashlib.md5()
        m.update(password.encode())
        # 创建用户
        try:
            user = UserProfile.objects.create(username=username, password=m.hexdigest(),
                                              email=email, phone=phone,gender=gender,
                                              birthday=birthday)
        except Exception as e:
            result = {'code': '10103', 'error': '用户名已存在!'}
            return JsonResponse(result)
        # 生成、签发token
        # {'code':200, 'username':'xxxx', 'data':{'token':xxxx}}
        token = make_token(username)
        # 发激活邮件
        random_int = random.randint(1000, 9999)
        code_str = username + '_' + str(random_int)
        code_str_bs = base64.urlsafe_b64encode(code_str.encode())
        # 将随机码组合存储在redis中 可以扩展成只存储1-3天
        r.set('email_active_%s' % (username), code_str)
        active_url = 'http://127.0.0.1:7000/dadashop/templates/active.html?code=%s' % (code_str_bs.decode())
        send_active_email.delay(email, active_url)
        return JsonResponse({'code': 200, 'username': username, 'data': {'token': token.decode()}})

# 发送激活邮件函数
def send_active_mail(email, code_url):
    subject = 'DaDa-Beauty用户激活邮件'
    html_message = '''
        <p>亲爱的DaDa-Beauty用户：</p>
        <p>&nbsp;&nbsp;&nbsp;&nbsp;感谢注册达达美妆！</p>
        <p>&nbsp;&nbsp;&nbsp;&nbsp;激活地址为<a href='%s' target='blank'>点击激活</a></p>
        <p>&nbsp;&nbsp;&nbsp;&nbsp;Let's together to feel the charming world and beautify our marvelous life!</p>
        ''' % (code_url)
    send_mail(subject, '', '411180564@qq.com', html_message=html_message, recipient_list=[email])

# 用户账户激活
def users_active(request):
    if request.method != 'GET':
        result = {'code': 10104, 'error': '请使用post方法提交'}
        return JsonResponse(result)
    code = request.GET.get('code')
    if not code:
        pass
    try:
        code_str = base64.urlsafe_b64decode(code.encode())
        # username_9999
        new_code_str = code_str.decode()
        username, rcode = new_code_str.split('_')
    except Exception as e:
        result = {'code': 10105, 'error': 'Your code is wrong!'}
        return JsonResponse(result)
    old_data = r.get('email_active_%s' % (username))
    if not old_data:
        result = {'code': 10106, 'error': 'Your code is wrong!'}
        return JsonResponse(result)
    if code_str != old_data:
        result = {'code': 10107, 'error':'Your code is wrong!!'}
        return JsonResponse(result)
    # 判断完基本信息，开始激活用户
    users = UserProfile.objects.filter(username=username)
    if not users:
        result = {'code': 10108, 'error': 'Your code is wrong!!'}
        return JsonResponse(result)
    user = users[0]
    user.isActive = True
    user.save()
    # 删除redis数据
    r.delete('email_active_%s' % (username))
    result = {'code': 200, 'data':'激活成功'}
    return JsonResponse(result)


class OAuthWeiboUrlView(View):
    def get(self, request):
        # 获取登录地址
        url = get_weibo_login_url()
        return JsonResponse({'code': 200, 'oauth_url': url})

class OAuthWeiboView(View):
    def get(self, request):
        # 获取前端传来的微博code
        code = request.GET.get('code')
        # 向微博服务器发送请求 用code换取token
        # celery.delay()
        try:
            user_info = get_access_token(code)
        except Exception as e:
            print('----get_access_token error')
            print(e)
            result = {'code': 202, 'error':'Weibo server is busy ~'}
            return JsonResponse(result)
        print('------------')
        print(user_info)
        # 微博用户id
        wuid = user_info.get('uid')
        access_token = user_info.get('access_token')
        # 查询weibo用户表，判断是否第一次光临
        try:
            weibo_user = WeiboUser.objects.get(wuid=wuid)
        except Exception as e:
            print('weibouser get error')
            # 该用户第一次用微博登录
            # 创建数据 & 暂时不绑定UserProfile
            WeiboUser.objects.create(access_token=access_token, wuid=wuid)
            data = {'code': '201', 'uid': wuid}
            return JsonResponse(data)
        else:
            # 该用户非第一次微博登录
            # 检查是否进行过绑定
            uid = weibo_user.uid
            if uid:
                # 之前绑定过，则认为当前为正常登陆，照常签发token
                username = uid.username
                token = make_token(username)
                result = {'code': 200, 'username': username, 'data': {'token': token.decode()}}
                return JsonResponse(result)
            else:
                # 之前微博登陆过，但是没有执行微博绑定注册
                data = {'code': '201', 'uid': wuid}
                return JsonResponse(data)
        return JsonResponse({'code': 200, 'error': 'test'})

    def post(self, request):
        # 绑定注册
        # 前端将weiboid命名为uid POST 过来
        # 返回值 跟 正常注册 一样
        data = json.loads(request.body)
        # 获取微博的用户id
        uid = data.get('uid')
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        birthday = data.get('birthday')
        gender = data.get('gender')
        # todo 检查参数是否存在
        m = hashlib.md5()
        m.update(password.encode())
        password_m = m.hexdigest()
        try:
            # 注册用户 事务
            with transaction.atomic():
                user = UserProfile.objects.create(username=username, phone=phone, email=email,
                                                  password=password_m,birthday = birthday,gender = gender)
                weibo_user = WeiboUser.objects.get(wuid=uid)
                # 绑定外键
                weibo_user.uid = user  # 用类属性赋值
                weibo_user.uid_id = user.id  # 用数据库字段赋值
                weibo_user.save()
        except Exception as e:
            print('---weibo register error---')
            print(e)
            return JsonResponse({'code': '10115', 'error': {'message': 'The username is exitsed'}})
        # 签发token
        token = make_token(username)
        result = {'code': 200, 'username': username, 'data': {'token': token.decode()}}
        return JsonResponse(result)
        # todo 发注册邮件
        # return JsonResponse({'code':200})

def get_access_token(code):
    # 向资源授权平台 换取token
    token_url = 'https://api.weibo.com/oauth2/access_token'
    post_data = {'client_id': settings.WEIBO_CLIENT_ID,
                 'client_secret': settings.WEIBO_CLIENT_SECRET,
                 'grant_type': 'authorization_code',
                 'redirect_uri': settings.WEIBO_REDIRECT_URI,
                 'code': code
                 }
    try:
        # 向微博服务器发送post请求
        res = requests.post(token_url, data=post_data)
    except Exception as e:
        print('---weibo request error---')
        print(e)
    if res.status_code == 200:
        return json.loads(res.text)
    raise KeyError

def get_weibo_login_url():
    # response_type - code 代表启用授权码模式
    # scope 授权范围
    params = {'response_type': 'code', 'client_id': settings.WEIBO_CLIENT_ID,
              'redirect_uri': settings.WEIBO_REDIRECT_URI, 'scope': ''}
    weibo_url = 'https://api.weibo.com/oauth2/authorize?'
    url = weibo_url + urlencode(params)
    return url

# 用户挑选感兴趣的部分
def interested(request):
    if request.method == 'GET':
        result = {'code':'10108','error':'请使用post方式提交'}
        return JsonResponse(result)
    elif request.method == 'POST':
        data = request.body
        if not data:
            result = {'code': '10109', 'error': '请提供感兴趣的方面'}
            return JsonResponse(result)
        json_obj = json.loads(data) # {'uid':'01','interests':'1,2,5'}
        intesters_all = json_obj.get('interests') #'1,2,5'
        uid = json_obj.get('uid')
        interests_list = intesters_all.split(',') #['1','2','5']
        user_interests_list = []
        for i in range(len(interests_list)):
            interest = Interests_User.objects.create(uid=uid,iid=interests_list[i])
            user_interests_list.append(Interests.object.filter(id=i).field)
        # 向前端返回数据 例子{'code':200,'data':{'id':1,'user_interests_list':'小清新风','欧美妆容'}}
        result = {'code':200,'data':{'id':uid,'user_interests_list':user_interests_list}}

# 设置头像与个性签名
def further_info(request):
    if request.method == 'GET':
        result = {'code':'10110','error':'请使用post方式提交'}
        return JsonResponse(result)
    elif request.method == 'POST':
        try:
            a_profile = request.FILES['myfile']
            filename =os.path.join(settings.MEDIA_ROOT,a_profile.name)
            with open(filename, 'wb') as f:
                data = a_profile.file.read()
                f.write(data)
        except Exception as e:
            raise Http404
        data = request.body
        json_obj = json.loads(data)
        uid = json_obj.get('uid')
        description = json_obj.get('description')
        if not data:
            return JsonResponse({'code':10111,'error':"请上传头像和个性签名"})
        else:
            # 1.查
            user = UserProfile.objects.filter(id=uid)
            if not user:
                return JsonResponse({'code':10112,'error':'not found the user'})
            user=user[0]
            # 2.改
            user.profile_image_url = '/static/upload_profile/%s'%a_profile.name
            user.description = description
            user.save()
            #3.更新
            profile_image_url = '/static/upload_profile/%s' % a_profile.name
            result = {'uid':uid,'profile_image_url':profile_image_url,'description':description}
            return JsonResponse({'code':200,'data':result})




# 用户被关注
class Fan(View):
    def get(self, request):
        pass
    def post(self,request):
        pass

# 用户关注别人
class Follows(View):
    def get(self, request):
        pass
    def post(self,request):
        pass

# 自动发送生日邮件
class Birthday_email(View):
    def get(self,request):
        pass
    def post(self,request):
        pass

