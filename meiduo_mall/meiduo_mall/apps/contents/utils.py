from collections import OrderedDict

from goods.models import GoodsChannel


def get_categories():
    '''商品分页'''
    # 查询商品频道和分类
    categories = OrderedDict()
    # 进行排序
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    for channel in channels:
        group_id = channel.group_id

        # 不重复遍历分组,构建有序字典
        if group_id not in categories:
            categories[group_id] = {
                'channels': [],
                'sub_cats': [],
            }
        # 获取当前频道类别(多对一的关系)
        cat1 = channel.category
        # 追加当前频道
        categories[group_id]['channels'].append({
            "id": cat1.id,
            "name": cat1.name,
            'url': channel.url
        })

        # 构建当前子类商品类别
        for cat2 in cat1.subs.all():
            cat2.sub_cats = []
            for cat3 in cat2.subs.all():
                cat2.sub_cats.append(cat3)
            categories[group_id]['sub_cats'].append(cat2)

    return categories