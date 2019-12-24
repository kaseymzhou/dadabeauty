# 176.122.12.156:7001/dadabeauty/index.html --> dadabeauty网站首页

import redis
from django.http import JsonResponse
from community.models import Blog, Tag, Forward, Comment, Reply, Collect, Image, Tag_blog
from dadabeauty import settings
from tools.logging_check import logging_check
import json
import hashlib
from django.views.generic.base import View

from user.models import UserProfile

r = redis.Redis(host='127.0.0.1', port=6379, db=1)


# 发表博客文章（已完成）
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
        for f in files:
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


# 不需要登录也可以查看所有博客
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


@logging_check
def my_index(request):
    # http://127.0.0.1:8000/v1/community/index?authorname=xxx  访问特定人的博客主页
    if request.method == 'GET':
        authorname = request.GET.get('authorname')
        author_list = UserProfile.objects.filter(authorname=authorname)
        if not author_list:
            result = {'code': 30108, 'error': '这个用户不存在 !'}
            return JsonResponse(result)
        author = author_list[0]
        blog_send_list = []
        # 取原博客
        blog_list = Blog.objects.filter('is_active' == True, 'uid' == author.id).order_by('create_time')
        get_first_blog(blog_list, blog_send_list)
        # 取转发博客
        forward_list = Forward.objects.filter('is_active' == True, 'uid' == author.id).order_by('create_time')
        get_forward_blog(forward_list, blog_send_list)
        # 按照时间排序
        order_by_creatime(blog_send_list)
        result = {'code': 200, 'data': blog_send_list}
        return JsonResponse(result)

    if request.method == 'POST':
        result = {'code': 30107, 'error': '请使用GET请求!'}
        return JsonResponse(result)


@logging_check
def my_index_collect(request):
    # http://127.0.0.1:8000/v1/community/index_collect?authorname=xxx  访问特定人的收藏列表
    if request.method == 'GET':
        authorname = request.GET.get('authorname')
        author_list = UserProfile.objects.filter(authorname=authorname)
        if not author_list:
            result = {'code': 30108, 'error': '这个用户不存在 !'}
            return JsonResponse(result)
        author = author_list[0]
        blog_send_list = []
        # 取收藏博客
        collect_list = Collect.objects.filter('is_active' == True, 'uid' == author.id).order_by('create_time')
        get_collect_blog(collect_list, blog_send_list)
        result = {'code': 200, 'data': blog_send_list}
        return JsonResponse(result)
    if request.method == 'POST':
        result = {'code': 30107, 'error': '请使用GET请求!'}
        return JsonResponse(result)


@logging_check
def detail_blog(request):
    id = request.GET.get('blogid')
    userme = request.myuser
    if request.method == 'POST':
        result = {'code': 30107, 'error': '请使用GET请求!'}
        return JsonResponse(result)

    if request.method == 'DELETE':
        # http://127.0.0.1:8000/v1/community/detail?blogid=xxx
        try:
            blog = Blog.objects.get(id=id)
            blog.is_active = False
            blog.save()
        except Exception as e:
            print('删除博客错误\n', e)
            result = {'code': 30108, 'error': '请给我博客id!'}
            return JsonResponse(result)
        result = {'code': 200, 'username': userme}
        return JsonResponse(result)

    if request.method == 'GET':
        # http://127.0.0.1:8000/v1/community/detail?blogid=xxx
        try:
            blog = Blog.objects.get(id=id)
        except Exception as e:
            print('获得博客错误\n', e)
            result = {'code': 30108, 'error': '请给我博客id!'}
            return JsonResponse(result)
        # 获取博客详情
        result = get_detail_blog(blog)
        return JsonResponse(result)


