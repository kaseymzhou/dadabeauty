# 176.122.12.156:7001/dadabeauty/index.html --> dadabeauty网站首页

import redis
from django.http import JsonResponse
from django.utils import timezone
from community.models import Blog, Tag, Forward, Comment, Reply, Collect, Image, Tag_blog,LikeCommunity
from dadabeauty import settings
from tools.logging_check import logging_check
import json
import hashlib
from django.views.generic.base import View
from tools.datetimeseri import JsonCustomEncoder
from user.models import UserProfile

r = redis.Redis(host='127.0.0.1', port=6379, db=1)

# 发表博客页面
class Send_topics(View):
    @logging_check
    def post(self, request):
        # 发表博客
        # http://127.0.0.1:8000/v1/community/sendtopics?authorname=xxx
        author_name = request.GET.get('authorname')
        # json_str = request.body
        # json_obj = json.loads(json_str)
        title = request.POST.get('title')
        if not title:
            result = {'code': 30103, 'error': 'title不得为空!'}
            return JsonResponse(result)
        # 文章内容
        content = request.POST.get('content')
        if not content:
            result = {'code': 30104, 'error': 'content不得为空!'}
            return JsonResponse(result)
        info = title + content[:10]
        unique_key = hashlib.md5(info.encode()).hexdigest()
        # 创建blog
        users = UserProfile.objects.filter(username=author_name)
        Blog.objects.create(unique_key=unique_key, title=title, content=content, uid=users[0])

        # 创建tag
        tag_list = request.POST.get('tags')
        if not tag_list:
            result = {'code': 30102, 'error': 'tag不得为空!'}
            return JsonResponse(result)
        tag_new_list = tag_list.split(',')
        blog_object = Blog.objects.filter(unique_key=unique_key)
        blog_object = blog_object[0]
        for item in tag_new_list:
            tag_object = Tag.objects.filter(tag_name=item)
            tag_object = tag_object[0]
            Tag_blog.objects.create(tag_id_fk=tag_object, blog_id_fk=blog_object)

        # 添加图片
        files = request.FILES.getlist('blogpics')
        print(files)
        for f in files[0:6]:
            dest = open('../dadabeauty/media/blogpics/' + f.name, 'wb+')
            for chunk in f.chunks():
                dest.write(chunk)
                Image.objects.create(b_id=blog_object, image='blogpics/' + f.name)
            dest.close()
            # 图片访问地址  http://127.0.0.1:8000/media/blogpics/文件名  ==>  settings.PIC_URL+str(image表对象.image)
        return JsonResponse({'code': 200})

    @logging_check
    def get(self, request):
        # 获得当前发送博客的界面
        # http://127.0.0.1:8000/v1/community/sendtopics?authorname=xxx
        author_name = request.GET.get('authorname')
        authors = UserProfile.objects.filter(username=author_name)
        if not authors:
            result = {'code': 30105, 'error': 'The author is not existed !'}
            return JsonResponse(result)
        # 当前被访问的博客博主
        author = authors[0]
        tags = Tag.objects.all()
        tags_list = []
        for item in tags:
            tags_list.append(item.tag_name)
        res = {'code': 200, 'username': author.username, 'tags_list': tags_list}
        return JsonResponse(res)

