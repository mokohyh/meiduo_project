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
from users.models import User, Address

# 用户登录
from users.utils import generate_verify_email_url, check_verify_email



class ChangePasswordView(LoginRequiredJSONMixin, View):
    '''修改密码'''
    def get(self, request):
        '''展示修改页面'''
        pass

    def post(self, request):
        '''修改密码'''
        pass



class UpdateTitleAddressView(LoginRequiredJSONMixin, View):
    '''设置地址标题'''
    def put(self, request, address_id):
        """修改地址标题"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')
        try:
            # 地址查询
            address = Address.objects.get(id=address_id)
            # 设置新的标题
            address.title = title
            address.save()

        except Exception as e:
            # logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置地址标题失败'})

            # 4.响应删除地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置地址标题成功'})



class DefaultAddressView(LoginRequiredJSONMixin, View):
    """设置默认地址"""
    def put(self, request, address_id):
        """设置默认的地址"""
        try:
            # 查询地址
            address = Address.objects.get(id=address_id)

            # 设置地址为默认地址
            request.user.default_address = address
            request.user.save()
        except Exception as e:
        # logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})
        # 响应设置默认地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})



class UpdateDestroyAddressView(LoginRequiredJSONMixin, View):
    '''修改和删除地址'''
    def put(self, request, address_id):
        '''修改地址'''
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')
        # 判断地址是否存在,并更新地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user= request.user,
                title = receiver,
                receiver = receiver,
                province = province_id,
                city = city_id,
                district = district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

        except Exception as e:
            # logger.error(e)
            return  http.JsonResponse({'code': RETCODE.DBERR, 'errmsg':'更新地址失败'})

        # 构造响应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})


    def delete(self, request, address_id):
        '''删除地址'''
        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)

            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:
            # logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})



class AddressView(LoginRequiredJSONMixin, View):
    '''用户收货地址'''

    def get(self, request):
        '''提供收货地址页面'''
        #  获取用户地址表
        login_user = request.user
        # 查询该用户的地址
        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        address_dict_list = []
        for address in addresses:
            address_dict_list.append({
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email

            })
        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_dict_list,
        }

        return render(request, 'user_center_site.html', context)


class CreateAddressView(LoginRequiredJSONMixin, View):
    '''新增地址'''
    def post(self,request):
        '''实现新增地址逻辑'''
        # 判断是否超过20个地址
        count = Address.objects.filter(user=request.user, is_deleted = False).count()
        # count = request.user.addresses.count()
        if count > 20:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})

        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 保存地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            # logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 新增地址成功，将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        # 响应保存结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


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

class VerifyEmailView(View):
    '''验证邮箱'''

    def get(self,request):
        '''实现验证链接'''

        # 接收参数
        token = request.GET.get('token')
        # 校验参数
        if not token:
            return http.HttpResponseForbidden('缺少token参数')
        # 使用解码工具check_verify_email解码token，提取出user
        user = check_verify_email(token)
        # 判断user是否有效
        if not user:
            return http.HttpResponseForbidden('无效的token参数')
        #　修改数据的邮箱激活状态
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            # logger.error(e)
            return http.HttpResponseServerError('激活邮件失败')
        # 返回响应
        return redirect(reverse('users:info'))



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