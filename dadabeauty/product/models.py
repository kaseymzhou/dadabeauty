from django.db import models
from user.models import UserProfile

# Create your models here.
class GoodsCatalog(models.Model):
    name = models.CharField(verbose_name='产品类别名字',max_length=50)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'P_goods_catalog'

    def __str__(self):
        return 'id :%s; goods_name:%s' % (self.id, self.name)

class GoodsSubclass(models.Model):
    name = models.CharField(verbose_name='产品子类名字',max_length=50)
    gc_id = models.ForeignKey(GoodsCatalog)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'P_goosd_subclass'

    def __str__(self):
        return 'id :%s; goosd_subclass:%s' % (self.id, self.name)

class Brand(models.Model):
    name = models.CharField('品牌名',max_length=100)
    logo_url = models.ImageField(verbose_name='Logo图片')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'P_brand'

    def __str__(self):
        return 'id :%s; brand:%s' % (self.id, self.name)

class Spu(models.Model):
    name=models.CharField('spu名字',max_length=100)
    sb_id = models.ForeignKey(GoodsSubclass)
    br_id = models.ForeignKey(Brand)

    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'P_spu'

    def __str__(self):
        return 'id :%s; spu:%s' % (self.id, self.name)

class Source(models.Model):
    name = models.CharField('来源商城',max_length=30)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'P_source'

    def __str__(self):
        return 'id :%s; source:%s' % (self.id, self.name)


class Sku(models.Model):
    name = models.CharField('sku名字',max_length=100)
    spu_id = models.ForeignKey(Spu)
    source = models.ForeignKey(Source)
    default_img_url = models.ImageField('sku图片')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'P_sku'

    def __str__(self):
        return 'id :%s; sku:%s' % (self.id, self.name)

class sku_source(models.Model):
    sku_id = models.ForeignKey(Sku)
    source_id = models.ForeignKey(Source)
    price = models.DecimalField('价格',max_digits=10,decimal_places=2)
    source_url = models.URLField('来源网址')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'P_sku_source'

    def __str__(self):
        return 'id :%s; sku_source:%s' % (self.id, self.name)

class Sale_attr(models.Model):
    attr_name = models.CharField('产品属性名',max_length=50)
    spu_id = models.ForeignKey(Spu)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'P_Sale_attr'

    def __str__(self):
        return 'id :%s; sale_attr:%s' % (self.id, self.attr_name)

class Sale_attr_val(models.Model):
    val = models.CharField('产品属性值',max_length=50)
    sale_attr_id = models.ForeignKey(Sale_attr)
    sku_id = models.ForeignKey(Sku)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'P_Sale_attr_val'

    def __str__(self):
        return 'id :%s; Sale_attr_val:%s' % (self.id, self.val)

class Sku_img(models.Model):
    img_url = models.URLField('sku图片')
    sku_id = models.ForeignKey(Sku)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'P_Sku_img'

    def __str__(self):
        return 'id :%s' % (self.id)

class Comment(models.Model):
    content = models.TextField('评论')
    uid = models.ForeignKey(UserProfile)
    sku_id = models.ForeignKey(Sku)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)

    class Meta:
        db_table = 'P_Comment'

    def __str__(self):
        return 'id :%s' % (self.id)

class Reply(models.Model):
    content = models.TextField('评论回复')
    uid = models.ForeignKey(UserProfile)
    c_id = models.ForeignKey(Comment)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)

    class Meta:
        db_table = 'P_Comment'

    def __str__(self):
        return 'id :%s' % (self.id)

class Collect(models.Model):
    uid = models.ForeignKey(UserProfile)
    sku_id = models.ForeignKey(Sku)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)

    class Meta:
        db_table = 'P_Collect'

    def __str__(self):
        return 'id :%s' % (self.id)

class Tag(models.Model):
    name = models.CharField('商品标签名字',max_length=50)
    sku_id = models.ForeignKey(Sku)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'P_Tag'
    def __str__(self):
        return 'id :%s; name:%s' % (self.id,self.name)

