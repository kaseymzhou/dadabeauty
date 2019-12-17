import redis
from django.http import JsonResponse

# Create your views here.
from community.models import Blog, Tag, Forward, Comment, Reply
from tools.logging_check import logging_check
import json

from user.models import UserProfile

r = redis.Redis(host='127.0.0.1', port=6379, db=0)


@logging_check
def send_topics(request):
    if request.method == 'POST':
        # 发表博客
        # http://127.0.0.1:8000/v1/community/send_topics?authorname=xxx
        author_name = request.GET.get(', authorname')
        author = request.myuser
        if author.username != author_name:
            result = {'code': 30101, 'error': '非本人操作!'}
            return JsonResponse(result)
        json_str = request.body
        json_obj = json.loads(json_str)
        title = json_obj.get('title')
        if not title:
            result = {'code': 30103, 'error': 'title不得为空!'}
            return JsonResponse(result)
        tag = json_obj.get('tag')
        if not tag:
            result = {'code': 30102, 'error': 'tag不得为空!'}
            return JsonResponse(result)
        tag_object = Tag.objects.get(tar_name=tag)
        # 文章内容
        content = json_obj.get('content')
        if not content:
            result = {'code': 30104, 'error': 'content不得为空!'}
            return JsonResponse(result)
        # 创建blog
        Blog.objects.create(title=title, content=content, uid=author, tid=tag_object)
        result = {'code': 200, 'username': author.username}
        return JsonResponse(result)

    if request.method == 'GET':
        # 获得当前发送博客的界面
        # http://127.0.0.1:8000/v1/community/send_topics?authorname=xxx
        author_name = request.GET.get(', authorname')
        authors = UserProfile.objects.filter(username=author_name)
        if not authors:
            result = {'code': 30105, 'error': 'The author is not existed !'}
            return JsonResponse(result)
        # 当前被访问的博客博主
        author = authors[0]
        res = {'code': 200, 'username': author.username}
        return JsonResponse(res)


@logging_check
def index(request):
    # http://127.0.0.1:8000/v1/community/index  访问所有博客
    # http://127.0.0.1:8000/v1/community/index?tag=xxx  访问tag标签博客
    if request.method == 'GET':
        user_me = request.myuser
        tag = request.GET.get('tag_name')
        if not tag:
            blog_list = Blog.objects.order_by('create_time')
            for item in blog_list:
                if item['is_active'] == True:
                    id = item['id']
                    username = item.userprofile.username
                    title = item['title']
                    tag_name = item.tag.tag_name
                    content = item['content']
                    create_time = item['create_time']
                    like_count_exist = r.hexists('like:count', id)
                    if like_count_exist:
                        like_count = r.hget('like:count', id)
                    else:
                        like_count = 0
                    forward_count_exist = r.hexists('forward:count', id)
                    if forward_count_exist:
                        forward_count = r.hget('forward:count', id)
                    else:
                        forward_count = 0
                    collect_count_exist = r.hexists('collect:count', id)
                    if collect_count_exist:
                        collect_count = r.hget('collect:count', id)
                    else:
                        collect_count = 0
                    comment_count_exist = r.hexists('comment:count', id)
                    if comment_count_exist:
                        comment_count = r.hget('comment:count', id)
                    else:
                        comment_count = 0
                    data = {'id': id,
                            'user_me': user_me,
                            'username': username,
                            'title': title,
                            'tag_name': tag_name,
                            'content': content,
                            'crete_time': create_time,
                            'like_count': like_count,
                            'forward_count': forward_count,
                            'collect_count': collect_count,
                            'comment_count': comment_count
                            }
                    result = {'code': 200, 'data': data}
                    return JsonResponse(result)
        else:
            tag = Tag.objects.filter(tag_name=tag)
            if not tag:
                result = {'code': 30106, 'error': '这个标签不存在 !'}
                return JsonResponse(result)
            tag_name = tag[0]['tag_name']
            blog_list = Blog.objects.order_by('create_time')
            for item in blog_list:
                if item['tag_name'] == tag_name:
                    if item['is_active'] == True:
                        id = item['id']
                        username = item.userprofile.username
                        title = item['title']
                        tag_name = item.tag.tag_name
                        content = item['content']
                        create_time = item['create_time']
                        like_count_exist = r.hexists('like:count', id)
                        if like_count_exist:
                            like_count = r.hget('like:count', id)
                        else:
                            like_count = 0
                        forward_count_exist = r.hexists('forward:count', id)
                        if forward_count_exist:
                            forward_count = r.hget('forward:count', id)
                        else:
                            forward_count = 0
                        collect_count_exist = r.hexists('collect:count', id)
                        if collect_count_exist:
                            collect_count = r.hget('collect:count', id)
                        else:
                            collect_count = 0
                        comment_count_exist = r.hexists('comment:count', id)
                        if comment_count_exist:
                            comment_count = r.hget('comment:count', id)
                        else:
                            comment_count = 0
                        data = {'id': id,
                                'user_me': user_me,
                                'username': username,
                                'title': title,
                                'tag_name': tag_name,
                                'content': content,
                                'crete_time': create_time,
                                'like_count': like_count,
                                'forward_count': forward_count,
                                'collect_count': collect_count,
                                'comment_count': comment_count
                                }
                        result = {'code': 200, 'data': data}
                        return JsonResponse(result)
        if request.method == 'post':
            result = {'code': 30107, 'error': '请使用GET请求!'}
            return JsonResponse(result)


