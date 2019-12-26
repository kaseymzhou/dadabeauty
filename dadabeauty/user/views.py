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
from django.http import JsonResponse,Http404
from .models import *
from django.conf import settings
import os
from dtoken.views import make_token
from tools.logging_check import logging_check
from community.models import *
from product.models import *
from .tasks import send_active_mail
# Create your views here.

r = redis.Redis(host='127.0.0.1',port=6379,db=0)

#test
class Test(View):
    def post(self,request):
        return JsonResponse({'code':200})

# 访问他人主页
class OthersProfile(View):
    def get(self,request,ouid):
        ousers = UserProfile.objects.filter(id=ouid)
        ouser = ousers[0]
        img = settings.PIC_URL+str(ouser.profile_image_url)
        username = ouser.username
        description = ouser.description
        data = {'img':img,'username':username,'description':description}
        return JsonResponse({'code':200,'data':data})


# 用户个人主页'我的关注'页面展示
class FocusView(View):
    @logging_check
    def get(self,request,uid):
        follow_count = r.hget('user:%s'%uid,'follow_count')
        follow_count = follow_count.decode()
        follow_object = UserProfile.objects.filter(id=uid)
        follows = FollowUser.objects.filter(fans_id=follow_object[0],isActive=True).order_by('-updated_time')
        if not follows:
            return JsonResponse({'code':10115,'data':'你还没有关注过别人哦'})
        follow_info = []
        for item in follows:
            per_follow_info = {}
            per_follow_info['id'] = item.followed_id.id
            per_follow_info['username'] = item.followed_id.username
            per_follow_info['profile'] = settings.PIC_URL+str(item.followed_id.profile_image_url)
            per_follow_info['description']=item.followed_id.description
            follow_info.append(per_follow_info)
        result = {'code':200,'data':{
                                    'uid':uid,
                                    'follow_count':follow_count,
                                    'follow_info':follow_info}
                  }
        return JsonResponse(result)

# 用户个人主页'我的粉丝'页面展示
class FansView(View):
    @logging_check
    def get(self,request,uid):
        fans_count = r.hget('user:%s'%uid, 'fans_count')
        fans_count = fans_count.decode()
        fans_object = UserProfile.objects.filter(id=uid)
        fans = FollowUser.objects.filter(followed_id=fans_object[0], isActive=True).order_by('-updated_time')
        if not fans:
            return JsonResponse({'code': 10116, 'data': '你还没有粉丝哦'})
        fans_info = []
        for item in fans:
            per_fans_info = {}
            per_fans_info['id'] = item.fans_id.id
            per_fans_info['profile'] = settings.PIC_URL+str(item.fans_id.profile_image_url)
            per_fans_info['username'] = item.fans_id.username
            per_fans_info['description'] = item.fans_id.description
            fans_info.append(per_fans_info)
        result = {'code': 200, 'data': {
                                        'uid': uid,
                                        'fans_count': fans_count,
                                        'fans_info': fans_info}
                  }
        return JsonResponse(result)

# 他人主页'ta的粉丝'页面展示
class OthersFansView(View):
    def get(self,request,username):
        user_object = UserProfile.objects.filter(username=username)
        fans_count = r.hget('user:%s'%user_object[0].id, 'fans_count')
        if not fans_count:
            fans_count = 0
        else:
            fans_count = fans_count.decode()
        fans = FollowUser.objects.filter(followed_id=user_object[0], isActive=True).order_by('-updated_time')
        if not fans:
            return JsonResponse({'code': 10116, 'data': '你还没有粉丝哦'})
        fans_info = []
        for item in fans:
            per_fans_info = {}
            per_fans_info['id'] = item.fans_id.id
            per_fans_info['profile'] = settings.PIC_URL+str(item.fans_id.profile_image_url)
            per_fans_info['username'] = item.fans_id.username
            per_fans_info['description'] = item.fans_id.description
            fans_info.append(per_fans_info)
        result = {'code': 200, 'data': {
                                        'uid': user_object[0].id,
                                        'username':username,
                                        'profile_img':settings.PIC_URL+str(user_object[0].profile_image_url),
                                        'description':user_object[0].description,
                                        'fans_count': fans_count,
                                        'fans_info': fans_info}
                  }
        return JsonResponse(result)

