from django.contrib import admin
from . import models

# Register your models here.
class TagManager(admin.ModelAdmin):
    # 在管理后台显示的字段
    list_display = ['id','tag_name','create_time','update_time']
    # 指定跳转在详情页面的字段
    list_display_links = ['id']
    # 可修改的字段
    # list_editable = ['name']
# 注册管理类
admin.site.register(models.Tag,TagManager)

class ForwardManager(admin.ModelAdmin):
    list_display = ['id','content','is_active','b_id','uid','create_time','update_time']
    list_display_links = ['id']
admin.site.register(models.Forward,ForwardManager)

class CommentManager(admin.ModelAdmin):
    list_display = ['id','content','is_active','b_id','uid','create_time','update_time']
admin.site.register(models.Comment,CommentManager)

class ReplyManager(admin.ModelAdmin):
    list_display = ['id','content','is_active','uid','create_time','update_time']
admin.site.register(models.Reply,ReplyManager)

class BlogManager(admin.ModelAdmin):
    list_display = ['id','title','content','is_active','uid','create_time','update_time']
admin.site.register(models.Blog,BlogManager)

class CollectManager(admin.ModelAdmin):
    list_display = ['id', 'b_id', 'is_active', 'uid', 'create_time', 'update_time']
admin.site.register(models.Collect, CollectManager)