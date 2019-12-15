from django.conf.urls import url
from . import views

urlpatterns = [
    # 用户注册 http://127.0.0.1:8000/v1/user
    url(r'^$',views.Users.as_view()),

    # v1/token POST 创建token - 登录

    # 用户激活
    # http://127.0.0.1:7000/dadashop/templates/active.html?code=emhvdW1pbjFfNjMzNg==
    # http://127.0.0.1:8000/v1/user/activation
    url(r'^/activation$', views.users_active),

    # 用于前端获取微博登录地址
    # http://127.0.0.1:8000/v1/user/weibo/authorization POST 创建校验 登录
    url(r'^/weibo/authorization$', views.OAuthWeiboUrlView.as_view()),


    # 接收前端微博code
    # http://127.0.0.1:8000/v1/user/weibo/users
    url(r'^/weibo/users$', views.OAuthWeiboView.as_view()),

    # http://127.0.0.1:8000/v1/user/interested
    url(r'^/interested$',views.InterestedChoiceView.as_view()),

    # http://127.0.0.1:8000/v1/user/further_info
    url(r'^/further_info',views.FurtherInfoView.as_view()),

    # http://127.0.0.1:8000/v1/user/fan
    url(r'^/fan',views.FanView.as_view()),

    # http://127.0.0.1:8000/v1/user/personindex/(user_id)
    url(r'^/personindex/(\d+)$',views.PersonalIndex.as_view()),

    # http://127.0.0.1:8000/v1/user/focus/(user_id)
    url(r'^/focus/(\d+)$',views.FocusView.as_view()),

    # http://127.0.0.1:8000/v1/user/fan/(user_id)
    url(r'^/fans/(\d+)$',views.FansView.as_view()),

    # http://127.0.0.1:8000/v1/user/collectpro/(user_id)
    url(r'^/collectpro/(\d+)$',views.CollectProductView.as_view()),

    # http://127.0.0.1:8000/v1/user/collectblog/(user_id)
    url(r'^/collectblog/(\d+)$',views.CollectBlogView.as_view()),

    # http://127.0.0.1:8000/v1/user/personalinfo/(user_id)
    url(r'^/personalinfo/(\d+)$',views.ChangePersonalInfo.as_view()),

    # http://127.0.0.1:8000/v1/user/password
    url(r'^/password$',views.ChangePassword.as_view())




]