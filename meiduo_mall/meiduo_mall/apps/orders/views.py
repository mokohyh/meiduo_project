import json
from decimal import Decimal

from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.views import View
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from orders.models import OrderInfo, OrderGoods
from users.models import Address


class OrderCommitView(LoginRequiredJSONMixin, View):
    '''提交订单'''
    def post(self,request):
        """保存订单信息和订单商品信息"""
        # 接收参数
        json_data = json.loads(request.body.decode())
        address_id = json_data.get('address_id')
        pay_method = json_data.get('pay_method')

        # 校验参数
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 判断address_id 是否有效
        try:
            address = Address.objects.get(id=address_id)
        except Exception:
            return http.HttpResponseForbidden('参数address_id错误')
        # 判断pay_method否有效
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method错误')

        # 获取登录用户
        user = request.user
        # 生成订单编号：年月日时分秒+用户编号
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

        # 显式的开启一个事务
        with transaction.atomic():
            # 创建事务保存点
            save_id = transaction.savepoint()

            try:
                # 保存订单基本信息 OrderInfo（一）
                order = OrderInfo.objects.create(
                order_id = order_id,
                user = user,
                address = address,
                total_count = 0,
                total_amount =Decimal('0'),
                freight = Decimal('10.00'),
                pay_method = pay_method,
                status =OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )


                # 从redis读取购物车中被勾选的商品信息
                redis_conn = get_redis_connection('carts')
                redis_carts = redis_conn.hgetall('cart_%s' % user.id)
                selected = redis_conn.smembers('selected_%s' % user.id)
                # 用一个空字典存储已被勾选的sku信息
                carts = {}
                for sku_id in selected:
                    # 获取对于的个数
                    carts[int(sku_id)] = int(redis_carts[sku_id])

                sku_ids = carts.keys()
                # 遍历这些已勾选的sku_id
                for sku_id in sku_ids:
                    # 查询sku信息
                    sku = SKU.objects.get(id=sku_id)
                    # 判断库存量
                    sku_count = carts[sku_id]
                    if sku_count > sku.stock:
                        transaction.savepoint_rollback(save_id)
                        return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

                    # 减少库存量,增加销量
                    sku.stock -= sku_count
                    sku.sales += sku_count
                    sku.save()

                    # 修改spu的销量
                    sku.spu.sales += sku_count
                    sku.spu.save()

                    # 保存订单商品信息 OrderGoods（多）
                    OrderGoods.objects.create(
                    order = order,
                    sku = sku,
                    count = sku_count,
                    price = sku.price,
                    )

                # 添加邮费
                order.total_amount += order.freight
                order.save()
            except Exception as e:
                # logger.error(e)
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})

            # 删除redis数据库中的操作
            pl = redis_conn.pipeline()
            pl.hdel('cart_%s' % user.id, *selected)
            pl.srem('selected_%s' % user.id, *selected)
            pl.execute()

        # 响应提交订单结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '下单成功', 'order_id': order.order_id})


class OrderSuccessView(LoginRequiredMixin, View):
    """提交订单成功"""

    def get(self, request):
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }
        return render(request, 'order_success.html', context)


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
        for skuu_id in carts_selected:
            cart[int(skuu_id)] = int(redis_carts[skuu_id])


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