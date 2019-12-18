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
