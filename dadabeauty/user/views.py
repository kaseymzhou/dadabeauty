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
from .tasks import send_active_email
from tools.logging_check import logging_check
from community.models import *
from product.models import *

# Create your views here.

r = redis.Redis(host='127.0.0.1',port=6379,db=0)

# 用户个人主页展示
class PersonalIndex(View):
    @logging_check
    def get(self,request,uid):
        '''
        返给前端的数据结构:
        'data':{
            'username':username,
            'description':description,
            'profile_img':profile_img,
            'blogs':[
                    {'title':title,
                    'content':content
                    'created_time':created_time,
                    'like_count':like_count,
                    'comment_count':comment_count,
                    'forward_count':forward_count},
                    ....
                    ]
                }
        '''
        users = UserProfile.objects.filter(id=uid)
        if not users:
            return JsonResponse({'code':10113,'data':'没找到该用户'})
        user = users[0]
        username = user.username
        description = user.description
        profile_img = user.profile_image_url
        all_blog_list = Blog.objects.filter(uid=uid,isActive=True).order_by('-updated_time')
        if not all_blog_list:
            return JsonResponse({'code':10114,'data':'您还未发表文章'})
        # 只取前三篇
        blog3_list = all_blog_list[:3]
        blogs_list = []
        for item in blog3_list:
            per_blog_info_dic ={}
            per_blog_info_dic['title']=item.title
            per_blog_info_dic['content']=item.content
            per_blog_info_dic['created_time']=item.created_time
            per_blog_info_dic['like_count']=item.like_count
            per_blog_info_dic['comment_count']=item.comment_count
            per_blog_info_dic['forward_count']=item.forward_count
            blogs_list.append(per_blog_info_dic)

        result = {'code':200,'data':{
            'username':username,
            'description':description,
            'profile_img':profile_img,
            'blogs':blogs_list
        }}
        return JsonResponse(result)


# 用户个人主页'我的关注'页面展示
class FocusView(View):
    @logging_check
    def get(self,request,uid):
        '''
                返给前端的数据结构:
                'data':{
                    'uid':uid,
                    'follow_amount':follow_count,
                    'follow_info':[
                                {'followed_username':followed_username,
                                 'followed_profile':followed_profile
                                },
                                {'followed_username':followed_username,
                                 'followed_profile':followed_profile
                                },
                                ....

                                 ]
                        }
                '''
        follow_count = r.hget('fans:amount',uid)
        follows = Follow.objects.filter(fans_id=uid,isActive=True).order_by('-updated_time')
        if not follows:
            return JsonResponse({'code':10115,'data':'你还没有关注过别人哦'})
        follow_info = []
        for item in follows:
            per_follow_info = {}
            followed_id = item.followed_id
            followers = UserProfile.objects.filter(id=followed_id)
            followed_username = followers[0].username
            followed_profile = followers[0].profile_image_url
            per_follow_info['followed_username']=followed_username
            per_follow_info['followed_profile']=followed_profile
            follow_info.append(per_follow_info)
        result = {'code':200,'data':{
            'uid':uid,
            'follow_amount':follow_count,
            'follow_info':follow_info
        }}
        return JsonResponse(result)

# 用户个人主页'我的粉丝'页面展示
class FansView(View):
    @logging_check
    def get(self, request, uid):
        '''
                返给前端的数据结构:
                'data':{
                    'uid':uid,
                    'fans_amount':fans_count,
                    'fans_info':[
                                {'fans_username':fans_username,
                                 'fans_profile':fans_profile
                                },
                                {'fans_username':fans_username,
                                 'fans_profile':fans_profile
                                },
                                ....

                                 ]
                        }
                '''
        fans_count = r.hget('followed_id', uid)
        fans = Follow.objects.filter(followed=uid, isActive=True).order_by('-updated_time')
        if not fans:
            return JsonResponse({'code': 10116, 'data': '你还没有粉丝哦'})
        fans_info = []
        for item in fans:
            per_fans_info = {}
            fans_id = item.fans_id
            fans_profile_info = UserProfile.objects.filter(id=fans_id)
            fans_username = fans_profile_info[0].username
            fans_profile = fans_profile_info[0].profile_image_url
            per_fans_info['fans_username'] = fans_username
            per_fans_info['fans_profile'] = fans_profile
            fans_info.append(per_fans_info)
        result = {'code': 200, 'data': {
            'uid': uid,
            'follow_amount': fans_count,
            'follow_info': fans_info
        }}
        return JsonResponse(result)


