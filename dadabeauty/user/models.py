from django.db import models

# Create your models here.
GENDER_CHOICE = (
    (1,'男'),
    (2,'女')
)

class UserProfile(models.Model):
    # 用户信息表
    username = models.CharField(max_length=20,verbose_name='用户昵称',unique=True)
    password = models.CharField(max_length=32,verbose_name='密码')
    email = models.EmailField()
    phone = models.CharField(max_length=11,verbose_name='联系电话',default='')
    gender = models.SmallIntegerField(verbose_name='性别',choices=GENDER_CHOICE)
    birthday = models.DateField()
    isActive = models.BooleanField(default=False,verbose_name='是否激活')
    profile_image_url = models.CharField(verbose_name='头像',default='/static/default_pic/default_profile.jpg',
                                         max_length=100)
    description = models.CharField(verbose_name='个性签名',null=True,max_length=100)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'uuser_profile'

    def __str__(self):
        return 'id :%s; username:%s'%(self.id,self.username)

class WeiboUser(models.Model):
    # 微博用户表
    uid = models.OneToOneField(UserProfile,null=True)
    wuid = models.CharField(max_length=50,db_index=True,verbose_name='微博用户id')
    access_token = models.CharField(max_length=100,verbose_name='授权令牌')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'uweibo_user'
    def __str__(self):
        return '%s_%s'%(self.wuid,self.uid)

class Interests(models.Model):
    # 可以提供给用户选择的用户感兴趣方向
    field = models.CharField(verbose_name='用户感兴趣的方向',max_length=30)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    class Meta:
        db_table = 'uinterests'
    def __str__(self):
        return '%s_%s'%(self.id,self.field)

class Interests_User(models.Model):
    uid = models.OneToOneField(UserProfile)
    iid = models.OneToOneField(Interests)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    class Meta:
        db_table = 'uinterests_user'

    def __str__(self):
        return '%s_%s' % (self.uid, self.iid)

class Follow(models.Model):
    followed_id = models.OneToOneField(UserProfile,related_name='followed_id',default='')
    fans_id = models.OneToOneField(UserProfile,related_name='fans_id',default='')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    class Meta:
        db_table = 'ufollow'
    def __str__(self):
        return '%s_%s'%(self.id,self.uid)
