from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def test(request):
    return HttpResponse('test is ok')

# 首页显示产品（按点赞量显示图片+sku名）
# 点进子类连接，显示子类产品（按上线新旧）
# 产品详情页（）
# 评论
#
#
#