from django.contrib import admin
from . import models

# Register your models here.
class InterestsManager(admin.ModelAdmin):
    # 在管理后台显示的字段
    list_display = ['id','field','created_time','updated_time','isActive']
    # 指定跳转在详情页面的字段
    list_display_links = ['id']
    # 可修改的字段
    list_editable = ['field']
# 注册管理类
admin.site.register(models.Interests,InterestsManager)

class FollowManager(admin.ModelAdmin):
    # 在管理后台显示的字段
    list_display = ['id','followed_id','fans_id','created_time','updated_time','isActive']
    # 指定跳转在详情页面的字段
    list_display_links = ['id']
# 注册管理类
admin.site.register(models.FollowUser,FollowManager)