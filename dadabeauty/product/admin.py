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
    list_display = ['id','name','logo_url','created_time','updated_time']
    list_display_links = ['id']
admin.site.register(models.Brand,BrandManager)


class SpuManager(admin.ModelAdmin):
    list_display = ['id','name','sb_id','br_id','created_time','updated_time']
    list_display_links = ['id']
admin.site.register(models.Spu,SpuManager)

class SourceManager(admin.ModelAdmin):
    list_display = ['id','name','created_time','updated_time']
    list_display_links = ['id']
admin.site.register(models.Source,SourceManager)


