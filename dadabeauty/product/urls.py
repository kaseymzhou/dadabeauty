from django.conf.urls import url
from . import views

urlpatterns = [
    # http://127.0.0.1:8000/v1/product/test
    url(r'^/test$',views.test),

    # http://127.0.0.1:8000/v1/product/index
    url(r'^/index$',views.IndexShow.as_view()),

    # http://127.0.0.1:8000/v1/product/list/subclass/1?page=1
    url(r'^/list/(?P<subclass_id>\d+)$',views.ProductsListView.as_view()),

    # http://127.0.0.1:8000/v1/product/detail/401/
    url(r'^/detail/(?P<sku_id>\d+)$',views.ProductsDetailView.as_view()),


    url(r'^/comment$',views.Comment_product.as_view()),


    url(r'^/reply$',views.Reply.as_view()),

    url(r'^/like$',views.LikeProduct.as_view()),

    url(r'^/collect$',views.CollectProducts.as_view),
]