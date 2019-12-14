from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
from community.models import Blog, Tag
from tools.logging_check import logging_check
import json

from user.models import UserProfile


@logging_check
def send_topics(request, author_name):
    if request.method == 'POST':
        # 发表博客
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
        # 获取 用户文章数据
        # /v1/topics/guoxiaonao - guoxiaonao的所有文章
        # /v1/topics/guoxiaonao?category=tec|no-tec 查看具体种类
        # /v1/topics/guoxiaonao?t_id=33 查看具体文章
        # 1, 访问当前博客的访问者  visitor
        # 2, 当前被访问的博客的博主 author
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
    # http://127.0.0.1:8000/v1/community/index?tag  访问tag标签博客
    if request.method == 'GET':
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
                    data = {'username ': username,
                            'title ': title,
                            'tag_name ': tag_name,
                            'content ': content,
                            'like_count ': like_count,
                            'forward_count ': forward_count,
                            'collect_count ': collect_count,
                            'comment_count ': comment_count
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
                        data = {'username ': username,
                                'title ': title,
                                'tag_name ': tag_name,
                                'content ': content,
                                'like_count ': like_count,
                                'forward_count ': forward_count,
                                'collect_count ': collect_count,
                                'comment_count ': comment_count
                                }
                        result = {'code': 200, 'data': data}
                        return JsonResponse(result)
        if request.method == 'post':
            result = {'code': 30107, 'error': '请使用GET请求!'}
        return JsonResponse(result)

def my_index(request):
    pass