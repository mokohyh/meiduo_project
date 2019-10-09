import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, user, response):
    '''
    登录后合并cookie购物车数据到Redis
    :param request: 本次请求对象，获取cookie中的数据
    :param user: 登录用户信息，获取user_id
    :param response: 本次请求对象，获取cookie中的数据, 清楚cookie
    :return: respsonse
    '''
    # 获取cookie中的购物车信息
    cookie_carts_str = request.COOKIES.get('carts')
    # 判断购物车中的信息是否存在
    if not cookie_carts_str:
        # 如果不存在不用合并
        return response
    # 如果存在需要合并
    cookie_carts_dict = pickle.loads(base64.b64decode((cookie_carts_str.encode())))
    # 准备新的数据容器： sku_id:count  selected   unselected
    new_cart_dict = {}
    new_cart_selected = []
    new_cart_selected_remove = []

    # 将cookie中的数据写入新容器
    # 遍历出cookie中的购物车信息
    for sku_id, cookie_dict in cookie_carts_dict.items():
        new_cart_dict[sku_id] = cookie_dict['count']
        if cookie_dict['selected']:
            new_cart_selected.append(sku_id)
        else:
            new_cart_selected_remove.append(sku_id)

    # 保存到redis数据库中
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()
    # 因为我们已cookie为准，因此将新构造的进行添加或覆盖
    pl.hmset('cart_%s' % user.id, new_cart_dict)
    # 添加被勾选状态
    if new_cart_selected:
        pl.sadd("selected_%s" % user.id, *new_cart_selected)
    if new_cart_selected_remove:
        pl.srem("selected_%s" % user.id, *new_cart_selected_remove)
    pl.execute()
    # 清除cookie
    response.delete_cookie('carts')

    return response
