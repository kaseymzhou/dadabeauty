from django.contrib import admin
from . import models

# Register your models here.
class GoodsCatalogManager(admin.ModelAdmin):
    # 在管理后台显示的字段
    list_display = ['id','name','created_time','updated_time']
    # 指定跳转在详情页面的字段
    list_display_links = ['id']
    # 可修改的字段
    # list_editable = ['name']
# 注册管理类
admin.site.register(models.GoodsCatalog,GoodsCatalogManager)

class GoodsSubclassManager(admin.ModelAdmin):
    list_display = ['id','name','gc_id','created_time','updated_time']
    list_display_links = ['id']
admin.site.register(models.GoodsSubclass,GoodsSubclassManager)

class BrandManager(admin.ModelAdmin):
    list_display = ['id','name','logo_url']
    list_display_links = ['id']
admin.site.register(models.Brand,BrandManager)

class SpuManager(admin.ModelAdmin):
    list_display = ['id','name','sb_id','br_id','created_time','updated_time']
    list_editable = ['name','sb_id','br_id']
    list_display_links = ['id']
admin.site.register(models.Spu,SpuManager)

class SourceManager(admin.ModelAdmin):
    list_display = ['id','name']
    list_display_links = ['id']
admin.site.register(models.Source,SourceManager)

class SkuManager(admin.ModelAdmin):
    list_display = ['id',
                    'name',
                    'spu_id',
                    'source_id',
                    'default_img_url',
                    'feature','price',
                    'discount_price',
                    'source_url',
                    'created_time',
                    'updated_time']
    list_display_links = ['id']
admin.site.register(models.Sku, SkuManager)

class Sale_attr_valManager(admin.ModelAdmin):
    list_display = ['id','val','sale_attr_id','sku_id','created_time','updated_time']
    list_editable = ['val','sale_attr_id','sku_id']
    list_display_link = ['id']
admin.site.register(models.Sale_attr_val,Sale_attr_valManager)

class Sale_attrManager(admin.ModelAdmin):
    list_display = ['id','attr_name','spu_id','created_time','updated_time']
    list_editable = ['attr_name','spu_id']
    list_display_links = ['id']
admin.site.register(models.Sale_attr,Sale_attrManager)

class CommentManager(admin.ModelAdmin):
    list_display = ['id','content','uid','sku_id','created_time','updated_time','isActive']
admin.site.register(models.Comment,CommentManager)

class ReplyManager(admin.ModelAdmin):
    list_display = ['id','content','uid','c_id','created_time','updated_time','isActive']
admin.site.register(models.ReplyProduct,ReplyManager)

class CollectManager(admin.ModelAdmin):
    list_display = ['id','uid','sku_id','created_time','updated_time','isActive']
admin.site.register(models.Collect,CollectManager)

class LikeManager(admin.ModelAdmin):
    list_display = ['id','uid','sku_id','created_time','updated_time','isActive']
admin.site.register(models.LikeProduct,LikeManager)

