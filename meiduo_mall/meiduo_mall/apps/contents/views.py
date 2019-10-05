from collections import OrderedDict

from django.shortcuts import render


from django.views import View

from contents.models import ContentCategory
from contents.utils import get_categories
from goods.models import GoodsCategory, GoodsChannelGroup, GoodsChannel
# Create your views here.


class IndexView(View):
    '''首页广告'''
    def get(self, request):
        '''提供首页广告数据的'''
        # 查询商品分类
        categories = get_categories()

        # 构建广告类别
        contents = {}
        # 查询广告类别
        content_categories = ContentCategory.objects.all()
        # 遍历类别类别，查询内容
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')


        # 渲染模板的上下文
        context = {
            'categories': categories,
            'contents': contents,
        }
        return render(request, 'index.html',context)