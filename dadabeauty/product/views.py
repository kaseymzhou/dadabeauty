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
from tools.datetimeseri import JsonCustomEncoder
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
        # 1. 建立列表储存点赞前10的sku信息
        redis_index = r.get('index_cache')
        if redis_index is None:
            print("未使用缓存")
            # 从redis中获取点赞前10的商品信息
            like_list = r.zrevrange('product:like',0,-1,withscores=True) #[(b'product:1', 5.0), (b'product:2', 2.0), (b'product:3', 1.0)]
            like_top10_products = like_list[:12]
            new_like_top10_products = []
            product_info = []
            for item in like_top10_products:
                item = list(item)
                item[0] = item[0].decode()
                # new_like_top30_products[['product:sku_id',点赞数],['product:sku_id',点赞数],...]
                new_like_top10_products.append(item)
            for item in new_like_top10_products:
                sku_id = item[0].split(':')[-1]
                sku_infos = Sku.objects.filter(id=sku_id)
                sku_info = sku_infos[0]
                product_dic = {}
                product_dic['id'] = sku_id
                product_dic['name'] = sku_info.name
                product_dic['url'] = str(sku_info.default_img_url)
                product_dic['source']=sku_info.source_id.name
                product_dic['like'] = str(int(item[1]))
                product_info.append(product_dic)
            r.setex("index_cache",60*5,json.dumps(product_info))
            redis_index = r.get('index_cache')
            index_data = json.loads(redis_index)
        else:
            print("使用缓存")
            index_data = json.loads(redis_index)
        result = {"code": 200, "data": index_data}

        return JsonResponse(result)

