import random
from django import http
from django.shortcuts import render
# from verifications.libs.twilio_send_note.send_note import Note

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from verifications.libs.captcha.captcha import captcha

# 短信验证码
class SMSCodeView(View):
    def get(self,request, mobile):
        '''
        :param request: 接收请求
        :param mobile: 用户手机号
        :return: JSON
        '''
        # 接收参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 校验参数
        if not all([uuid, image_code_client]):
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})

        # 提取图片验证码
        redis_conn = get_redis_connection('verify_code')
        image_code_server = redis_conn.get('img_%s'%uuid)
        if image_code_server == None:
            return http.JsonResponse({'code':RETCODE.THROTTLINGERR, 'errmsg': '验证码已失效'})
        # 删除图形验证码
        redis_conn.delete('img_%s'%uuid)

        # 注意，redis里读取的数据是二进制类型
        image_code_server = image_code_server.decode()
        # 对比图形验证码,转为小写
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code':RETCODE.IMAGECODEERR, 'errmsg': '验证码有误'})

        # 生成短信验证码
        sms_code = '%06d'%random.randint(0,999999)
        # logger.info(sms_code)
        # 保存短信验证码
        redis_conn.setex('sms_%s'%uuid, 300, sms_code)
        # 发送短信（这里使用twilio发送短信）
        # Note类的send_one_note方法的参数
        #sms_code是短信验证吗, expiration_time是过期时间,mobile手机号
        expiration_time = 1
        # Note().send_one_note(sms_code, expiration_time,mobile)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})



# 图片验证码
class ImageCodeView(View):
    def get(self,request, uuid):
        '''
        :param request: 请求对象
        :param uuid: 唯一标识图形验证码所属的用户
        :return: 图形验证码
        '''
        # 实现主体业务逻辑： 生成，保存， 响应图形验证码
        # 生成图形验证码
        print(uuid)
        text, image = captcha.generate_captcha()
        # 保存图形验证码
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s'%uuid, 300, text)
        # 响应图形验证码
        return http.HttpResponse(image, content_type='image/jpg')