# 不需要登录也可以查看所有博客 -> community模块主页面
def index(request):
    # http://127.0.0.1:8000/v1/community/index  访问所有博客
    if request.method == 'GET':
        tag = request.GET.get('tag_name', 0)
        if tag == 0:  # 周敏已改 if not tag部分
            '''
            反前端数据结构
            'data':[{'bid':bid,
                     'title':title,
                     'content':content,
                     'create_time':create_time,
                     'username':username,
                     'tags':[tag,tag,tag...],
                     'like_count':like_count,
                     'comment_count':comment_count,
                     'forward_count':forward_count,
                     'collect_count':collect_count,
                     'img':[img1,img2,img3...]},
                     {},
                     {},
                ...]
            '''
            blog_send_list = []
            # 取原博客
            blog_list = Blog.objects.filter(is_active=True).order_by('create_time')
            get_first_blog(blog_list, blog_send_list)
            # 取转发博客
            forward_list = Forward.objects.filter(is_active=True).order_by('create_time')
            get_forward_blog(forward_list, blog_send_list)
            # 按照时间排序
            order_by_creatime(blog_send_list)
            result = {'code': 200, 'data': blog_send_list}
            return JsonResponse(result)

        else:
            # http://127.0.0.1:8000/v1/community/index?tag=xxx  访问tag标签博客
            tag = Tag.objects.filter(tag_name=tag)
            if not tag:
                result = {'code': 30106, 'error': '这个标签不存在 !'}
                return JsonResponse(result)
            tag_name = tag[0]['tag_name']
            blog_send_list = []
            # 取原博客
            blog_list = Blog.objects.filter('is_active' == True, 'tag_name' == tag_name).order_by('create_time')
            get_first_blog(blog_list, blog_send_list)
            # 取转发博客
            forward_list = Forward.objects.filter('is_active' == True, 'tag_name' == tag_name).order_by('create_time')
            get_forward_blog(forward_list, blog_send_list)
            # 按照时间排序
            order_by_creatime(blog_send_list)
            result = {'code': 200, 'data': blog_send_list}
            return JsonResponse(result)

    if request.method == 'post':
        result = {'code': 30107, 'error': '请使用GET请求!'}
        return JsonResponse(result)

# 我的主页 -> 已发表博客展示页面
class MyIndex(View):
    @logging_check
    def get(self,request):
        # http://127.0.0.1:8000/v1/community/index?authorname=xxx  访问特定人的博客主页
        authorname = request.GET.get('authorname')
        author_list = UserProfile.objects.filter(username=authorname)
        if not author_list:
            result = {'code': 30108, 'error': '这个用户不存在 !'}
            return JsonResponse(result)
        author = author_list[0]
        blog_send_list = []
        # 取原博客
        blog_list = Blog.objects.filter(is_active=True, uid=author).order_by('-create_time')
        if not blog_list:
            return JsonResponse({'code':30111,'data':'你还没有发表文章哦'})
        else:
            for item in blog_list:
                per_blog_info = {}
                per_blog_info['title']=item.title
                per_blog_info['content']=item.content[:50]+'……'
                per_blog_info['bid'] = item.id
                per_blog_info['create_time']=timezone.localtime(item.create_time).strftime("%b %d %Y %H:%M:%S")
                img_obj = Image.objects.filter(b_id=item)
                if not img_obj:
                    per_blog_info['img'] = ''
                else:
                    per_blog_info['img'] = settings.PIC_URL + str(img_obj[0].image)
                    # 取点赞数
                    like_count_exist = r.hexists('blog:%s' % item.id, 'like')
                    if not like_count_exist:
                        like_count = 0
                    else:
                        like_count = r.hget('blog:%s' % item.id, 'like')
                        like_count = like_count.decode()
                    per_blog_info['like_count'] = like_count
                    # 取转发数
                    forward_count_exist = r.hexists('blog:%s' % item.id, 'forward')
                    if not forward_count_exist:
                        forward_count = 0
                    else:
                        forward_count = r.hget('blog:%s' % item.id, 'forward')
                        forward_count = forward_count.decode()
                    per_blog_info['forward_count'] = forward_count
                    # 取收藏数数
                    collect_count_exist = r.hexists('blog:%s' % item.id, 'collect')
                    if not collect_count_exist:
                        collect_count = 0
                    else:
                        collect_count = r.hget('blog:%s' % item.id, 'collect')
                        collect_count = collect_count.decode()
                    per_blog_info['collect_count'] = collect_count
                    # 取评论数
                    comment_count_exist = r.hexists('blog:%s' % item.id, 'comment')
                    if not comment_count_exist:
                        comment_count = 0
                    else:
                        comment_count = r.hget('blog:%s' % item.id, 'comment')
                        comment_count = comment_count.decode()
                    per_blog_info['comment_count'] = comment_count
                    blog_send_list.append(per_blog_info)
        result = {'code':200,'data':blog_send_list}
        return JsonResponse(result)

        #get_first_blog(blog_list, blog_send_list)
        # 取转发博客
        #forward_list = Forward.objects.filter(is_active=True, uid=author).order_by('create_time')
        #get_forward_blog(forward_list, blog_send_list)
        # 按照时间排序
        #order_by_creatime(blog_send_list)
        #result = {'code': 200, 'data': blog_send_list}

