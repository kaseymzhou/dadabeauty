from django.conf.urls import url
from . import views

urlpatterns = [
    #test http://127.0.0.1:8000/v1/user/test
    url(r'^/test$',views.Test.as_view()),

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

    # http://127.0.0.1:8000/v1/user/uid/profile_img
    url(r'/(\d+)/profile_img',views.ProfileImg.as_view()),

    # http://127.0.0.1:8000/v1/user/person_description
    url(r'/person_description',views.PersonDescription.as_view()),

    # http://127.0.0.1:8000/v1/user/uid/fan
    url(r'^/(\d+)/fan$',views.FansView.as_view()),

    # http://127.0.0.1:8000/v1/user/(user_id)/focus
    url(r'^/(\d+)/focus$',views.FocusView.as_view()),

    # http://127.0.0.1:8000/v1/user/addfan
    url(r'^/addfan$',views.AddFan.as_view()),

    # http://127.0.0.1:8000/v1/user/personalinfo/(user_id)
    url(r'^/personalinfo/(\d+)$',views.ChangePersonalInfo.as_view()),

    # http://127.0.0.1:8000/v1/user/password
    url(r'^/password$',views.ChangePassword.as_view()),

    # http://127.0.0.1:8000/v1/user/test_celery
    # url(r'^/test_celery$',views.ChangePassword.as_view()),

    # http://127.0.0.1:8000/v1/user/other_fan/(username)
    url(r'^/other_fan/(.*)$',views.OthersFansView.as_view()),

    # http://127.0.0.1:8000/v1/user/other_follow/(username)
    url(r'^/others_follow/(.*)$',views.OthersFocusView.as_view()),


]