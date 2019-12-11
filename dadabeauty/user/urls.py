from django.conf.urls import url
from . import views

urlpatterns = [
    #http://127.0.0.1:8000/v1/user
    url(r'^$',views.Users.as_view()),

    # v1/token POST 创建token - 登录
    # v1/authorization POST 创建校验 登录
    # http://127.0.0.1:7000/dadashop/templates/active.html?code=emhvdW1pbjFfNjMzNg==
    url(r'^/activation$', views.users_active),

    # 用于前端获取微博登录地址
    url(r'^/weibo/authorization$', views.OAuthWeiboUrlView.as_view()),
    # 接收前端微博code
    url(r'^/weibo/users$', views.OAuthWeiboView.as_view()),

    url(r'^/interested$',views.InterestedChoiceView.as_view()),

    url(r'^/further_info',views.FurtherInfoView.as_view()),

    url(r'^/fan',views.FanView.as_view())

]