# 用户个人主页'收藏商品'页面展示
class CollectProductView(View):
    @logging_check
    def get(self,uid):
        '''
        返给前端的数据结构:
        'data':{
            'uid':uid,
            'blogs':[
                    {'title':title,
                            'content':content
                            'created_time':created_time,
                            'like_count':like_count,
                            'comment_count':comment_count,
                            'forward_count':forward_count},
                    ....
                    ]
                }
        '''
        sku_info_list=[]
        collect_list = Collect.objects.filter(uid=uid,isActive=True).order_by('-updated_time')
        if not collect_list:
            return JsonResponse({'code':10117,'data':'你还没收藏产品哦'})
        for item in collect_list:
            per_sku_info = {}
            sku_id = item.sku_id
            sku_info = Sku.objects.filter(id=sku_id)
            sku_name = sku_info.name
            sku_img = sku_info.default_img_url
            collect_count = r.hget('product:collect',sku_id)
            per_sku_info['sku_name']=sku_name
            per_sku_info['sku_img']=sku_img
            per_sku_info['collect_count']=collect_count
            sku_info_list.append(per_sku_info)
        result = {'code':200,'data':{
                                    'uid':uid,
                                    'sku_info':sku_info_list}
                  }
        return JsonResponse(result)


# 用户个人主页'收藏文章'页面展示
class CollectBlogView(View):
    @logging_check
    def get(self,uid):
        '''
        返给前端的数据结构:
        'data':{
            'uid':uid,
            'blog_info':[
                        {'sku_name':sku_name,
                         'sku_img':sku_img,
                         'collect_count':collect_count
                        },
                        {'sku_name':sku_name,
                         'sku_img':sku_img,
                         'collect_count':collect_count
                        },
                        ....
                         ]
                }
        '''
        all_blog_list = Blog.objects.filter(uid=uid, isActive=True).order_by('-updated_time')
        if not all_blog_list:
            return JsonResponse({'code': 10118, 'data': '您还未发表文章'})
        blogs_list = []
        for item in all_blog_list:
            per_blog_info_dic = {}
            per_blog_info_dic['title'] = item.title
            per_blog_info_dic['content'] = item.content
            per_blog_info_dic['created_time'] = item.created_time
            per_blog_info_dic['like_count'] = item.like_count
            per_blog_info_dic['comment_count'] = item.comment_count
            per_blog_info_dic['forward_count'] = item.forward_count
            blogs_list.append(per_blog_info_dic)

        result = {'code': 200, 'data': {
            'uid': uid,
            'blogs': blogs_list
        }}
        return JsonResponse(result)


