from django import http
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render

# Create your views here.
from django.views import View

from contents.utils import get_categories
from goods import models
from goods.models import GoodsCategory, SKU
from goods.utils import get_beradcrumb
from meiduo_mall.utils.response_code import RETCODE


class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):
        """提供商品详情页"""
        # 获取当前sku的信息
        try:
            sku = models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return render(request, '404.html')

        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_beradcrumb(sku.category)

        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
        }
        return render(request, 'detail.html', context=context)

class HotGoodsView(View):
    '''热销排行商品'''
    def get(self, request, category_id):
        # 查询指定分类的sku，而且必须是上架商品，然后销量由高到底排序，最后进行切片
        skus = SKU.objects.filter(category_id = category_id, is_launched=True).order_by('-sales')[:2]
        # 构造json字典
        hot_skus = []
        for sku in skus:
            sku_dict = {
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url' : sku.default_image.url
            }
            hot_skus.append(sku_dict)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg':"OK", 'hot_skus':hot_skus})

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

        # 接收排序规则
        sort = request.GET.get('sort', 'default')
        # 按照排序规则查询该分类商品SKU信息
        # 注意一定是模型字段里的
        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            # 按销量降序
            sort_field = '-sales'
        else:
            sort = 'default'
            sort_field = 'create_time'
        # 商品排序
        skus = SKU.objects.filter(category=category, is_launched=True).order_by(sort_field)
        # 商品分页，创建分页器
        paginator = Paginator(skus, 5)      # 把skus分页，默认每页5条
        # 获取当前用户要查看的那一页
        try:
            page_skus = paginator.page(page_num)
        except EmptyPage:
            # 如果page_num不正确，默认给用户404
            return http.HttpResponseNotFound('empty page')
        # 获取总页数
        total_page = paginator.num_pages

        # 构造上下文
        context = {
            'categories' : categories,
            'beradcrumb' : beradcrumb,   # 面包屑导航
            'page_skus' : page_skus,     #当前页面的商品种类
            'total_page' : total_page,   # 总页数
            'page_num' : page_num,          # 当前页面
            'sort' : sort,               # 排序规则
            'category_id' : category_id, # 商品id
        }

        return render(request, 'list.html', context)
