from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.generic import View
from .models import *
import redis
import json
from django.core.paginator import Paginator
from tools.logging_check import logging_check
from user.models import *
# Create your views here.

r = redis.Redis(host='127.0.0.1',port=6379,db=2)

def test(request):
    return HttpResponse('test is ok')

# 首页显示产品（按点赞量显示图片+sku名）
class IndexShow(View):
    def get(self,request):
        """
        首页最hit产品展示
        :param result:
        :return:
        """
        # 127.0.0.1:8000/v1/product/index

        # 0. 获取所有产品详细内容
        catalog_list = Sku.objects.all()
        # 1. 建立列表储存点赞前30的sku信息
        redis_index = r.get('index_cache')
        if redis_index is None:
            print("未使用缓存")
            # 从redis中获取点赞前30的商品信息
            like_list = r.zrevrange('product:like',0,-1,withscores=True)
            like_top30_products = like_list[:30]
            new_like_top30_products = []
            product_info = []
            for item in like_top30_products:
                item = list(item)
                item[0] = item[0].decode()
                # new_like_top30_products[[sku(id),点赞数],[sku(id),点赞数],...]
                new_like_top30_products.append(item)
            for item in new_like_top30_products:
                sku_infos = Sku.objects.filter(id=item[0])
                sku_info = sku_infos[0]
                product_dic = {}
                product_dic['id'] = sku_info.id
                product_dic['name'] = sku_info.name
                product_dic['url'] = sku_info.default_img_url
                product_dic['like'] = item[1]
            product_info.append(product_dic)
            r.set("index_cache",product_info,ex=600)
        else:
            print("使用缓存")
            index_data = json.loads(redis_index)
        result = {"code": 200, "data": index_data, "base_url": settings.PIC_URL}

        return JsonResponse(result)

# 点进子类连接，显示子类产品（按updated_time从新到旧排）
class ProductsListView(View):
    def get(self,request,subclass_id):
        """
        :param request:
        :param subclass_id:子类id
        :param page_num:第几页
        :param page_size:每页显示多少项
        :return:
        """
        #  127.0.0.1:8000/v1/product/catalogs/1/1/?page=1
        # 0. 获取url传递参数值
        page_num = request.GET.get('page',1)
        # 1. 获取分类下的spu列表
        spu_list_ids = Spu.objects.filter(sb_id=subclass_id).values("id")
        sku_list = Sku.objects.filter(spu_id__in=spu_list_ids).order_by("-updated_time")
        # 2.分页
        # 创建分页对象，指定列表、页大小
        page_num = int(page_num)
        page_size = 10
        try:
            paginator = Paginator.page(sku_list,page_size)
            # 获取指定页码的数据
            page_skus = paginator.page(page_num)
            page_skus_json = []
            for sku in page_skus:
                sku_dict = {}
                sku_dict['skuid'] = sku.id
                sku_dict['name'] = sku.name
                sku_dict['image'] = str(sku.default_image_url)
                page_skus_json.append(sku_dict)
        except:
            result = {'code': 40200, 'error': '页数有误，小于0或者大于总页数'}
            return JsonResponse(result)
        result = {'code': 200, 'data': page_skus_json, 'paginator': {'pagesize': page_size, 'total': len(sku_list)},
                  'base_url': settings.PIC_URL}
        return JsonResponse(result)