@logging_check
def forward_blog(request):
    if request.method == 'GET':
        result = {'code': 30109, 'error': '请给我POST请求!'}
        return JsonResponse(result)

    if request.method == 'POST':
        # http://127.0.0.1:8000/v1/community/forward?authorname=xxx
        author_name = request.GET.get('authorname')
        author = request.myuser
        if author.username != author_name:
            result = {'code': 30101, 'error': '非本人操作!'}
            return JsonResponse(result)
        json_str = request.body
        json_obj = json.loads(json_str)
        content = json_obj.get('content')
        blog_id = json_obj.get('id')
        blog_object = Blog.objects.get(id=blog_id)
        Forward.objects.create(content=content, uid=author, b_id=blog_object)
        # 统计转发数
        forward_count_exist = r.hexists('blog:%s' % blog_id, 'forward')
        if forward_count_exist is False:
            r.hset('blog:%s' % blog_id, 'forward', 0)
        r.hincrby('blog:%s' % blog_id, 'forward', 1)
        result = {'code': 200, 'username': author}
        return JsonResponse(result)


@logging_check
def like_blog(request):
    if request.method == 'GET':
        # http://127.0.0.1:8000/v1/community/like?authorname=xxx&blogid=xxx
        author_name = request.GET.get('authorname')
        author = request.myuser
        if author.username != author_name:
            result = {'code': 30101, 'error': '非本人操作!'}
            return JsonResponse(result)
        blog_id = request.GET.get('blogid')
        # 统计转发数'blog:%s' % item.id, 'like'
        like_count_exist = r.hexists('blog:%s' % blog_id, 'like')
        if like_count_exist is False:
            r.hset('blog:%s' % blog_id, 'like', 0)
        r.hincrby('blog:%s' % blog_id, 'like', 1)
        result = {'code': 200, 'username': author}
        return JsonResponse(result)
    else:
        result = {'code': 30107, 'error': '请使用GET请求!'}
        return JsonResponse(result)


@logging_check
def unlike(request):
    if request.method == 'GET':
        # http://127.0.0.1:8000/v1/community/unlike?authorname=xxx&blogid=xxx
        author_name = request.GET.get('authorname')
        author = request.myuser
        if author.username != author_name:
            result = {'code': 30101, 'error': '非本人操作!'}
            return JsonResponse(result)
        blog_id = request.GET.get('blogid')
        # 统计转发数
        like_count_exist = r.hexists('blog:%s' % blog_id, 'like')
        if like_count_exist is False:
            r.hset('blog:%s' % blog_id, 'like', 0)
        r.hincrby('blog:%s' % blog_id, 'like', -1)
        result = {'code': 200, 'username': author}
        return JsonResponse(result)
    else:
        result = {'code': 30107, 'error': '请使用GET请求!'}
        return JsonResponse(result)