# 删除自己已发表的博客
class DeleteBlog(View):
    @logging_check
    def get(self,request):
        # http://127.0.0.1:8000/v1/community/index?bid=xxx
        bid = request.GET.get('bid')
        blog_obj = Blog.objects.filter(id=bid)
        blog_obj = blog_obj[0]
        blog_obj.is_active = False
        blog_obj.save()
        return JsonResponse({'code':200,'data':'删除成功'})

# 他人主页 -> 已发表博客展示页面
class OtherIndex(View):
    def get(self, request):
        # http://127.0.0.1:8000/v1/community/index?user=xxx  访问特定人的博客主页
        user = request.GET.get('user')
        user_list = UserProfile.objects.filter(username=user)
        if not user_list:
            result = {'code': 30108, 'error': '这个用户不存在 !'}
            return JsonResponse(result)
        user = user_list[0]
        user_info ={}
        user_info['username']=user.username
        user_info['uid']=user.id
        user_info['description']=user.description
        user_info['img'] = settings.PIC_URL + str(user.profile_image_url)
        # 取原博客
        blog_send_list =[]
        blog_list = Blog.objects.filter(is_active=True, uid=user).order_by('-create_time')
        if not blog_list:
            return JsonResponse({'code': 30111, 'data': '你还没有发表文章哦'})
        else:
            for item in blog_list:
                per_blog_info = {}
                per_blog_info['title'] = item.title
                per_blog_info['content'] = item.content[:50] + '……'
                per_blog_info['bid'] = item.id
                per_blog_info['create_time'] = timezone.localtime(item.create_time).strftime("%b %d %Y %H:%M:%S")
                img_obj = Image.objects.filter(b_id=item)
                if not img_obj:
                    per_blog_info['img'] = ''
                else:
                    per_blog_info['img'] = settings.PIC_URL + str(img_obj[0].image)
                    # 取点赞数
                    like_count_exist = r.hexists('blog:%s' % item.id, 'like')
                    if not like_count_exist:
                        like_count = 0
                    else:
                        like_count = r.hget('blog:%s' % item.id, 'like')
                        like_count = like_count.decode()
                    per_blog_info['like_count'] = like_count
                    # 取转发数
                    forward_count_exist = r.hexists('blog:%s' % item.id, 'forward')
                    if not forward_count_exist:
                        forward_count = 0
                    else:
                        forward_count = r.hget('blog:%s' % item.id, 'forward')
                        forward_count = forward_count.decode()
                    per_blog_info['forward_count'] = forward_count
                    # 取收藏数数
                    collect_count_exist = r.hexists('blog:%s' % item.id, 'collect')
                    if not collect_count_exist:
                        collect_count = 0
                    else:
                        collect_count = r.hget('blog:%s' % item.id, 'collect')
                        collect_count = collect_count.decode()
                    per_blog_info['collect_count'] = collect_count
                    # 取评论数
                    comment_count_exist = r.hexists('blog:%s' % item.id, 'comment')
                    if not comment_count_exist:
                        comment_count = 0
                    else:
                        comment_count = r.hget('blog:%s' % item.id, 'comment')
                        comment_count = comment_count.decode()
                    per_blog_info['comment_count'] = comment_count
                    blog_send_list.append(per_blog_info)
        result = {'code': 200, 'data': blog_send_list,'user':user_info}
        return JsonResponse(result)

# 我的主页 -> 收藏博客展示页面
class MyIndexCollect(View):
    @logging_check
    def get(self,request):
    # http://127.0.0.1:8000/v1/community/index_collect?authorname=xxx  访问我的收藏列表
        authorname = request.GET.get('authorname')
        author_list = UserProfile.objects.filter(username=authorname)
        if not author_list:
            result = {'code': 30108, 'error': '这个用户不存在 !'}
            return JsonResponse(result)
        author = author_list[0]
        collect_send_list = get_collect_blogs(author)
        result = {'code': 200, 'data': collect_send_list}
        return JsonResponse(result)
    def post(self,request):
        result = {'code': 30107, 'error': '请使用GET请求!'}
        return JsonResponse(result)