@logging_check
def my_index(request):
    # http://127.0.0.1:8000/v1/community/index?authorname=xxx  访问特定人的博客主页
    if request.method == 'GET':
        authorname = request.GET.get('authorname')
        author = UserProfile.objects.get(username=authorname)
        user_me = request.myuser
        blog_list = author.blog_set.order_by('create_time')
        for item in blog_list:
            if item['is_active'] == True:
                username = item.userprofile.username
                id = item['id']
                title = item['title']
                tag_name = item.tag.tag_name
                content = item['content']
                create_time = item['create_time']
                like_count_exist = r.hexists('like:count', id)
                if like_count_exist:
                    like_count = r.hget('like:count', id)
                else:
                    like_count = 0
                forward_count_exist = r.hexists('forward:count', id)
                if forward_count_exist:
                    forward_count = r.hget('forward:count', id)
                else:
                    forward_count = 0
                collect_count_exist = r.hexists('collect:count', id)
                if collect_count_exist:
                    collect_count = r.hget('collect:count', id)
                else:
                    collect_count = 0
                comment_count_exist = r.hexists('comment:count', id)
                if comment_count_exist:
                    comment_count = r.hget('comment:count', id)
                else:
                    comment_count = 0
                data = {'id': id,
                        'user_me': user_me,
                        'username': username,
                        'title': title,
                        'tag_name': tag_name,
                        'content': content,
                        'crete_time': create_time,
                        'like_count': like_count,
                        'forward_count': forward_count,
                        'collect_count': collect_count,
                        'comment_count': comment_count
                        }
                result = {'code': 200, 'data': data}
                return JsonResponse(result)
    if request.method == 'POST':
        result = {'code': 30107, 'error': '请使用GET请求!'}
        return JsonResponse(result)


