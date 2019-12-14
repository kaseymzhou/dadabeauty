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
        tag_object = Tag.objects.get(tar_name = tag)
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

def