# 产品详情页
class ProductsDetailView(View):
    def get(self, request, sku_id):
        """
        获取sku详情页信息，获取图片暂未完成
        :param request:
        :param sku_id: sku的id
        :return:
        """
        # 127.0.0.1:8000/v1/goods/detail/401/
        # 1. 获取sku实例
        sku_details = {}

        # 从redis中获取所有缓存
        redis_detail = r.get('index_detail_%s'%sku_id)

        # 无缓存
        if redis_detail is None:
            print("未使用缓存")
            """
            返回给前端的商品信息数据结构
            sku_details = {'name':name, 'spu':spu, 'img'=img,
                             {'diff':[source:price,source:price,source:price]},
                             {Sale_attr_name:[val_id:val,val_id:val,val_id:val]}
                             'comment_details':comment_details}
                             
            """
            try:
                sku_item = Sku.objects.get(id=sku_id)
                sku_source_item = Sku_source.objects.filter(sku_id=sku_id)
            except:
                # 判断是否有当前sku
                result = {'code': 30300, 'error': "相关产品不存在", }
                return JsonResponse(result)

            sku_catalog = sku_item.spu_id.name
            sku_details['image'] = str(sku_item.default_image_url)
            sku_details["spu"] = sku_item.spu_id.id
            sku_details["name"] = sku_item.name

            source_list = []
            for i in sku_source_item:
                sku_source_dic = {}
                sku_source_dic[i.source_id.name]= i.price
                source_list.append(sku_source_dic)
                sku_details['diff'] = source_list

            # 详情图片
            sku_images = Sku_img.objects.filter(sku_id=sku_id)
            if sku_images:
                sku_details['detail_image'] = str(sku_images[0].img_url)
            else:
                sku_details['detail_image'] = ""

            # 获取sku销售属性名称和sku销售属性值
            sale_attrs_val_lists = Sale_attr_val.objects.filter(sku=sku_id)

            sale_attr_id = sale_attrs_val_lists[0].sale_attr_id
            Sale_attr_lists = Sale_attr.objects.filter(id=sale_attr_id)
            Sale_attr_name = Sale_attr_lists[0].attr_name

            val_id_val_list = []
            for i in sale_attrs_val_lists:
                val_dic = {}
                val_dic[i.id] = i.val
                val_id_val_list.append(val_dic)
                sku_details[Sale_attr_name] = val_id_val_list

            """
            返回给前端时的评论区数据结构
            comments_info = {
                            'total_comments_count':total_comment_count,
                            per_comment_detail:[
                                                一条评论一个字典，所有评论字典组成一个大列表构成comments_info字典里per_comment_detail这个key的value
                                                划分依据：列表好遍历，字典好取值（key是固定的）

                                                {'comment_id' : comment_id,
                                                'comment_username' : comment_username,
                                                'comment_user_profile' : comment_user_profile,
                                                'comment_content' : comment_content,
                                                'comment_replies' : [
                                                                    {'comment_reply_1' : {
                                                                                        'reply_username' : reply_username,
                                                                                        'reply_profile' : reply_profile,
                                                                                        'reply_content' : reply_content
                                                                                         },
                                                                    {'comment_reply_2' : {
                                                                                        'reply_username' : reply_username,
                                                                                        'reply_profile' : reply_profile,
                                                                                        'reply_content' : reply_content
                                                                                         },
                                                                    {'comment_reply_3' : {
                                                                                        'reply_username' : reply_username,
                                                                                        'reply_profile' : reply_profile,
                                                                                        'reply_content' : reply_content
                                                                                         }

                                                                    ]

                                                },
                                                ...
                                                ]
                            }
            """

            comment_details = {}
            total_comments_count = r.hget('product:comment',sku_id)
            comment_details['total_comments_count'] = total_comments_count
            per_comment_detail_dic = []


            comments = Comment.objects.filter(sku_id=sku_id,isActive=True)
            for item in comments:
                one_comment_info = {}
                c_id = item.id
                one_comment_info['comment_id'] = c_id
                uid = item.uid
                users = UserProfile.objects.filter(id=uid)
                if not users:
                    return JsonResponse({'code':30112,'data':'查看该用户评论失败'})
                comment_username = users[0].username
                one_comment_info['comment_username']=comment_username
                comment_user_profile = users[0].profile_image_url
                one_comment_info['comment_user_profile'] = comment_user_profile
                comment_user_profile['comment_content'] = item.content
                # 获取每条评论对应的回复
                replies = Reply.objects.filter(c_id=c_id,isActive=True)
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
                    one_reply_info['comment_reply_%s'%(i)] = one_reply_info_detail
                    replies_dic.append(one_reply_info['comment_reply_%s'%(i)])
                    i += 1
                one_comment_info['comment_replies'] = replies_dic
                per_comment_detail_dic.append(one_comment_info)
            comment_details['per_comment_detail'] = per_comment_detail_dic
            sku_details['comment_details'] = comment_details


        # 写入缓存
            r.setex('index_detail_%s'%sku_id,60*60*24,json.dumps(sku_details))

        # 商品详细页评论、回复展示
        else:
            print("使用缓存")
            sku_details = json.loads(redis_detail)

            result = {'code': 200, 'data': sku_details,  'base_url': settings.PIC_URL}
            return JsonResponse(result)