@logging_check
def my_index_forward(request):
    # http://127.0.0.1:8000/v1/community/index_forward?authorname=xxx  访问特定人的博客主页
    if request.method == 'GET':
        authorname = request.GET.get('authorname')
        try:
            author = UserProfile.objects.get(username=authorname)
        except Exception as e:
            print(e)
            result = {'code': 30110, 'error': '该用户不存在!'}
            return JsonResponse(result)
        user_me = request.myuser
        forward_list = author.forward_set.order_by('create_time')
        for item in forward_list:
            if item['is_active'] == True:
                username = item.userprofile.username
                id = item['id']
                blog_title = item.blog.title
                tag_name = item.tag.tag_name
                content = item['content']
                blog_content = item.blog.content
                data = {'id': id,
                        'user_me': user_me,
                        'username': username,
                        'blog_title': blog_title,
                        'tag_name': tag_name,
                        'content': content,
                        'blog_content': blog_content,
                        }
                result = {'code': 200, 'data': data}
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
            blog.is_active = False
            blog.save()
        except Exception as e:
            print('获得博客错误\n', e)
            result = {'code': 30108, 'error': '请给我博客id!'}
            return JsonResponse(result)
        username = blog.userprofile.username
        title = blog['title']
        tag_name = blog.tag.tag_name
        content = blog['content']
        create_time = blog['create_time']
        like_count_exist = r.hexists('like:count', id)
        if like_count_exist:
            like_count = r.hget('like:count', id)
        else:
            like_count = 0
        forward_count_exist = r.hexists('forward:count', id)
        if forward_count_exist:
            forward_count = r.hget('forward:count', id)
        else:
            forward_count = 0
        collect_count_exist = r.hexists('collect:count', id)
        if collect_count_exist:
            collect_count = r.hget('collect:count', id)
        else:
            collect_count = 0
        comment_count_exist = r.hexists('comment:count', id)
        if comment_count_exist:
            comment_count = r.hget('comment:count', id)
        else:
            comment_count = 0
        data = {'user_me': userme,
                'username': username,
                'title': title,
                'tag_name': tag_name,
                'content': content,
                'crete_time': create_time,
                'like_count': like_count,
                'forward_count': forward_count,
                'collect_count': collect_count,
                'comment_count': comment_count
                }
        result = {'code': 200, 'data': data}
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
        forward_count_exist = r.hexists('forward:comment', blog_id)
        if forward_count_exist is False:
            r.hset('forward:comment', blog_id, 0)
        r.hincrby('forward:comment', blog_id, 1)
        result = {'code': 200, 'username': author}
        return JsonResponse(result)


@logging_check
def like_blog(request):
    if request.method == 'POST':
        result = {'code': 30107, 'error': '请使用GET请求!'}
        return JsonResponse(result)

    if request.method == 'GET':
        # http://127.0.0.1:8000/v1/community/like?authorname=xxx&blogid=xxx
        author_name = request.GET.get('authorname')
        author = request.myuser
        if author.username != author_name:
            result = {'code': 30101, 'error': '非本人操作!'}
            return JsonResponse(result)
        blog_id = request.GET.get('blogid')
        # 统计转发数
        like_count_exist = r.hexists('like:comment', blog_id)
        if like_count_exist is False:
            r.hset('like:comment', blog_id, 0)
        r.hincrby('like:comment', blog_id, 1)
        result = {'code': 200, 'username': author}
        return JsonResponse(result)


@logging_check
def unlike(request):
    if request.method == 'POST':
        result = {'code': 30107, 'error': '请使用GET请求!'}
        return JsonResponse(result)

    if request.method == 'GET':
        # http://127.0.0.1:8000/v1/community/unlike?authorname=xxx&blogid=xxx
        author_name = request.GET.get('authorname')
        author = request.myuser
        if author.username != author_name:
            result = {'code': 30101, 'error': '非本人操作!'}
            return JsonResponse(result)
        blog_id = request.GET.get('blogid')
        # 统计转发数
        like_count_exist = r.hexists('like:comment', blog_id)
        if like_count_exist is False:
            r.hset('like:comment', blog_id, 0)
        r.hincrby('like:comment', blog_id, -1)
        result = {'code': 200, 'username': author}
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
        blog_comment_count = r.hexists('comment:count', blog_id)
        if blog_comment_count is False:
            r.hset('comment:count', blog_id, 0)
        # redis做评论计数
        r.hincrby('comment:count', blog_id, 1)
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
        sku_id = comment.sku_id
        r.hincrby('comment:count', sku_id, -1)
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
        Reply.objects.create(content=content, uid=uid, c_id=c_id)
        # mysql数据库录入
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
        reply.isActive = False
        reply.save()
        result = {'code': 200, 'data': '删除回复成功'}
        return JsonResponse(result)
