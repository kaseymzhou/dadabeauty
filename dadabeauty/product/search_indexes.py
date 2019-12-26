from haystack import indexes
# 1. 改成你自己的model

from .models import Sku
# 2. 类名为模型类的名称+Index,比如模型类为Type,则这里类名为TypeIndex

class SkuIndex(indexes.SearchIndex, indexes.Indexable):
# 指明哪些字段产生索引,产生索引的字段,会作为前端检索查询的关键字;
# document是指明text是使用的文档格式,产生字段的内容在文档中进行描述;
# use_template是指明在模板中被声明需要产生索引;
    text = indexes.CharField(document=True, use_template=True)

    #3. 返回的是你自己的model
    def get_model(self):
        """返回建立索引的模型类"""
        return Sku

    # 4. 修改return 可以修改返回查询集的内容,比如返回时,有什么条件限制
    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.all()