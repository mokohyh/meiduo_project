import json
import re
from django import http
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,redirect
from django.urls import reverse
from django.views import View
# Create your views here

from django_redis import get_redis_connection

from celery_tasks.email.tasks import send_verify_email
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from users.models import User

# 用户登录
from users.utils import generate_verify_email_url


class LoginView(View):
    '''用户登录'''
    def get(self,request):
        '''提供登录界面的'''
        return render(request, 'login.html')

    def post(self, request):
        """接收登录post表单"""
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 校验参数
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必传参数')
            # 判断用户名是否是5-20个字符
        if not re.match(r'[a-zA-Z0-9_-]{5,20}', username):
            return http.HttpResponseForbidden("请输入5-20个字符的用户名")

        # 判断密码是否是8-20个数字
        if not re.match(r'[a-zA-Z0-9_-]{8,20}', password):
            return http.HttpResponseForbidden("请输入8-20位的密码")

        # 认证用户
        user = authenticate(request=request, username = username, password = password)
        # 判断用户是否存在
        if user is None:
            return render(request, 'login.html',{'account_errmsg': '用户名或密码错误'})

        # 状态保持
        login(request, user)
        # 判断用户是是否记住登录
        if remembered == 'on':
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)

        # 获取从哪个url跳转过来，next值
        next = request.GET.get('next')
        # 判断是否想要跳转
        if next != None:
            # 响应结果
            response = redirect(next)
        else:
            # 响应结果
            response = redirect(reverse('contents:index'))
        # 登录成功，写入session
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response


# 用户登出
class LoginOutView(View):
    '''退出登录'''
    def get(self, request):
        '''实现登出逻辑'''
        # 清理session
        logout(request)

        # 退出登录重定向
        response = redirect(reverse('contents:index'))

        # 清理cookie
        response.delete_cookie('username')
        return response


# 用户中心
class UserInfoView(LoginRequiredMixin,View):
    '''用户中心'''
    def get(self, request):
        '''用户中心页面'''
        context={
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html',context)


# 邮箱修改
class EmailsView(LoginRequiredJSONMixin,View):
    '''邮箱修改'''
    def put(self, request):
        # 接收参数
        email_client = json.loads(request.body.decode())
        email = email_client.get('email')
        # 校验参数
        if not email:
            return http.HttpResponseForbidden('缺少email参数')
        if not re.match(r'[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}', email):
            return http.HttpResponseForbidden("参数不正确")

        # 赋值email字段
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            # 添加日志
            return http.JsonResponse({'code':RETCODE.DBERR, 'errmsg': '添加失败'})

        # 生成邮箱验证码
        verify_url = generate_verify_email_url(request.user)
        #  celery异步发送邮箱验证
        send_verify_email.delay(email, verify_url)



        return http.JsonResponse({'code':RETCODE.OK, 'errmsg': '添加邮箱成功'})


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


# 注册路由
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
        response = redirect(reverse("contents:index"))

        # 写入session
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        # 重定向到首页
        return response