# 评论
class Comment_product(View):
    @logging_check
    def post(self,request):
        data = request.body
        if not data:
            result = {'code': '30101', 'error': '请填写评论'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        sku_id = json_obj.get('sku_id')
        content = json_obj.get('content')
        uid = json_obj.get('uid')
        Comment.objects.create(content=content,uid=uid,sku_id=sku_id)

        # 判断是否在redis中曾经有设立过计数key
        sku_comment_count = r.hexists('product:comment',sku_id)
        if sku_comment_count is False:
            r.hset('product:comment',sku_id,0)
        # redis做评论计数
        r.hincrby('peoducts:comment',sku_id,1)
        result = {'code':200,'data':'评论成功'}
        return JsonResponse(result)

    @logging_check
    def delete(self,request):
        data = request.body
        if not data:
            result = {'code': '30102', 'error': '删除失败'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        comment_id = json_obj.get('comment_id')
        comments = Comment.objects.filter(id=comment_id)
        if not comments:
            return JsonResponse({'code': 30103, 'error': '无法删除该评论'})
        comment = comments[0]
        # 修改评论isActive属性为False
        comment.isActive=False
        comment.save()
        # redis做评论计数
        sku_id = comment.sku_id
        r.hincrby('peoducts:comment', sku_id, -1)
        result = {'code': 200, 'data': '删除评论成功'}
        return JsonResponse(result)

# 评论的回复
class Reply(View):
    @logging_check
    def post(self,request):
        data = request.body
        if not data:
            result = {'code': '30104', 'error': '请填写回复信息'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        content = json_obj.get('content')
        uid = json_obj.get('uid')
        c_id = json_obj.get('c_id')
        Reply.objects.create(content=content, uid=uid,c_id=c_id)
        # redis做评论计数
        comments = Comment.objects.filter(id=c_id)
        comment = comments[0]
        sku_id = comment.sku_id
        r.hincrby('peoducts:comment', sku_id, 1)
        # mysql数据库录入
        result = {'code':200,'data':'回复成功'}
        return JsonResponse(result)
    @logging_check
    def delete(self, request):
        data = request.body
        if not data:
            result = {'code': '30105', 'error': '删除失败'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        reply_id = json_obj.get('reply_id')
        replies = Reply.objects.filter(id=reply_id)
        if not replies:
            return JsonResponse({'code': 30106, 'error': '无法删除该回复'})
        reply = replies[0]
        reply.isActive = False
        reply.save()
        # redis做评论计数
        c_id = reply.c_id
        comments = Comment.objects.filter(id=c_id)
        comment = comments[0]
        sku_id = comment.sku_id
        r.hincrby('peoducts:comment', sku_id, -1)
        result = {'code': 200, 'data': '删除回复成功'}
        return JsonResponse(result)


# 点赞
class LikeProduct(View):
    @logging_check
    def post(self,request):
        data = request.body
        if not data:
            result = {'code': '30106', 'error': '点赞失败，请重试'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        uid = json_obj.get('uid')
        sku_id = json_obj.get('sku_id')
        LikeProduct.objects.create(uid=uid,sku_id=sku_id)

        # 判断是否在redis中曾经有设立过计数key
        sku_like_count = r.hexists('product:like', sku_id)
        if sku_like_count is False:
            r.hset('product:like', sku_id, 0)
        # redis做评论计数
        r.hincrby('peoducts:like', sku_id, 1)
        # mysql数据库录入
        result = {'code':200,'data':'点赞成功'}
        return JsonResponse(result)
    @logging_check
    def delete(self, request):
        data = request.body
        if not data:
            result = {'code': '30107', 'error': '点赞失败'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        like_id = json_obj.get('like_id')
        likes = LikeProduct.objects.filter(id=like_id)
        if not likes:
            return JsonResponse({'code': 30108, 'error': '无法取消点赞'})
        like = likes[0]
        like.isActive = False
        like.save()
        # redis做评论计数
        sku_id = like.sku_id
        r.hincrby('product:like', sku_id, -1)
        result = {'code': 200, 'data': '取消点赞成功'}
        return JsonResponse(result)

# 收藏商品
class CollectProducts(View):
    @logging_check
    def post(self,request):
        data = request.body
        if not data:
            result = {'code': '30109', 'error': '收藏失败，请重试'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        uid = json_obj.get('uid')
        sku_id = json_obj.get('sku_id')
        Collect.objects.create(uid=uid,sku_id=sku_id)

        # 判断是否在redis中曾经有设立过计数key
        sku_collect_count = r.hexists('product:collect', sku_id)
        if sku_collect_count is False:
            r.hset('product:collect', sku_id, 0)
        # redis做评论计数
        r.hincrby('product:collect', sku_id, 1)
        # mysql数据库录入
        result = {'code':200,'data':'收藏成功'}
        return JsonResponse(result)
    @logging_check
    def delete(self, request):
        data = request.body
        if not data:
            result = {'code': '30110', 'error': '取消收藏失败'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        collect_id = json_obj.get('collect_id')
        collects = Collect.objects.filter(id=collect_id)
        if not collects:
            return JsonResponse({'code': 30111, 'error': '无法取消收藏'})
        collect = collects[0]
        collect.isActive = False
        collect.save()
        # redis做评论计数
        sku_id = collect.sku_id
        r.hincrby('product:collect', sku_id, -1)
        result = {'code': 200, 'data': '取消点赞成功'}
        return JsonResponse(result)
