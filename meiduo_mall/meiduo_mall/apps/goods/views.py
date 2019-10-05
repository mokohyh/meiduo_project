from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

from contents.utils import get_categories
from goods.models import GoodsCategory
from goods.utils import get_beradcrumb


class ListView(View):
    '''提供列表页'''
    def get(self,request,category_id,page_num):
        '''提供列页'''
        # 校验参数
        try:
            # 三级类别
            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            return http.HttpResponseNotFound('GoodsCategory does not exist')

        # 面包屑导航
        beradcrumb = get_beradcrumb(category)


        # 查询商品分类
        categories = get_categories()

        # 构造上下文
        context = {
            'categories':categories,
            'beradcrumb':beradcrumb,   # 面包屑导航
        }

        return render(request, 'list.html', context)
