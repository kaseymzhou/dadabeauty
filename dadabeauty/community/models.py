from django.db import models
from user.models import UserProfile
# Create your models here.

class Tag(models.Model):
    tag_name = models.CharField('标签名', max_length=20)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'ctag'

    def __str__(self):
        return 'tag_name:%s' % (self.tag_name,)



class Blog(models.Model):
    title = models.CharField('标题', max_length=100)
    content = models.TextField(verbose_name='文章内容')
    like_count = models.IntegerField(default=0,verbose_name='点赞数量')
    forward_count = models.IntegerField(default=0, verbose_name='转发数量')
    collect_count = models.IntegerField(default=0, verbose_name='收藏数量')
    comment_count = models.IntegerField(default=0, verbose_name='评论数量')
    uid = models.ForeignKey(UserProfile)
    tid=models.ForeignKey(Tag)
    is_active = models.BooleanField(default=True, verbose_name='删除与否')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'cblog'

    def __str__(self):
        return 'title:%s content:%s forward_count:%s collect_count:%s comment_count:%s' % (
        self.title, self.content, self.forward_count, self.collect_count, self.comment_count)


class Image(models.Model):
    b_id = models.ForeignKey(Blog)
    image = models.ImageField(verbose_name='图片路径',default=0)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'cimage'


class Comment(models.Model):
    content = models.TextField(verbose_name='评论内容')
    is_active = models.BooleanField(default=True, verbose_name='删除与否')
    b_id = models.ForeignKey(Blog)
    uid = models.ForeignKey(UserProfile,related_name='comment_uid')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'ccomment'

    def __str__(self):
        return 'content:%s' % (self.content)


class Reply(models.Model):
    content = models.TextField(verbose_name='回复内容')
    is_active = models.BooleanField(default=True, verbose_name='删除与否')
    c_id = models.ForeignKey(Comment)
    uid = models.ForeignKey(UserProfile,related_name='reply_uid')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'creply'

    def __str__(self):
        return 'reply_content:%s' % (self.content)


class Collect(models.Model):
    is_active = models.BooleanField(default=True, verbose_name='删除与否')
    b_id = models.ForeignKey(Blog)
    uid = models.ForeignKey(UserProfile,related_name='collect_uid')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'ccollect'


class Forward(models.Model):
    content = models.CharField(verbose_name='转发内容', max_length=200)
    is_active = models.BooleanField(default=True, verbose_name='删除与否')
    b_id = models.ForeignKey(Blog)
    uid = models.ForeignKey(UserProfile)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'cforward'

    def __str__(self):
        return 'forward_content:%s' % (self.content)