# 点进子类连接，显示子类产品（按updated_time从新到旧排）
class ProductsListView(View):
    # def get(self,request,subclass_id):
    #     """
    #     :param request:
    #     :param subclass_id:子类id
    #     :param page_num:第几页
    #     :param page_size:每页显示多少项
    #     :return:
    #     """
    #     #  127.0.0.1:8000/v1/product/catalogs/1/1/?page=1
    #     # 0. 获取url传递参数值
    #     page_num = request.GET.get('page',1)
    #     # 1. 获取分类下的spu列表
    #     spu_list_ids = Spu.objects.filter(sb_id=subclass_id).values("id")
    #     sku_list = Sku.objects.filter(spu_id__in=spu_list_ids).order_by("-updated_time")
    #     # 2.分页
    #     # 创建分页对象，指定列表、页大小
    #     page_num = int(page_num)
    #     page_size = 18
    #     try:
    #         paginator = Paginator.page(sku_list,page_size)
    #         # 获取指定页码的数据
    #         page_skus = paginator.page(page_num)
    #         page_skus_json = []
    #         for sku in page_skus:
    #             sku_dict = {}
    #             sku_dict['skuid'] = sku.id
    #             sku_dict['name'] = sku.name
    #             sku_dict['image'] = str(sku.default_image_url)
    #             sku_dict['source']=sku.source_id.name
    #             page_skus_json.append(sku_dict)
    #     except:
    #         result = {'code': 40200, 'error': '页数有误，小于0或者大于总页数'}
    #         return JsonResponse(result)
    #     result = {'code': 200,
    #               'data': page_skus_json,
    #               'paginator': {'pagesize': page_size, 'total': len(sku_list)},
    #               'base_url': settings.PIC_URL}
    #     return JsonResponse(result)
    def get(self,request,subclass_id):
        """
        :param request:
        :param subclass_id:子类id
        :return:
        """
        # 1. 获取分类下的spu列表
        spu_list_ids = Spu.objects.filter(sb_id=subclass_id).values("id")
        sku_list = Sku.objects.filter(spu_id__in=spu_list_ids).order_by("-updated_time")
        if not sku_list:
            return JsonResponse({'code':'30111','error':"未能查询到该商品"})
        sku_show_list = []
        for sku in sku_list:
            sku_dict = {}
            sku_dict['skuid'] = sku.id
            sku_dict['name'] = sku.name
            sku_dict['image'] = str(sku.default_img_url)
            sku_dict['source']=sku.source_id.name
            sku_show_list.append(sku_dict)
        result = {'code': 200,
                  'data': sku_show_list}
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
            sku_details = {'name':name, 
                           'img':img,
                           'price':price,
                           'source':source,
                           'discount_price':price,
                           'like_count':like_count,
                           'url':url,
                           'feature':feature
                           'sale_attr':[{'name':name,'val':val},{'name':name,'val':val}],
                           'comment_details':comment_details
                            }
                             
            """
            try:
                sku_item = Sku.objects.get(id=sku_id)
            except:
                # 判断是否有当前sku
                result = {'code': 30300, 'error': "相关产品不存在", }
                return JsonResponse(result)

            sku_details['image'] = str(sku_item.default_img_url)
            sku_details["price"] = str(sku_item.price)
            sku_details["name"] = sku_item.name
            sku_details["discount_price"] = str(sku_item.discount_price)
            sku_details["source"] = sku_item.source_id.name
            sku_details['sale_attr'] = []
            sku_details['url'] = str(sku_item.source_url)
            sku_details['feature'] = sku_item.feature
            redis_like_count = r.zscore('product:like','product:%s'%sku_id)
            if not redis_like_count:
                sku_details['like_count'] = 0
            else:
                sku_details['like_count'] = redis_like_count


            sale_attr_and_value=[]
            spu_id = sku_item.spu_id
            sale_attr_list = Sale_attr.objects.filter(spu_id=spu_id)
            for sale_attr in sale_attr_list:
                per_sale_attr_value_dic={}
                sale_attr_name = sale_attr.attr_name
                sale_attr_value = Sale_attr_val.objects.filter(sku_id=sku_id,sale_attr_id=sale_attr.id)
                sale_attr_val=sale_attr_value[0].val
                per_sale_attr_value_dic['name']=sale_attr_name
                per_sale_attr_value_dic['value']=sale_attr_val
                sale_attr_and_value.append(per_sale_attr_value_dic)
            sku_details['sale_attr']=sale_attr_and_value


            """
            返回给前端时的评论区数据结构
            comments_info = {
                            'total_comments_count':total_comment_count,
                            per_comment_detail:[
                                                一条评论一个字典，所有评论字典组成一个大列表构成comments_info字典里per_comment_detail这个key的value
                                                划分依据：列表好遍历，字典好取值（key是固定的）

                                                {'comment_id' : comment_id,
                                                'comment_uid':comment_uid
                                                'comment_username' : comment_username,
                                                'comment_user_profile' : comment_user_profile,
                                                'comment_content' : comment_content,
                                                'comment_created_time':comment_created_time,
                                                'comment_replies' : [
                                                                    {
                                                                        'reply_username' : reply_username,
                                                                        'reply_uid':reply_uid,
                                                                        'reply_content' : reply_content,
                                                                        'reply_created_time':reply_created_time
                                                                         ,
                                                                    {
                                                                        'reply_username' : reply_username,
                                                                        'reply_uid':reply_uid,
                                                                        'reply_content' : reply_content,
                                                                        'reply_created_time':reply_created_time
                                                                         ,
                                                                    {
                                                                        'reply_username' : reply_username,
                                                                        'reply_uid':reply_uid,
                                                                        'reply_content' : reply_content,
                                                                        'reply_created_time':reply_created_time
                                                                    }
                                                                    ,
                                                                    ...  
                                                                    ]

                                                },
                                                ...
                                                ]
                            }
            """

            comment_details = {}
            redis_comment_total_count = r.hget('product:%s'%sku_id,'comment')
            if not redis_comment_total_count:
                comment_details['total_comments_count'] = 0
            else:
                comment_details['total_comments_count'] = redis_comment_total_count.decode()
            per_comment_detail_dic = []


            comments = Comment.objects.filter(sku_id=sku_id,isActive=True)
            for item in comments:
                one_comment_info = {}
                c_id = item.id
                one_comment_info['comment_id'] = c_id
                uid = item.uid.id
                users = UserProfile.objects.filter(id=uid)
                if not users:
                    return JsonResponse({'code':30112,'data':'查看该用户评论失败'})
                comment_username = users[0].username
                one_comment_info['comment_username']=comment_username
                comment_user_profile = users[0].profile_image_url
                one_comment_info['comment_user_profile'] = settings.PIC_URL+str(comment_user_profile)
                one_comment_info['comment_content'] = item.content
                one_comment_info['comment_created_time']=item.created_time
                one_comment_info['comment_uid']=users[0].id
                # 获取每条评论对应的回复
                replies = ReplyProduct.objects.filter(c_id=c_id,isActive=True)
                replies_dic = []

                for item in replies:
                    one_reply_info_detail = {}
                    users = UserProfile.objects.filter(id=item.uid.id)
                    reply_username = users[0].username
                    reply_uid = users[0].id
                    reply_content = item.content
                    one_reply_info_detail['reply_username'] = reply_username
                    one_reply_info_detail['reply_uid'] = reply_uid
                    one_reply_info_detail['reply_content'] = reply_content
                    one_reply_info_detail['reply_created_time'] = item.created_time
                    replies_dic.append(one_reply_info_detail)
                one_comment_info['comment_replies'] = replies_dic
                per_comment_detail_dic.append(one_comment_info)
            comment_details['per_comment_detail'] = per_comment_detail_dic
            sku_details['comment_details'] = comment_details


        # 写入缓存
            r.setex('index_detail_%s'%sku_id,3,json.dumps(sku_details,cls=JsonCustomEncoder))
            redis_detail = r.get('index_detail_%s' % sku_id)
            sku_details = json.loads(redis_detail)


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
        commentuser = UserProfile.objects.filter(id=uid)
        commentproduct = Sku.objects.filter(id=sku_id)
        Comment.objects.create(content=content,uid=commentuser[0],sku_id=commentproduct[0])

        # 判断是否在redis中曾经有设立过计数key
        sku_comment_count = r.hexists('product:%s'%sku_id,'comment')
        if sku_comment_count is False:
            r.hset('product:%s'%sku_id,'comment',0)
        # redis做评论计数
        r.hincrby('product:%s'%sku_id,'comment',1)
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
        r.hincrby('product:%s'%sku_id,'comment',-1)
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
        replyuser = UserProfile.objects.filter(id=uid)
        replycomment = Comment.objects.filter(id=c_id)
        ReplyProduct.objects.create(content=content, uid=replyuser[0],c_id=replycomment[0])
        # redis做评论计数
        comments = Comment.objects.filter(id=c_id)
        comment = comments[0]
        sku_id = comment.sku_id
        r.hincrby('product:%s'%sku_id, 'comment', 1)
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
        replies = ReplyProduct.objects.filter(id=reply_id)
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
        r.hincrby('product:%s'%sku_id, 'comment', -1)
        result = {'code': 200, 'data': '删除回复成功'}
        return JsonResponse(result)


# 点赞
class LikeP(View):
    @logging_check
    def post(self,request):
        data = request.body
        if not data:
            result = {'code': '30106', 'error': '点赞失败，请重试'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        uid = json_obj.get('uid')
        sku_id = json_obj.get('sku_id')
        print(uid,sku_id)

        # 在mysql中根据uid和sku_id查看是否有记录，若没有记录，证明客户动作为点赞，在redis和mysql中记录点赞动作
        likeuser = UserProfile.objects.filter(id=uid)
        likesku = Sku.objects.filter(id=sku_id)
        like_record = LikeProduct.objects.filter(uid=likeuser[0],sku_id=likesku[0])
        if like_record.count() == 0:
            # 判断是否在redis中曾经有设立过计数key[有序集合]
            sku_like_count = r.zscore('product:like','product:%s'%sku_id)
            # 还未设立
            if sku_like_count is False:
                #设立key
                r.zadd('product:like',{'product:%s'%sku_id:0})
            # redis做评论计数加1
            r.zincrby('product:like',1,'product:%s'%sku_id)
                # mysql数据库录入
            LikeProduct.objects.create(uid=likeuser[0], sku_id=likesku[0])
            result = {'code':200,'data':'点赞成功'}
            return JsonResponse(result)
        # 有mysql记录，看记录来判断用户进行的是点赞还是取消点赞动作，并进行相反的数据库记录
        else:
            like_record=like_record[0]
            isactive = like_record.isActive
            # 用户曾经点赞 --> 现在：取消点赞
            if isactive == True:
                like_record.isActive = False
                like_record.save()
                # redis计数减1
                r.zincrby('product:like',-1,'product:%s'%sku_id)
                return JsonResponse({'code':201,'data':'取消点赞成功'})
            # 用户曾经取消点赞 --> 现在：重新点赞
            else:
                like_record.isActive = True
                like_record.save()
                # redis计数加1
                r.zincrby('product:like',1,'product:%s'%sku_id)
                return JsonResponse({'code':200,'data':'点赞成功'})

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
        collectuser = UserProfile.objects.filter(id=uid)
        collectsku= Sku.objects.filter(id=sku_id)
        collectrecord = Collect.objects.filter(uid=collectuser[0],sku_id=collectsku[0])
        print(collectrecord)
        if collectrecord.count() == 0:
            Collect.objects.create(uid=collectuser[0],sku_id=collectsku[0])
            # 判断是否在redis中曾经有设立过计数key
            sku_collect_count = r.hexists('product:%s'%sku_id,'collect')
            if sku_collect_count is False:
                r.hset('product:%s'%sku_id,'collect', 0)
            # redis做评论计数
            r.hincrby('product:%s'%sku_id,'collect', 1)
            result = {'code':200,'data':'收藏成功'}
            return JsonResponse(result)
        else:
            collectrecord = collectrecord[0]
            iscollect = collectrecord.isActive
            if iscollect == True:
                collectrecord.isActive = False
                collectrecord.save()
                r.hincrby('product:%s' % sku_id, 'collect', -1)
                result = {'code': 201, 'data': '取消收藏成功'}
                return JsonResponse(result)
            else:
                collectrecord.isActive = True
                collectrecord.save()
                r.hincrby('product:%s' % sku_id, 'collect', 1)
                result = {'code': 200, 'data': '收藏成功'}
                return JsonResponse(result)
