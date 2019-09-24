from django import http
from django.core.cache import cache
from django.shortcuts import render
from django.views import View

from area.models import Area
from meiduo_mall.utils.response_code import RETCODE


class AreasView(View):
    '''省市区数据'''

    def get(self, request):
        '''提供省市区数据的'''

        #　获取参数
        area_id = request.GET.get('area_id')

        # 判断area_id是否存在
        if not area_id:

            # 读取缓存
            province_list = cache.get('province_list')
            # 判断是否有缓存
            if not province_list:
                # 不存在则说明前端需要的是省份信息
                try:
                    # 通过area_id=None查询
                    province_model_list = Area.objects.filter(parent__isnull = True)
                    # 序列化数据
                    province_list = []
                    for province_model in province_model_list:
                        province_list.append({
                            'id': province_model.id,
                            'name': province_model.name,
                        })

                except Exception as e:
                    # logger.error(e)
                    return http.JsonResponse({'code':RETCODE.DBERR, 'errmsg': '省份数据错误'})
                # 添加缓存
                cache.set('province_list', province_list, 3600)
            # 响应省份信息
            return http.JsonResponse({'code': RETCODE.OK, 'province_list': province_list})
        else:
            # 读取市或区缓存
            sub_data = cache.get('sub_area' + area_id)
            if not sub_data:
                # 查询市或县数据
                # 通过area_id来查询
                try:
                    parent_model = Area.objects.get(id=area_id)
                    sub_model_list = parent_model.subs.all()
                    # 序列化数据
                    sub_list = []
                    for sub_model in sub_model_list:
                        sub_list.append({
                            'id': sub_model.id,
                            'name': sub_model.name
                        })
                    sub_data = {
                        'id': parent_model.id,  # 父级pk
                        'name': parent_model.name,  # 父级name
                        'subs': sub_list  # 父级的子集
                    }


                except Exception as e:
                    # logger.error(e)
                    return http.JsonResponse({'code':RETCODE.DBERR, 'errmsg': '省份数据错误'})
                # 存储市或区
                cache.set('sub_area' + area_id, sub_data, 3600)
            # 响应市或区数据
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})





