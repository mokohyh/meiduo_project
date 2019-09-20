import re

from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.conf import settings
from django.contrib.auth import login
from django.db import DatabaseError
from django.shortcuts import render,redirect

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.settings import dev
from oauth.models import OAuthQQUser
from oauth.utils import generate_eccess_token, check_access_token
from users.models import User


class QQAuthURLView(View):
    '''提供qq登录
    https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=xxx&redirect_uri=xxx&state=xxx
    '''

    def get(self, request):
        # 获取next，示从哪个页面进入到的登录页面，将来登录成功后，就自动回到那个页面
        next = request.GET.get('next')
        # 获取qq登录页面的网址
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        # oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        # 生成qq扫码链接地址
        login_url = oauth.get_qq_url()
        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})





class QQAuthUserView(View):
    '''扫码登录后的回调处理'''
    def get(self,request):
        '''Oauth2.0认证'''
        # 接收Authorization Code
        code = request.GET.get('code')
        # 判断是否有code
        if not code:
            return http.HttpResponseForbidden('缺少code')

        # 创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            # 通过code获取access_token。向qq服务器发送请求了
            access_token = oauth.get_access_token(code)
            # 通过access_token获取open_id
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            # logger.error(e)
            return http.HttpResponseServerError('OAuth2.0认证失败')

        # 判断是否为美多用户
        # 通过opent_id为查绚条件查绚
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 没有openid就没有绑定美多
            access_token = generate_eccess_token(openid)
            context = {'access_token': access_token}
            return render(request, 'oauth_callback.html', context)
        else:
            # 有openid则已绑定美多
            # 实现状态保持,  注意，使用的用户是user
            qq_user = oauth_user.user
            login(request,qq_user)

            # 响应结果
            next = request.GET.get('next')
            response = redirect(next)

            # 设置cookie
            response.set_cookie('username', qq_user.username, max_age=600 * 24 * 15)

            return response

    def post(self, request):
        '''美多商城用户绑定'''
        # 接收参数
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        access_token = request.POST.get('access_token')
        print(access_token)

        # 校验参数
        # 判断参数是否齐全
        if not all([mobile, pwd, sms_code_client, access_token]):
            return http.HttpResponseForbidden("参数不全")
        # 判断手机号是否合格
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden("请输入正确的手机号码")
            # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', pwd):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断短信验证码是否一致
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})
        # 判断openid是否有效：错误提示放在sms_code_errmsg位置
        openid = check_access_token(access_token)
        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': '无效的openid'})

        # 保存注册信息
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 用户不存在，新建用户
            user = User.objects.create_user(username=mobile, password=pwd, mobile=mobile)
        else:
            # 用户存在，检查密码
            if not user.check_password(pwd):
                return render(request, 'oauth_callback.html', {'account_errmsg': '用户名或密码错误'})

        # 将用户绑定openid
        try:
            OAuthQQUser.objects.create(openid=openid, user=user)
        except DatabaseError:
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': 'QQ登录失败'})

        # 实现状态保持
        login(request, user)

        # 响应绑定结果
        next = request.Get.get('next')
        response = redirect(next)

        # 设置cookie
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        return response
