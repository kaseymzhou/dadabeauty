from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
from .models import *
from django_redis import get_redis_connection
import redis
import json
from django.core.paginator import Paginator
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
            like_list = r.zrevrange('product_like',0,-1,withscores=True)
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
class ProductsLiistView(View):
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
        # 从redis中获取所有数据
        redis_conn = get_redis_connection('goods')
        redis_detail = redis_conn.get('goods_%s' % sku_id)
        if redis_detail is None:
            print("未使用缓存")
            try:
                sku_item = SKU.objects.get(id=sku_id)
            except:
                # 1.1 判断是否有当前sku
                result = {'code': 40300, 'error': "Such sku doesn' exist", }
                return JsonResponse(result)
            sku_catalog = sku_item.SPU_ID.catalog
            sku_details['image'] = str(sku_item.default_image_url)
            sku_details["spu"] = sku_item.SPU_ID.id
            sku_details["name"] = sku_item.name
            sku_details["caption"] = sku_item.caption
            sku_details["price"] = str(sku_item.price)
            sku_details["catalog_id"] = sku_catalog.id
            sku_details["catalog_name"] = sku_catalog.name

            # 详情图片
            sku_image = SKUImage.objects.filter(sku_id=sku_item.id)
            if sku_image:
                sku_details['detail_image'] = str(sku_image[0].image)
            else:
                sku_details['detail_image'] = ""

            # 2. 获取sku销售属性名称和sku销售属性值
            sku_sale_attrs_val_lists = SaleAttrValue.objects.filter(sku=sku_id)
            sku_sale_attr_val_names = []  # 保存sku销售属性值名称的list
            sku_sale_attr_val_id = []
            sku_sale_attr_names = []  # 保存sku销售属性名称的list
            sku_sale_attr_id = []
            sku_all_sale_attr_vals_name = {}
            sku_all_sale_attr_vals_id = {}

            # 传递sku销售属性id和名称  以及  sku销售属性值id和名称
            for sku_sale_attrs_val in sku_sale_attrs_val_lists:
                sku_sale_attr_val_names.append(sku_sale_attrs_val.sale_attr_value_name)
                sku_sale_attr_val_id.append(sku_sale_attrs_val.id)
                sku_sale_attr_names.append(sku_sale_attrs_val.sale_attr_id.sale_attr_name)
                sku_sale_attr_id.append(sku_sale_attrs_val.sale_attr_id.id)
                # 该销售属性下的所有属性值，供·页面选择使用
                # SPU销售属性：颜色，容量
                # 页面显示：
                # 颜色： 红色，蓝色
                # 容量：100ml，200ml
                # 返回数据包含：
                #   1. spu销售属性id，即颜色，容量两个属性的id
                #   2. spu销售属性名称
                #   3. 销售属性值id，即 红色id为1，蓝色id为2，100ml的id为3，200ml的id为4
                #   4. 销售属性值名称
                #   5. sku销售属性值id及名称
                attr = SPUSaleAttr.objects.get(id=sku_sale_attrs_val.sale_attr_id.id)
                sku_all_sale_attr_vals_id[attr.id] = []
                sku_all_sale_attr_vals_name[attr.id] = []
                vals = SaleAttrValue.objects.filter(sale_attr_id=attr.id)
                for val in vals:
                    print("attr.id:", attr.id)
                    print("val.id:", val.id, val.sale_attr_value_name)
                    sku_all_sale_attr_vals_name[int(attr.id)].append(val.sale_attr_value_name)
                    sku_all_sale_attr_vals_id[int(attr.id)].append(val.id)
                    print(sku_all_sale_attr_vals_name, sku_all_sale_attr_vals_id)
            sku_details['sku_sale_attr_id'] = sku_sale_attr_id
            sku_details['sku_sale_attr_names'] = sku_sale_attr_names
            sku_details['sku_sale_attr_val_id'] = sku_sale_attr_val_id
            sku_details['sku_sale_attr_val_names'] = sku_sale_attr_val_names
            sku_details['sku_all_sale_attr_vals_id'] = sku_all_sale_attr_vals_id
            sku_details['sku_all_sale_attr_vals_name'] = sku_all_sale_attr_vals_name

            # sku规格部分
            # 用于存放规格相关数据，格式：{规格名称1: 规格值1, 规格名称2: 规格值2, ...}
            spec = dict()
            sku_spec_values = SKUSpecValue.objects.filter(sku=sku_id)
            if not sku_spec_values:
                sku_details['spec'] = dict()
            else:
                for sku_spec_value in sku_spec_values:
                    spec[sku_spec_value.spu_spec.spec_name] = sku_spec_value.name
                sku_details['spec'] = spec

            # 写入缓存
            redis_conn.setex("goods_%s" % sku_id, 60 * 60 * 24, json.dumps(sku_details))
        else:
            print("使用缓存")
            sku_details = json.loads(redis_detail)

        result = {'code': 200, 'data': sku_details, 'base_url': PIC_URL}
        return JsonResponse(result)

# 评论
# 点赞
# 收藏
#