@logging_check
def comment(request):
    if request.method == 'POST':
        data = request.body
        if not data:
            result = {'code': '30111', 'error': '请填写评论'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        blog_id = json_obj.get('blog_id')
        content = json_obj.get('content')
        uid = json_obj.get('uid')
        Comment.objects.create(content=content, uid=uid, b_id=blog_id)

        # 判断是否在redis中曾经有设立过计数key
        blog_comment_count = r.hexists('blog:%s' % blog_id, 'comment')
        if blog_comment_count is False:
            r.hset('blog:%s' % blog_id, 'comment', 0)
        # redis做评论计数
        r.hincrby('blog:%s' % blog_id, 'comment', 1)
        result = {'code': 200, 'data': '评论成功'}
        return JsonResponse(result)

    if request.method == 'DELETE':
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


# 评论的回复
@logging_check
def reply(request):
    if request.method == 'POST':
        data = request.body
        if not data:
            result = {'code': '30114', 'error': '请填写回复信息'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        content = json_obj.get('content')
        uid = json_obj.get('uid')
        c_id = json_obj.get('c_id')
        # mysql数据库录入
        Reply.objects.create(content=content, uid=uid, c_id=c_id)
        # redis做评论计数
        comments = Comment.objects.filter(id=c_id)
        if not comments:
            return JsonResponse({'code': '30113', 'error': '无法删除该评论'})
        comment = comments[0]
        blog_id = comment.b_id
        r.hincrby('blog:%s' % blog_id, 'comment', 1)
        result = {'code': 200, 'data': '回复成功'}
        return JsonResponse(result)
    if request.method == 'DELETE':
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


@logging_check
def collect_blog(request):
    if request.method == 'POST':
        result = {'code': 30117, 'error': '请给我GET请求!'}
        return JsonResponse(result)

    if request.method == 'GET':
        # http://127.0.0.1:8000/v1/community/collect?authorname=xxx,id=xxx
        author_name = request.GET.get('authorname')
        author = request.myuser
        if author.username != author_name:
            result = {'code': 30101, 'error': '非本人操作!'}
            return JsonResponse(result)
        blog_id = request.GET.get('id')
        blog_object = Blog.objects.get(id=blog_id)
        Collect.objects.create(uid=author, b_id=blog_object)
        # 统计收藏数
        collect_count_exist = r.hexists('blog:%s' % blog_id, 'collect')
        if collect_count_exist is False:
            r.hset('blog:%s' % blog_id, 'collect', 0)
        r.hincrby('blog:%s' % blog_id, 'collect', 1)
        result = {'code': 200, 'username': author}
        return JsonResponse(result)


# 取原博客
def get_first_blog(blog_list, blog_send_list):
    for item in blog_list:
        per_blog = {}
        per_blog['code'] = 201
        per_blog['bid'] = item.id
        per_blog['title'] = item.title
        per_blog['content'] = item.content
        per_blog['username'] = item.uid.username
        per_blog['profile_img'] = settings.PIC_URL+str(item.uid.profile_image_url)
        per_blog['create_time'] = item.create_time
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


# 取博客详细信息
def get_detail_blog(blog):
    # 获取用户名
    data = {}
    data['username'] = blog.userprofile.username
    # 获取题目
    data['title'] = blog['title']
    tags_object_list = Tag_blog.objects.filter(blog_id_fk=blog)
    total_tags_list = []
    # 取tag
    for tag_obj in tags_object_list:
        per_tag_name = tag_obj.tag_id_fk.tag_name
        total_tags_list.append(per_tag_name)
    data['tags'] = total_tags_list
    # 取内容
    data['content'] = blog['content']
    # 取时间
    data['crete_time'] = blog['create_time']
    # 取点赞数
    like_count_exist = r.hexists('blog:%s' % blog.id, 'like')
    if not like_count_exist:
        like_count = 0
    else:
        like_count = r.hget('blog:%s' % blog.id, 'like')
    data['like_count'] = like_count
    # 取转发数
    forward_count = r.hexists('blog:%s' % blog.id, 'forward')
    if not forward_count:
        forward_count = 0
    else:
        forward_count = r.hget('blog:%s' % blog.id, 'forward')
    data['forward_count'] = forward_count
    # 取收藏数数
    collect_count_exist = r.hexists('blog:%s' % blog.id, 'collect')
    if not collect_count_exist:
        collect_count = 0
    else:
        collect_count = r.hget('blog:%s' % blog.id, 'collect')
    data['collect_count'] = collect_count
    # 取评论数
    comment_count_exist = r.hexists('blog:%s' % blog.id, 'comment')
    if not comment_count_exist:
        comment_count = 0
    else:
        comment_count = r.hget('blog:%s' % blog.id, 'comment')
    data['comment_count'] = comment_count
    # 取图片
    images = Image.objects.filter(b_id=blog)
    image_list = []
    for item in images:
        image_list.append(settings.PIC_URL + str(item.image))
    data['img'] = image_list
    # 取评论
    comment_details = {}
    per_comment_detail_dic = []
    comments = Comment.objects.filter(b_id=id, isActive=True)
    for item in comments:
        one_comment_info = {}
        c_id = item.id
        one_comment_info['comment_id'] = c_id
        uid = item.uid
        users = UserProfile.objects.filter(id=uid)
        if not users:
            return JsonResponse({'code': 30112, 'data': '查看该用户评论失败'})
        comment_username = users[0].username
        one_comment_info['comment_username'] = comment_username
        comment_user_profile = users[0].profile_image_url
        one_comment_info['comment_user_profile'] = comment_user_profile
        comment_user_profile['comment_content'] = item.content
        # 获取每条评论对应的回复
        replies = Reply.objects.filter(c_id=c_id, isActive=True)
        replies_dic = []
        i = 1

        for item in replies:
            one_reply_info = {}
            one_reply_info_detail = {}
            users = UserProfile.objects.filter(id=item.uid)
            reply_username = users[0].username
            reply_profile = users[0].profile_image_url
            reply_content = item.content
            one_reply_info_detail['reply_username'] = reply_username
            one_reply_info_detail['reply_profile'] = reply_profile
            one_reply_info_detail['reply_content'] = reply_content
            one_reply_info['comment_reply_%s' % (i)] = one_reply_info_detail
            replies_dic.append(one_reply_info['comment_reply_%s' % (i)])
            i += 1
        one_comment_info['comment_replies'] = replies_dic
        per_comment_detail_dic.append(one_comment_info)
    comment_details['per_comment_detail'] = per_comment_detail_dic
    # 返回数据
    result = {'code': 200, 'data': data}
    return result


# 取转发博客
def get_forward_blog(forward_list, blog_send_list):
    for item in forward_list:
        forward_blog = {}
        forward_blog['code'] = 202
        forward_blog['fid'] = item.id
        forward_blog['fcontent'] = item.content
        forward_blog['fusername'] = item.uid.username
        forward_blog['profile_img'] = settings.PIC_URL+str(item.uid.profile_image_url)
        forward_blog['create_time'] = item.create_time
        blog_object = item.b_id
        forward_blog['id'] = blog_object.id
        forward_blog['title'] = blog_object.title
        forward_blog['content'] = blog_object.content
        forward_blog['username'] = blog_object.uid.username
        forward_blog['ocreate_time'] = blog_object.create_time
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


# 进行排序
def order_by_creatime(blog_send_list):
    for r in range(0, len(blog_send_list) - 1):
        for c in range(r, len(blog_send_list)):
            if blog_send_list[r]['create_time'] < blog_send_list[c]['create_time']:
                blog_send_list[r], blog_send_list[c] = blog_send_list[c], blog_send_list[r]


# 取收藏博客
def get_collect_blog(collect_list, blog_send_list):
    for item in collect_list:
        collect_blog = {}
        blog_object = item.b_id
        collect_blog['id'] = blog_object.id
        collect_blog['title'] = blog_object.title
        collect_blog['content'] = blog_object.content
        collect_blog['username'] = blog_object.username
        collect_blog['create_time'] = blog_object.create_time
        tags_object_list = Tag_blog.objects.filter(blog_id_fk=blog_object)
        total_tags_list = []
        # 取tag
        for tag_obj in tags_object_list:
            per_tag_name = tag_obj.tag_id_fk.tag_name
            total_tags_list.append(per_tag_name)
        collect_blog['tags'] = total_tags_list
        # 取点赞数
        like_count_exist = r.hexists('blog:%s' % blog_object.id, 'like')
        if not like_count_exist:
            like_count = 0
        else:
            like_count = r.hget('blog:%s' % blog_object.id, 'like')
        collect_blog['like_count'] = like_count
        # 取转发数
        forward_count_exist = r.hexists('blog:%s' % blog_object.id, 'forward')
        if not forward_count_exist:
            forward_count = 0
        else:
            forward_count = r.hget('blog:%s' % blog_object.id, 'forward')
        collect_blog['forward_count'] = forward_count
        # 取收藏数数
        collect_count_exist = r.hexists('blog:%s' % blog_object.id, 'collect')
        if not collect_count_exist:
            collect_count = 0
        else:
            collect_count = r.hget('blog:%s' % blog_object.id, 'collect')
        collect_blog['collect_count'] = collect_count
        # 取评论数
        comment_count_exist = r.hexists('blog:%s' % blog_object.id, 'comment')
        if not comment_count_exist:
            comment_count = 0
        else:
            comment_count = r.hget('blog:%s' % blog_object.id, 'comment')
        collect_blog['comment_count'] = comment_count
        # 取图片
        images = Image.objects.filter(b_id=blog_object)
        image_list = []
        for item in images:
            image_list.append(settings.PIC_URL + str(item.image))
        collect_blog['img'] = image_list
        blog_send_list.append(collect_blog)