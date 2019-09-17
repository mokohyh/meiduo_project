import random
from django import http
from django.shortcuts import render
from verifications.libs.twilio_send_note.send_note import Note

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from verifications.libs.captcha.captcha import captcha


class SMSCodeView(View):
    def get(self,request, mobile):
        pass

class ImageCodeView(View):
    def get(self,request, uuid):
        '''
        :param request: 请求对象
        :param uuid: 唯一标识图形验证码所属的用户
        :return: 图形验证码
        '''
        # 实现主体业务逻辑： 生成，保存， 响应图形验证码
        # 生成图形验证码
        text, image = captcha.generate_captcha()
        # 保存图形验证码
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s'%uuid, 300, text)
        # 响应图形验证码
        return http.HttpResponse(image, content_type='image/jpg')