# 他人主页 -> 收藏博客展示页面
class OtherIndexCollect(View):
    def get(self, request):
        # http://127.0.0.1:8000/v1/community/index_collect?user=xxx  访问特定人的收藏列表
        user = request.GET.get('user')
        user_list = UserProfile.objects.filter(username=user)
        if not user_list:
            result = {'code': 30108, 'error': '这个用户不存在 !'}
            return JsonResponse(result)
        user = user_list[0]
        user_info = {}
        user_info['username'] = user.username
        user_info['uid'] = user.id
        user_info['description'] = user.description
        user_info['img'] = settings.PIC_URL + str(user.profile_image_url)
        collect_send_list = get_collect_blogs(user)
        result = {'code': 200, 'data': collect_send_list,'user':user_info}
        return JsonResponse(result)

    def post(self, request):
        result = {'code': 30107, 'error': '请使用GET请求!'}
        return JsonResponse(result)

# 博客详细内容页面
class DeatilBlog(View):
    def post(self,request):
        result = {'code': 30107, 'error': '请使用GET请求!'}
        return JsonResponse(result)

    def get(self,request):
        # http://127.0.0.1:8000/v1/community/detail?blogid=xxx
        id = request.GET.get('blogid')
        try:
            blog = Blog.objects.filter(id=id)
            blog = blog[0]
        except Exception as e:
            print('获得博客错误\n', e)
            result = {'code': 30108, 'error': '请给我博客id!'}
            return JsonResponse(result)
        # 获取博客详情
        result = get_detail_blog(blog)
        return JsonResponse(result)

# 转发博客
class ForwardBlog(View):
    @logging_check
    def get(self,request):
        result = {'code': 30109, 'error': '请给我POST请求!'}
        return JsonResponse(result)

    @logging_check
    def post(self,request):
        # http://127.0.0.1:8000/v1/community/forward?authorname=xxx
        author_name = request.GET.get('authorname')
        json_str = request.body
        json_obj = json.loads(json_str)
        content = json_obj.get('content')
        blog_id = json_obj.get('id')
        blog_object = Blog.objects.filter(id=blog_id)
        user_object = UserProfile.objects.filter(username=author_name)
        Forward.objects.create(content=content, uid=user_object[0], b_id=blog_object[0])
        # 统计转发数
        forward_count_exist = r.hexists('blog:%s' % blog_id, 'forward')
        if not forward_count_exist:
            r.hset('blog:%s' % blog_id, 'forward', 0)
        r.hincrby('blog:%s' % blog_id, 'forward', 1)
        result = {'code': 200, 'data':'转发成功'}
        return JsonResponse(result)

# 点赞博客
class LikeBlog(View):
    @logging_check
    def get(self,request):
    # http://127.0.0.1:8000/v1/community/like?authorname=xxx&blogid=xxx
        author_name = request.GET.get('authorname')
        blog_id = request.GET.get('blogid')
        user_obj = UserProfile.objects.filter(username=author_name)
        blog_obj = Blog.objects.filter(id=blog_id)
        like_record = LikeCommunity.objects.filter(uid=user_obj[0],blog_id=blog_obj[0])
        if not like_record:
            # 点赞
            LikeCommunity.objects.create(uid=user_obj[0],blog_id=blog_obj[0])
            # 统计转发数'blog:%s' % item.id, 'like'
            like_count_exist = r.hexists('blog:%s' % blog_id, 'like')
            if not like_count_exist:
                r.hset('blog:%s' % blog_id, 'like', 0)
            r.hincrby('blog:%s' % blog_id, 'like', 1)
            result = {'code': 200,'data':'点赞成功'}
            return JsonResponse(result)
        else:
            like_record = like_record[0]
            # 取消点赞
            if like_record.is_active == True:
                like_record.is_active = False
                like_record.save()
                r.hincrby('blog:%s' % blog_id, 'like', -1)
                result = {'code': 201, 'data': '取消点赞成功'}
                return JsonResponse(result)
            # 重新点赞
            else:
                like_record.is_active = True
                like_record.save()
                r.hincrby('blog:%s' % blog_id, 'like', 1)
                result = {'code': 200, 'data': '点赞成功'}
                return JsonResponse(result)

    @logging_check
    def post(self,request):
        result = {'code': 30107, 'error': '请使用GET请求!'}
        return JsonResponse(result)

