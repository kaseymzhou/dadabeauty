from django.http import JsonResponse

# Create your views here.
from community.models import Blog, Tag
from tools.logging_check import logging_check
import json

from user.models import UserProfile


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
        tag = request.GET.get('tag')
        if not tag:
            blog_list = Blog.objects.order_by('create_time')
            for item in blog_list:
                if item['is_active'] == True:
                    username = item.userprofile.username
                    title = item['title']
                    tag_name = item.tag.tag_name
                    content = item['content']
                    like_count = item['like_count']
                    forward_count = item['forward_count']
                    collect_count = item['collect_count']
                    comment_count = item['comment_count']
                    data = {'user_me': user_me,
                            'username': username,
                            'title': title,
                            'tag_name': tag_name,
                            'content': content,
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
                        username = item.userprofile.username
                        title = item['title']
                        tag_name = item.tag.tag_name
                        content = item['content']
                        like_count = item['like_count']
                        forward_count = item['forward_count']
                        collect_count = item['collect_count']
                        comment_count = item['comment_count']
                        data = {'user_me': user_me,
                                'username': username,
                                'title': title,
                                'tag_name': tag_name,
                                'content': content,
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
                title = item['title']
                tag_name = item.tag.tag_name
                content = item['content']
                like_count = item['like_count']
                forward_count = item['forward_count']
                collect_count = item['collect_count']
                comment_count = item['comment_count']
                data = {'user_me': user_me,
                        'username': username,
                        'title': title,
                        'tag_name': tag_name,
                        'content': content,
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
def detail_blog(request):
    id = request.GET.get('blogid')
    userme = request.myuser
    if request.method == 'POST':
        result = {'code': 30107, 'error': '请使用GET请求!'}
        return JsonResponse(result)
    if request.method == 'DELETE':
        # http://127.0.0.1:8000/v1/community/index?blogid=xxx
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
        # http://127.0.0.1:8000/v1/community/index?blogid=xxx
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
        like_count = blog['like_count']
        forward_count = blog['forward_count']
        collect_count = blog['collect_count']
        comment_count = blog['comment_count']
        data = {'user_me': userme,
                'username': username,
                'title': title,
                'tag_name': tag_name,
                'content': content,
                'like_count': like_count,
                'forward_count': forward_count,
                'collect_count': collect_count,
                'comment_count': comment_count
                }
        result = {'code': 200, 'data': data}
        return JsonResponse(result)
