import re

from django import http
from django.contrib.auth import login
from django.shortcuts import render,redirect
from django.urls import reverse
from django.views import View


# Create your views here.
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from users.models import User


class UsernameCountView(View):
    def get(self,request, username):
        '''
        :param request: 请求对象
        :param username: 用户名
        :return: JOSN
        '''

        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code':RETCODE.OK ,'errmsg':'ok', 'count':count})

class MobileCountView(View):
    def get(self,request, mobile):
        '''
        :param request: 请求对象
        :param mobile: 用户手机好
        :return: JSON
        '''

        count = User.objects.filter(mobile=mobile).count()
        print(count)
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'ok','count':count})

class Register(View):
    def get(self, request):
        '''
        提供方注册页面的
        :param request: 请求对象
        :return: 注册结果
        '''

        return render(request,'register.html')

    def post(self, request):
        # 获取参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        sms_code_client = request.POST.get('sms_code')

        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow, sms_code_client]):
            return http.HttpResponseForbidden("参数不全")

        # 判断用户名是否是5-20个字符
        if not re.match(r'[a-zA-Z0-9_-]{5,20}',username):
            return http.HttpResponseForbidden("请输入5-20个字符的用户名")

        # 判断密码是否是8-20个数字
        if not re.match(r'[a-zA-Z0-9_-]{8,20}', password):
            return http.HttpResponseForbidden("请输入8-20位的密码")

        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')

        # 判断手机号是否合法

        if not re.match(r'^1[3-9]\d{9}', mobile):
            return http.HttpResponseForbidden("您输入的手机号格式不正确")
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden("请勾选协议")

        # 保存注册数据之前，对比短信验证码
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request,'register.html',  {'sms_code_errmsg':'无效的短信验证码'})
        if sms_code_server.decode() != sms_code_client:
            return render(request, 'register.html', {'sms_code_errmsg': '输入短信验证码有误'})

        # 以上都没有错就执行注册数据库
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except:
            return render(request,'register.html', {'register_errmsg': '注册失败'})

        # 状态保持
        login(request, user, backend=None)


        # 重定向到首页
        return redirect(reverse("contents:index"))