# 用户个人主页'修改个人基本信息'页面展示
class ChangePersonalInfo(View):
    @logging_check
    def get(self, request,uid):
        # 返给前端当前用户的基本信息
        user_info = UserProfile.objects.filter(id=uid)
        user_info = user_info[0]
        uid = user_info.uid
        username = user_info.username
        email = user_info.email
        phone = user_info.phone
        gender = user_info.gender
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
    def post(self, request):
        # 接收前端返回来的最新用户信息
        data = request.body
        if not data:
            result = {'code': '10119', 'error': '请提供完整信息'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        uid = json_obj.get('uid')
        username = json_obj.get('username')
        email = json_obj.get('email')
        phone = json_obj.get('phone')
        gender = json_obj.get('gender')
        birthday = json_obj.get('birthday')
        # 检查用户名是否可用
        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {'code': '10120', 'error': '用户名已存在!'}
            return JsonResponse(result)
        # 修改用户信息
        try:
            user = UserProfile.object.filter(id=uid)
            user = user[0]
            user.username = username
            user.email = email
            user.phone = phone
            user.gender = gender
            user.birthday = birthday
            user.save()
        except Exception as e:
            result = {'code': '10121', 'error': '用户名已存在!'}
            return JsonResponse(result)
        # 生成、签发token
        # {'code':200, 'username':'xxxx', 'data':{'token':xxxx}}
        token = make_token(username)
        return JsonResponse({'code': 200, 'username': username, 'data': {'token': token.decode()}})


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
        r.hset('followed:amount', create_uid, 0)
        r.hset('fans:amount', create_uid, 0)
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
        send_active_email.delay(email, active_url)
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
        json_obj = json.loads(data) # {'uid':'01','interests':'1,2,5'}
        intesters_all = json_obj.get('interests') #'1,2,5'
        uid = json_obj.get('uid')
        interests_list = intesters_all.split(',') #['1','2','5']
        user_interests_list = []
        for i in range(len(interests_list)):
            interest = Interests_User.objects.create(uid=uid,iid=interests_list[i])
            user_interests_list.append(Interests.objects.filter(id=i).field)
        # 向前端返回数据 例子{'code':200,'data':{'id':1,'user_interests_list':'小清新风','欧美妆容'}}
        result = {'code':200,'data':{'id':uid,'user_interests_list':user_interests_list}}
        return JsonResponse(result)

# 设置头像与个性签名
class FurtherInfoView(View):
    @logging_check
    def get(self,request):
        return JsonResponse({'code':200})
    @logging_check
    def post(self, request):
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
            profile_image_url = '/static/upload_profile/%s' %a_profile.name
            result = {'uid':uid,'profile_image_url':profile_image_url,'description':description}
            return JsonResponse({'code':200,'data':result})

# 关注用户
class FanView(View):
    @logging_check
    def get(self, request):
        return JsonResponse({'code':10113,'error':'请使用post方式'})
    @logging_check
    def post(self,request):
        data = request.body #{'followed_id':01,'fans_id':02}
        if not data:
            result = {'code': '10101', 'error': '关注失败'}
            return JsonResponse(result)
        else:
            json_obj = json.loads(data)
            followed_id = json_obj.get('followed_id')
            fans_id = json_obj.get('fans_id')
            followed = UserProfile.object.filter(followed_id=followed_id, fans_id=fans_id)
            if not followed:
                # 未关注过该用户
                Follow.objects.create(followed_id=followed_id, fans_id=fans_id)
                r.hincrby('followed:amount', followed_id, 1) # 被关注用户redis粉丝数加1
                r.hincrby('fans:amount',fans_id,1) # 关注了他人的用户redis关注数加1
            else:
                if followed.isActive is False:
                    # 曾经关注过该用户但取消了
                    followed = followed[0]
                    followed.isActive = True
                    followed.save()
                    r.hincrby('followed:amount',followed_id,1) # 被关注用户redis粉丝数加1
                    r.hincrby('fans:amount', fans_id, 1)  # 关注了他人的用户redis关注数加1
                else:
                    return JsonResponse({'code':10114,'data':'关注失败'})
            followed_no = r.hget('followed',followed_id)
            fans_no = r.hget('fans',fans_id)
            result = {'code':200,'data':{'followed_id':followed_id,'fans_id':fans_id,'followed_no':followed_no,
                                         'fans_no':fans_no}}
        return JsonResponse(result)
    @logging_check
    def delete(self,request):
        # 取消关注
        data = request.body  # {'followed_id':01,'fans_id':02}
        if not data:
            result = {'code': '10101', 'error': '取消关注失败'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        followed_id = json_obj.get('followed_id')
        fans_id = json_obj.get('fans_id')
        # 1.查
        followed = UserProfile.objects.filter(followed_id=followed_id,fans_id=fans_id)
        if not followed:
            return JsonResponse({'code': 10112, 'error': 'not found the user'})
        followed = followed[0]
        # 2.改
        followed.isActive = False
        followed.save()
        r.hincrby('followed:amount', followed_id, -1)  # 被关注用户redis粉丝数减1
        r.hincrby('fans:amount', fans_id, -1)  # 关注了他人的用户redis关注数减1
        # 3.更新
        followed_no = r.hget('followed', followed_id)
        fans_no = r.hget('fans', fans_id)
        result = {'code': 200, 'data': {'followed_id': followed_id, 'fans_id': fans_id, 'followed_no': followed_no,
                                        'fans_no': fans_no}}
        return JsonResponse(result)

# 自动发送生日邮件
class Birthday_email(View):
    def get(self,request):
        pass
    def post(self,request):
        pass