# 评论
class BlogComment(View):
    @logging_check
    def post(self,request):
        data = request.body
        if not data:
            result = {'code': '30111', 'error': '请填写评论'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        blog_id = json_obj.get('blog_id')
        content = json_obj.get('content')
        uid = json_obj.get('uid')
        user_obj = UserProfile.objects.filter(id=uid)
        blog_obj = Blog.objects.filter(id=blog_id)
        Comment.objects.create(content=content, uid=user_obj[0], b_id=blog_obj[0])

        # 判断是否在redis中曾经有设立过计数key
        blog_comment_count = r.hexists('blog:%s' % blog_id, 'comment')
        if not blog_comment_count:
            r.hset('blog:%s' % blog_id, 'comment', 0)
        # redis做评论计数
        r.hincrby('blog:%s' % blog_id, 'comment', 1)
        result = {'code': 200, 'data': '评论成功'}
        return JsonResponse(result)

    @logging_check
    def delete(self,request):
        data = request.body
        if not data:
            result = {'code': '30112', 'error': '删除失败'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        comment_id = json_obj.get('comment_id')
        comments = Comment.objects.filter(id=comment_id)
        if not comments:
            return JsonResponse({'code': '30113', 'error': '无法删除该评论'})
        comment = comments[0]
        # 修改评论isActive属性为False
        comment.isActive = False
        comment.save()
        # redis做评论计数
        blog_id = comment.b_id
        r.hincrby('blog:%s' % blog_id, 'comment', -1)
        result = {'code': 200, 'data': '删除评论成功'}
        return JsonResponse(result)

# 回复评论（二级评论）
class BlogReply(View):
    @logging_check
    def post(self,request):
        data = request.body
        if not data:
            result = {'code': '30114', 'error': '请填写回复信息'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        content = json_obj.get('content')
        uid = json_obj.get('uid')
        c_id = json_obj.get('c_id')
        # mysql数据库录入
        user_obj = UserProfile.objects.filter(id=uid)
        comment_obj = Comment.objects.filter(id=c_id)
        Reply.objects.create(content=content, uid=user_obj[0], c_id=comment_obj[0])
        # redis做评论计数
        blog_id = comment_obj[0].b_id.id
        r.hincrby('blog:%s' % blog_id, 'comment', 1)
        result = {'code': 200, 'data': '回复成功'}
        return JsonResponse(result)

    @logging_check
    def delete(self,request):
        data = request.body
        if not data:
            result = {'code': '30115', 'error': '删除失败'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        reply_id = json_obj.get('reply_id')
        replies = Reply.objects.filter(id=reply_id)
        if not replies:
            return JsonResponse({'code': 30116, 'error': '无法删除该回复'})
        reply = replies[0]
        reply.is_active = False
        reply.save()
        # redis做评论计数
        c_id = reply.c_id
        comments = Comment.objects.filter(id=c_id)
        if not comments:
            return JsonResponse({'code': '30113', 'error': '无法删除该评论'})
        comment = comments[0]
        blog_id = comment.b_id
        r.hincrby('blog:%s' % blog_id, 'comment', 1)
        result = {'code': 200, 'data': '删除回复成功'}
        return JsonResponse(result)

# 收藏博客文章
class CollectBlogs(View):
    @logging_check
    def post(self,request):
        result = {'code': 30117, 'error': '请给我GET请求!'}
        return JsonResponse(result)
    @logging_check
    def get(self,request):
        # http://127.0.0.1:8000/v1/community/collect?authorname=xxx&id=xxx
        author_name = request.GET.get('authorname')
        blog_id = request.GET.get('id')
        user_obj = UserProfile.objects.filter(username=author_name)
        blog_object = Blog.objects.filter(id=blog_id)
        collect_record = Collect.objects.filter(uid=user_obj[0],b_id=blog_object[0])
        if not collect_record:
            Collect.objects.create(uid=user_obj[0],b_id=blog_object[0])
            collect_count_exist = r.hexists('blog:%s' % blog_id, 'collect')
            if not collect_count_exist:
                r.hset('blog:%s' % blog_id, 'collect', 0)
            r.hincrby('blog:%s' % blog_id, 'collect', 1)
            result = {'code': 200, 'data': '收藏成功'}
            return JsonResponse(result)
        else:
            collect_record = collect_record[0]
            if collect_record.is_active==True:
                collect_record.is_active=False
                collect_record.save()
                r.hincrby('blog:%s' % blog_id, 'collect', -1)
                result = {'code': 201, 'data': '取消收藏成功'}
                return JsonResponse(result)
            else:
                collect_record.is_active = True
                collect_record.save()
                r.hincrby('blog:%s' % blog_id, 'collect', 1)
                result = {'code': 200, 'data': '收藏成功'}
                return JsonResponse(result)

# def 取原博客
def get_first_blog(blog_list, blog_send_list):
    for item in blog_list:
        per_blog = {}
        per_blog['code'] = 201
        per_blog['bid'] = item.id
        per_blog['title'] = item.title
        per_blog['content'] = item.content
        per_blog['username'] = item.uid.username
        per_blog['profile_img'] = settings.PIC_URL+str(item.uid.profile_image_url)
        per_blog['create_time'] = timezone.localtime(item.create_time).strftime("%b %d %Y %H:%M:%S")
        per_blog['order_create_time'] = item.create_time
        tags_object_list = Tag_blog.objects.filter(blog_id_fk=item)
        total_tags_list = []
        # 取tag
        for tag_obj in tags_object_list:
            per_tag_name = tag_obj.tag_id_fk.tag_name
            total_tags_list.append(per_tag_name)
        per_blog['tags'] = total_tags_list
        # 取点赞数
        like_count_exist = r.hexists('blog:%s' % item.id, 'like')
        if not like_count_exist:
            like_count = 0
        else:
            like_count = r.hget('blog:%s' % item.id, 'like')
            like_count = like_count.decode()
        per_blog['like_count'] = like_count
        # 取转发数
        forward_count = r.hexists('blog:%s' % item.id, 'forward')
        if not forward_count:
            forward_count = 0
        else:
            forward_count = r.hget('blog:%s' % item.id, 'forward')
            forward_count = forward_count.decode()
        per_blog['forward_count'] = forward_count
        # 取收藏数数
        collect_count_exist = r.hexists('blog:%s' % item.id, 'collect')
        if not collect_count_exist:
            collect_count = 0
        else:
            collect_count = r.hget('blog:%s' % item.id, 'collect')
            collect_count = collect_count.decode()
        per_blog['collect_count'] = collect_count
        # 取评论数
        comment_count_exist = r.hexists('blog:%s' % item.id, 'comment')
        if not comment_count_exist:
            comment_count = 0
        else:
            comment_count = r.hget('blog:%s' % item.id, 'comment')
            comment_count = comment_count.decode()
        per_blog['comment_count'] = comment_count
        # 取图片
        images = Image.objects.filter(b_id=item)
        image_list = []
        for item in images:
            image_list.append(settings.PIC_URL + str(item.image))
        per_blog['img'] = image_list
        blog_send_list.append(per_blog)

# def 取博客详细信息
def get_detail_blog(blog):
    # 获取用户名
    data = {}
    data['username'] = blog.uid.username
    data['profile_img'] = settings.PIC_URL + str(blog.uid.profile_image_url)
    # 获取题目
    data['title'] = blog.title
    tags_object_list = Tag_blog.objects.filter(blog_id_fk=blog)
    total_tags_list = []
    # 取tag
    for tag_obj in tags_object_list:
        per_tag_name = tag_obj.tag_id_fk.tag_name
        total_tags_list.append(per_tag_name)
    data['tags'] = total_tags_list
    # 取内容
    data['content'] = blog.content
    # 取时间
    data['create_time'] = timezone.localtime(blog.create_time).strftime("%b %d %Y %H:%M:%S")
    # 取点赞数
    like_count_exist = r.hexists('blog:%s' % blog.id, 'like')
    if not like_count_exist:
        like_count = 0
    else:
        like_count = r.hget('blog:%s' % blog.id, 'like')
        like_count = like_count.decode()
    data['like_count'] = like_count
    # 取转发数
    forward_count = r.hexists('blog:%s' % blog.id, 'forward')
    if not forward_count:
        forward_count = 0
    else:
        forward_count = r.hget('blog:%s' % blog.id, 'forward')
        forward_count = forward_count.decode()
    data['forward_count'] = forward_count
    # 取收藏数数
    collect_count_exist = r.hexists('blog:%s' % blog.id, 'collect')
    if not collect_count_exist:
        collect_count = 0
    else:
        collect_count = r.hget('blog:%s' % blog.id, 'collect')
        collect_count = collect_count.decode()
    data['collect_count'] = collect_count
    # 取评论数
    comment_count_exist = r.hexists('blog:%s' % blog.id, 'comment')
    if not comment_count_exist:
        comment_count = 0
    else:
        comment_count = r.hget('blog:%s' % blog.id, 'comment')
        comment_count = comment_count.decode()
    data['comment_count'] = comment_count
    # 取图片
    images = Image.objects.filter(b_id=blog)
    image_list = []
    for item in images:
        image_list.append(settings.PIC_URL + str(item.image))
    data['img'] = image_list
    # 取评论
    per_comment_detail_dic = []
    comments = Comment.objects.filter(b_id=blog, is_active=True)
    for item in comments:
        one_comment_info = {}
        c_id = item.id
        one_comment_info['comment_id'] = c_id
        uid = item.uid.id
        users = UserProfile.objects.filter(id=uid)
        if not users:
            return JsonResponse({'code': 30112, 'data': '查看该用户评论失败'})
        comment_username = users[0].username
        one_comment_info['comment_username'] = comment_username
        comment_user_profile = users[0].profile_image_url
        one_comment_info['comment_user_profile'] = settings.PIC_URL + str(comment_user_profile)
        one_comment_info['comment_content'] = item.content
        one_comment_info['create_time'] = timezone.localtime(item.create_time).strftime("%b %d %Y %H:%M:%S")

        # 获取每条评论对应的回复
        replies = Reply.objects.filter(c_id=item, is_active=True)
        replies_dic = []
        for item in replies:
            one_reply_info_detail = {}
            users = UserProfile.objects.filter(id=item.uid.id)
            reply_username = users[0].username
            reply_profile = settings.PIC_URL + str(users[0].profile_image_url)
            reply_content = item.content
            one_reply_info_detail['reply_username'] = reply_username
            one_reply_info_detail['reply_profile'] = reply_profile
            one_reply_info_detail['reply_content'] = reply_content
            one_reply_info_detail['create_time'] =  timezone.localtime(item.create_time).strftime("%b %d %Y %H:%M:%S")
            replies_dic.append(one_reply_info_detail)
        one_comment_info['comment_replies'] = replies_dic
        per_comment_detail_dic.append(one_comment_info)
    data['comment_detail'] = per_comment_detail_dic
    # 返回数据
    result = {'code': 200, 'data': data}
    return result

# def 取转发博客
def get_forward_blog(forward_list, blog_send_list):
    for item in forward_list:
        forward_blog = {}
        forward_blog['code'] = 202
        forward_blog['fid'] = item.id
        forward_blog['fcontent'] = item.content
        forward_blog['fusername'] = item.uid.username
        forward_blog['profile_img'] = settings.PIC_URL+str(item.uid.profile_image_url)
        forward_blog['create_time'] =  timezone.localtime(item.create_time).strftime("%b %d %Y %H:%M:%S")
        forward_blog['order_create_time'] = item.create_time
        blog_object = item.b_id
        forward_blog['id'] = blog_object.id
        forward_blog['title'] = blog_object.title
        forward_blog['content'] = blog_object.content
        forward_blog['username'] = blog_object.uid.username
        forward_blog['ocreate_time'] = blog_object.create_time
        forward_blog['oprofile_img'] = settings.PIC_URL + str(blog_object.uid.profile_image_url)
        tags_object_list = Tag_blog.objects.filter(blog_id_fk=blog_object)
        total_tags_list = []
        # 取tag
        for tag_obj in tags_object_list:
            per_tag_name = tag_obj.tag_id_fk.tag_name
            total_tags_list.append(per_tag_name)
        forward_blog['tags'] = total_tags_list
        # 取点赞数
        like_count_exist = r.hexists('blog:%s' % blog_object.id, 'like')
        if not like_count_exist:
            like_count = 0
        else:
            like_count = r.hget('blog:%s' % blog_object.id, 'like')
            like_count = like_count.decode()
        forward_blog['like_count'] = like_count
        # 取转发数
        forward_count_exist = r.hexists('blog:%s' % blog_object.id, 'forward')
        if not forward_count_exist:
            forward_count = 0
        else:
            forward_count = r.hget('blog:%s' % blog_object.id, 'forward')
            forward_count = forward_count.decode()
        forward_blog['forward_count'] = forward_count
        # 取收藏数数
        collect_count_exist = r.hexists('blog:%s' % blog_object.id, 'collect')
        if not collect_count_exist:
            collect_count = 0
        else:
            collect_count = r.hget('blog:%s' % blog_object.id, 'collect')
            collect_count = collect_count.decode()
        forward_blog['collect_count'] = collect_count
        # 取评论数
        comment_count_exist = r.hexists('blog:%s' % blog_object.id, 'comment')
        if not comment_count_exist:
            comment_count = 0
        else:
            comment_count = r.hget('blog:%s' % blog_object.id, 'comment')
            comment_count = comment_count.decode()
        forward_blog['comment_count'] = comment_count
        # 取图片
        images = Image.objects.filter(b_id=blog_object)
        image_list = []
        for item in images:
            image_list.append(settings.PIC_URL + str(item.image))
        forward_blog['img'] = image_list
        blog_send_list.append(forward_blog)

# def 将原创博客与转发博客进行时间排序
def order_by_creatime(blog_send_list):
    for r in range(0, len(blog_send_list) - 1):
        for c in range(r, len(blog_send_list)):
            if blog_send_list[r]['order_create_time'] < blog_send_list[c]['order_create_time']:
                blog_send_list[r], blog_send_list[c] = blog_send_list[c], blog_send_list[r]

# def 取收藏的博客信息列表
def get_collect_blogs(person):
    collect_send_list = []
    # 取收藏博客
    collect_list = Collect.objects.filter(is_active=True, uid=person).order_by('-create_time')
    if not collect_list:
        return JsonResponse({'code': 30112, 'data': '还没有收藏文章哦'})
    else:
        for item in collect_list:
            per_blog_info = {}
            per_blog_info['title'] = item.b_id.title
            per_blog_info['content'] = item.b_id.content[:50] + '……'
            per_blog_info['bid'] = item.b_id.id
            per_blog_info['create_time'] = timezone.localtime(item.b_id.create_time).strftime("%b %d %Y %H:%M:%S")
            img_obj = Image.objects.filter(b_id=item.b_id)
            if not img_obj:
                per_blog_info['img'] = ''
            else:
                per_blog_info['img'] = settings.PIC_URL + str(img_obj[0].image)
                # 取点赞数
                like_count_exist = r.hexists('blog:%s' % item.b_id.id, 'like')
                if not like_count_exist:
                    like_count = 0
                else:
                    like_count = r.hget('blog:%s' % item.b_id.id, 'like')
                    like_count = like_count.decode()
                per_blog_info['like_count'] = like_count
                # 取转发数
                forward_count_exist = r.hexists('blog:%s' % item.b_id.id, 'forward')
                if not forward_count_exist:
                    forward_count = 0
                else:
                    forward_count = r.hget('blog:%s' % item.b_id.id, 'forward')
                    forward_count = forward_count.decode()
                per_blog_info['forward_count'] = forward_count
                # 取收藏数数
                collect_count_exist = r.hexists('blog:%s' % item.b_id.id, 'collect')
                if not collect_count_exist:
                    collect_count = 0
                else:
                    collect_count = r.hget('blog:%s' % item.b_id.id, 'collect')
                    collect_count = collect_count.decode()
                per_blog_info['collect_count'] = collect_count
                # 取评论数
                comment_count_exist = r.hexists('blog:%s' % item.b_id.id, 'comment')
                if not comment_count_exist:
                    comment_count = 0
                else:
                    comment_count = r.hget('blog:%s' % item.b_id.id, 'comment')
                    comment_count = comment_count.decode()
                per_blog_info['comment_count'] = comment_count
                collect_send_list.append(per_blog_info)
        return collect_send_list