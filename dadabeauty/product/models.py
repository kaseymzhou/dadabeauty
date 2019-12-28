from django.db import models
from django.utils import timezone

from user.models import UserProfile

# Create your models here.
class GoodsCatalog(models.Model):
    name = models.CharField(verbose_name='产品类别名字',max_length=50)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pgoods_catalog'

    def __str__(self):
        return 'id :%s; goods_name:%s' % (self.id, self.name)

class GoodsSubclass(models.Model):
    name = models.CharField(verbose_name='产品子类名字',max_length=50)
    gc_id = models.ForeignKey(GoodsCatalog)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pgoosd_subclass'

    def __str__(self):
        return 'id :%s; goosd_subclass:%s' % (self.id, self.name)

class Brand(models.Model):
    name = models.CharField('品牌名',max_length=100)
    logo_url = models.ImageField(verbose_name='Logo图片')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pbrand'

    def __str__(self):
        return 'id :%s; brand:%s' % (self.id, self.name)

class Spu(models.Model):
    name=models.CharField('spu名字',max_length=100)
    sb_id = models.ForeignKey(GoodsSubclass)
    br_id = models.ForeignKey(Brand)
    created_time = models.DateTimeField(default=timezone.now)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pspu'

    def __str__(self):
        return 'id :%s; spu:%s' % (self.id, self.name)

class Source(models.Model):
    name = models.CharField('来源商城',max_length=30)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'psource'

    def __str__(self):
        return 'id :%s; source:%s' % (self.id, self.name)


class Sku(models.Model):
    name = models.CharField('sku名字',max_length=100)
    spu_id = models.ForeignKey(Spu)
    source_id = models.ForeignKey(Source,default='')
    default_img_url = models.URLField('sku图片',default='')
    feature = models.CharField(verbose_name='特点',max_length=100,default='')
    price = models.DecimalField('价格', max_digits=10, decimal_places=2,default=0)
    discount_price = models.DecimalField('折扣价', max_digits=10, decimal_places=2,default=0)
    source_url = models.URLField('来源网址',default='')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'psku'

    def __str__(self):
        return 'id :%s; sku:%s' % (self.id, self.name)


class Sale_attr(models.Model):
    attr_name = models.CharField('产品属性名',max_length=50)
    spu_id = models.ForeignKey(Spu)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'psale_attr'

    def __str__(self):
        return 'id :%s; sale_attr:%s' % (self.id, self.attr_name)

class Sale_attr_val(models.Model):
    val = models.CharField('产品属性值',max_length=50,default='')
    sale_attr_id = models.ForeignKey(Sale_attr)
    sku_id = models.ForeignKey(Sku)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'psale_attr_val'

    def __str__(self):
        return 'id :%s; Sale_attr_val:%s' % (self.id, self.val)

class Comment(models.Model):
    content = models.TextField('评论')
    uid = models.ForeignKey(UserProfile)
    sku_id = models.ForeignKey(Sku)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)

    class Meta:
        db_table = 'pcomment'

    def __str__(self):
        return 'id :%s' % (self.id)

class ReplyProduct(models.Model):
    content = models.TextField('评论回复')
    uid = models.ForeignKey(UserProfile)
    c_id = models.ForeignKey(Comment)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)

    class Meta:
        db_table = 'preply'

    def __str__(self):
        return 'id :%s' % (self.id)

class Collect(models.Model):
    uid = models.ForeignKey(UserProfile)
    sku_id = models.ForeignKey(Sku)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)

    class Meta:
        db_table = 'pcollect'

    def __str__(self):
        return 'id :%s' % (self.id)


class LikeProduct(models.Model):
    uid = models.ForeignKey(UserProfile)
    sku_id = models.ForeignKey(Sku)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)

    class Meta:
        db_table = 'plike'

    def __str__(self):
        return 'id :%s' % (self.id)

class ProductScore(models.Model):
    uid = models.ForeignKey(UserProfile)
    sku_id = models.ForeignKey(Sku)
    score = models.IntegerField(verbose_name='分数')

    class Meta:
        db_table = 'pscore'

    def __str__(self):
        return "uid(%s)-sku_id(%s)-score(%s)"%(self.uid,self.sku_id,self.score)

class PredictSkuScore(models.Model):
    user_id = models.ForeignKey(UserProfile)
    sku_id = models.ForeignKey(Sku)
    predict_score = models.FloatField(verbose_name='预测分数')
    product_type = models.IntegerField(verbose_name="从产品分类")
    class Meta:
        db_table = 'predict_sku_score'
    def __str__(self):
        return "uid(%s)-sku(%s)"%(self.user_id,self.sku_id)