# 他人主页'ta的关注'页面展示
class OthersFocusView(View):
    def get(self,request,username):
        user_object = UserProfile.objects.filter(username=username)
        follow_count = r.hget('user:%s'%user_object[0].id,'follow_count')
        if not follow_count:
            follow_count = 0
        else:
            follow_count = follow_count.decode()
        follows = FollowUser.objects.filter(fans_id=user_object[0],isActive=True).order_by('-updated_time')
        if not follows:
            return JsonResponse({'code':10115,'data':'你还没有关注过别人哦'})
        follow_info = []
        for item in follows:
            per_follow_info = {}
            per_follow_info['id'] = item.followed_id.id
            per_follow_info['username'] = item.followed_id.username
            per_follow_info['profile'] = settings.PIC_URL+str(item.followed_id.profile_image_url)
            per_follow_info['description']=item.followed_id.description
            follow_info.append(per_follow_info)
        result = {'code':200,'data':{
                                    'uid':user_object[0].id,
                                    'username': username,
                                    'profile_img': settings.PIC_URL + str(user_object[0].profile_image_url),
                                    'description': user_object[0].description,
                                    'follow_count':follow_count,
                                    'follow_info':follow_info}
                  }
        return JsonResponse(result)

# 用户个人主页'修改个人基本信息'页面展示
class ChangePersonalInfo(View):
    @logging_check
    def get(self, request,uid):
        # 返给前端当前用户的基本信息
        user_info = UserProfile.objects.filter(id=uid)
        user_info = user_info[0]
        uid = user_info.id
        username = user_info.username
        email = user_info.email
        phone = user_info.phone
        gender = user_info.gender
        if gender == 1:
            gender = '男'
        elif gender == 2:
            gender = '女'
        birthday = user_info.birthday
        return JsonResponse({'code': 200,'data':{
                                                 'uid':uid,
                                                 'username':username,
                                                 'email':email,
                                                 'phone':phone,
                                                 'gender':gender,
                                                 'birthday':birthday}
                             })
    @logging_check
    def post(self, request,uid):
        # 接收前端返回来的最新用户信息
        data = request.body
        if not data:
            result = {'code': '10119', 'error': '请提供完整信息'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        new_username = json_obj.get('username')
        new_email = json_obj.get('email')
        new_phone = json_obj.get('phone')
        new_gender = json_obj.get('gender')
        new_birthday = json_obj.get('birthday')
        # 检查用户名是否可用
        old_user = UserProfile.objects.filter(username=new_username)
        if old_user:
            result = {'code': '10120', 'error': '用户名已存在!'}
            return JsonResponse(result)
        # 修改用户信息
        try:
            user = UserProfile.objects.filter(id=uid)
            user = user[0]
            user.username = new_username
            user.email = new_email
            user.phone = new_phone
            user.gender = new_gender
            user.birthday = new_birthday
            user.save()
        except Exception as e:
            result = {'code': '10121', 'error': '用户名已存在!'}
            return JsonResponse(result)
        # 生成、签发token
        # {'code':200, 'username':'xxxx', 'data':{'token':xxxx}}
        token = make_token(new_username)

        return JsonResponse({'code': 200, 'data': {'token': token.decode(),'username':new_username}})


# 用户个人主页'修改密码'页面展示
class ChangePassword(View):
    @logging_check
    def get(self,request):
        return JsonResponse({'code':200})
    @logging_check
    def get(self,request):
        data = request.body
        if not data:
            result = {'code': '10122', 'error': '请提供完整的信息'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        uid = json_obj.get('uid')
        old_password = json_obj.get('old_password')
        new_password = json_obj.get('new_password')
        m = hashlib.md5()
        m.update(old_password.encode())
        user = UserProfile.objects.filter(id=uid)
        user = user[0]
        old_password_record = user.password
        if old_password_record != m.hexdigest():
            return JsonResponse({'code':'10123','data':'您的旧密码有误'})
        else:
            m.update(new_password.encode())
            user.password = m.hexdigest()
            user.save()
        return JsonResponse({'code':200,'data':'密码修改成功'})


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
        username = json_obj.get('username')
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
        user = UserProfile.objects.filter(username=username)
        user = user[0]
        create_uid = user.id
        r.hset('user:%s'%create_uid, 'follow_count', 0)
        r.hset('user:%s'%create_uid, 'fans_count', 0)
        # 生成、签发token
        # {'code':200, 'username':'xxxx', 'data':{'token':xxxx}}
        token = make_token(username)
        # 发激活邮件
        random_int = random.randint(1000, 9999)
        code_str = username + '_' + str(random_int)
        code_str_bs = base64.urlsafe_b64encode(code_str.encode())
        # 将随机码组合存储在redis中 可以扩展成只存储1-3天
        r.set('email_active_%s' % (username), code_str)
        active_url = 'http://127.0.0.1:7001/dadabeauty/active.html?code=%s' % (code_str_bs.decode())
        # send_active_mail.delay(email, active_url)
        return JsonResponse({'code': 200, 'username': username, 'uid':create_uid,'data': {'token': token.decode()}})

# 发送激活邮件函数
def send_active_mail(email, code_url):
    subject = 'DaDa-Beauty用户激活邮件'
    html_message = '''
        <p>亲爱的DaDa-Beauty用户：</p>
        <p>&nbsp;&nbsp;&nbsp;&nbsp;感谢注册达达美妆！</p>
        <p>&nbsp;&nbsp;&nbsp;&nbsp;激活地址为<a href='%s' target='blank'>点击激活</a></p>
        <p>&nbsp;&nbsp;&nbsp;&nbsp;Let's together to feel the charming world and beautify our marvelous life!</p>
        ''' % (code_url)
    send_mail(subject, '', 'dadabeauty1908@163.com.com', html_message=html_message, recipient_list=[email])

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

class InterestedChoiceView(View):
    @logging_check
    def get(self,request):
        result = {'code':200}
        return JsonResponse(result)
    @logging_check
    def post(self,request):
        data = request.body
        if not data:
            result = {'code': '10109', 'error': '请提供感兴趣的方面'}
            return JsonResponse(result)
        json_obj = json.loads(data) # {'uid':'01','interests':['1,2,5']}
        intesters_all = json_obj.get('interests') #['1,2,5']
        uid = json_obj.get('uid')
        print(intesters_all)
        for item in intesters_all:
            user = UserProfile.objects.filter(id=uid)
            interest = Interests.objects.filter(id=item)
            Interests_User.objects.create(uid=user[0], iid=interest[0])
        # 向前端返回数据 例子{'code':200,'data':{'id':1}
        result = {'code':200,'data':{'id':uid}}
        return JsonResponse(result)

# 设置头像
class ProfileImg(View):
    @logging_check
    def post(self,request,uid):
        user = UserProfile.objects.filter(id=uid)
        user = user[0]
        user.profile_image_url = request.FILES['myfile']
        user.save()
        img = settings.PIC_URL+str(user.profile_image_url)
        print(img)
        return JsonResponse({'code':200,'uid':uid,'img':img})

# 设置个性签名
class PersonDescription(View):
    @logging_check
    def post(self,request):
        data = request.body
        if not data:
            result = {'code': '10141', 'error': '请填写个性签名'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        description = json_obj.get('description')
        uid = json_obj.get('uid')
        user = UserProfile.objects.filter(id=uid)
        user = user[0]
        user.description = description
        user.save()
        return JsonResponse({'code':200,'uid':uid,'person_description':description})


# 关注用户
class AddFan(View):
    @logging_check
    def get(self, request):
        return JsonResponse({'code':10113,'error':'请使用post方式'})
    @logging_check
    def post(self,request):
        data = request.body #{'followed':name,'fans_id':02}
        if not data:
            result = {'code': '10101', 'error': '关注失败'}
            return JsonResponse(result)
        else:
            json_obj = json.loads(data)
            followed = json_obj.get('followed')
            fans_id = json_obj.get('fans_id')
            followeders = UserProfile.objects.filter(username=followed)
            followers = UserProfile.objects.filter(id=fans_id)
            followed = FollowUser.objects.filter(followed_id=followeders[0], fans_id=followers[0])
            # 没有mysql表记录，证明用户动作为关注
            if not followed:
                # 未关注过该用户
                FollowUser.objects.create(followed_id=followeders[0], fans_id=followers[0])
                fans_record = r.hexists('user:%s'%fans_id, 'follow_count')
                follow_record = r.hexists('user:%s' % followeders[0].id, 'fans_count')
                # 粉丝者的关注他人数加1
                if not fans_record:
                    r.hset('user:%s'%fans_id, 'follow_count',0)
                r.hincrby('user:%s'%fans_id, 'follow_count',1)
                # 被关注者的粉丝数加1
                if not follow_record:
                    r.hset('user:%s' % followeders[0].id, 'fans_count', 0)
                r.hincrby('user:%s' % followeders[0].id, 'fans_count', 1)
                result = {'code': 200, 'data': '关注成功'}
                return JsonResponse(result)
            # 有mysql记录，根据记录来看是关注还是取消关注
            else:
                followed = followed[0]
                # 曾经关注过该用户但取消了 --> 现在重新关注
                if followed.isActive is False:
                    followed.isActive = True
                    followed.save()
                    r.hincrby('user:%s' % followeders[0].id, 'fans_count', 1) # 被关注用户redis粉丝数加1
                    r.hincrby('user:%s'%fans_id, 'follow_count',1)  # 关注了他人的用户redis关注数加1
                    result = {'code': 200, 'data': '重新关注成功'}
                    return JsonResponse(result)
                # 已处于关注状态 --> 现在取消关注
                else:
                    followed.isActive = False
                    followed.save()
                    r.hincrby('user:%s' % followeders[0].id, 'fans_count', -1)  # 被关注用户redis粉丝数减1
                    r.hincrby('user:%s' % fans_id, 'follow_count', -1)  # 关注了他人的用户redis关注数减1
                    result = {'code':201,'data':'取消关注成功'}
                    return JsonResponse(result)

# 自动发送生日邮件
class Birthday_email(View):
    def get(self,request):
        pass
    def post(self,request):
        pass

