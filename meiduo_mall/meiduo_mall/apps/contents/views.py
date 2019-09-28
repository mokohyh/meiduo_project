from collections import OrderedDict

from django.shortcuts import render


from django.views import View

from contents.models import ContentCategory
from goods.models import GoodsCategory, GoodsChannelGroup, GoodsChannel
# Create your views here.


class IndexView(View):
    '''首页广告'''
    def get(self, request):
        '''提供首页广告数据的'''
        # 查询商品频道和分类
        categories = OrderedDict()
        # 进行排序
        channels = GoodsChannel.objects.order_by('group_id', 'sequence')
        for channel in channels:
            group_id = channel.group_id

            # 不重复遍历分组,构建有序字典
            if group_id not in categories:
                categories[group_id] = {
                    'channels':[],
                    'sub_cats':[],
                }
            # 获取当前频道类别(多对一的关系)
            cat1 = channel.category
            # 追加当前频道
            categories[group_id]['channels'].append({
                "id": cat1.id,
                "name": cat1.name,
                'url' : channel.url
            })

            # 构建当前子类商品类别
            for cat2 in cat1.subs.all():
                cat2.sub_cats = []
                for cat3 in cat2.subs.all():
                    cat2.sub_cats.append(cat3)
                categories[group_id]['sub_cats'].append(cat2)

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