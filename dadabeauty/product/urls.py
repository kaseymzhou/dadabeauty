from django.conf.urls import url
from . import views

urlpatterns = [
    # http://127.0.0.1:8000/v1/product/test
    url(r'^/test$',views.test),

    # http://127.0.0.1:8000/v1/product/index
    url(r'^/index$',views.IndexShow.as_view()),

    # http://127.0.0.1:8000/v1/product/list/subclass/1?page=1
    url(r'^/list/subclass/(?P<subclass_id>\d+)$',views.ProductsListView.as_view()),

    # http://127.0.0.1:8000/v1/product/detail/401
    url(r'^/detail/(?P<sku_id>\d+)$',views.ProductsDetailView.as_view()),

    # http://127.0.0.1:8000/v1/product/comment
    url(r'^/comment$',views.Comment_product.as_view()),

    # http://127.0.0.1:8000/v1/product/reply
    url(r'^/reply$',views.Reply.as_view()),

    # http://127.0.0.1:8000/v1/product/like
    url(r'^/like$',views.LikeP.as_view()),

    # http://127.0.0.1:8000/v1/product/collect
    url(r'^/collect$',views.CollectProducts.as_view()),

    # http://127.0.0.1:8000/v1/product/score
    url(r'^/score$',views.PScore.as_view()),

    # http://127.0.0.1:8000/v1/product/collectpro/(user_id)
    url(r'^/collectpro/(\d+)$',views.CollectProductView.as_view()),

    # http://176.122.12.156:8000/v1/product/others_collect_product/(username)
    url(r'^/others_collect_product/(.*)$',views.OthersCollectProductView.as_view()),


]