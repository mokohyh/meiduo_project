from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from goods.models import SKU
from users.models import Address


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        """提供订单结算页面"""
        # 用户登录的用户
        user = request.user
        # 获取用户地址, 需要限制条件是否是逻辑删除的地址
        try:
            addresses = Address.objects.filter(user=user, is_deleted = False)
        except Address.DoesNotExist:
            addresses = None

        # 获取已勾选商品
        redis_conn = get_redis_connection('carts')
        redis_carts = redis_conn.hgetall('cart_%s' % user.id)
        carts_selected = redis_conn.smembers('selected_%s' % user.id)

        # 暂时储存已勾选商品信息
        cart = {}
        # 循环出已勾选商品id
        for sku_id in carts_selected:
            cart[int(sku_id)] = redis_carts[sku_id]

        # 准备初始值
        # 商品件数
        total_count = 0
        # 商品总额
        total_amount = Decimal(0.00)

        # 查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            # 计算单个商品的小计
            sku.count = int(cart[sku.id])
            sku.amount = sku.count * sku.price
            # 计算总额
            total_count += sku.count
            total_amount += sku.amount

        # 添加运费
        freight = Decimal('10.00')

        # 构造上下文
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            # 运费
            'freight': freight,
            'payment_amount': total_amount + freight
        }
        return render(request, 'place_order.html', context)