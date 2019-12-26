
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^/sendtopics$',views.Send_topics.as_view()),
    # http://127.0.0.1:8000/v1/community/index  访问所有博客
    # http://127.0.0.1:8000/v1/community/index?tag=xxx  访问tag标签博客
    url(r'^/index$',views.index),
    url(r'^/myindex$',views.MyIndex.as_view()),
    url(r'^/detail$',views.DeatilBlog.as_view()),
    url(r'^/forward$',views.ForwardBlog.as_view()),
    url(r'^/like$',views.LikeBlog.as_view()),
    url(r'^/comment$',views.BlogComment.as_view()),
    url(r'^/reply$',views.BlogReply.as_view()),
    url(r'^/collect$',views.CollectBlogs.as_view()),
    # http://127.0.0.1:8000/v1/community/index_collect?authorname=xxx
    url(r'^/index_collect$',views.MyIndexCollect.as_view()),
    url(r'^/others_index_collect$',views.OtherIndexCollect.as_view()),
    url(r'^/others_index$',views.OtherIndex.as_view()),
    url(r'^/delete_blog$',views.DeleteBlog.as_view())
]