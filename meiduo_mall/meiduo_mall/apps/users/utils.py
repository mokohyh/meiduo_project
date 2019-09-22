from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from itsdangerous import BadData
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import re

from users import constants
from .models import User


def check_verify_email(token):
    '''
    反序列化接收的ｔｏｋｅｎ，　提取user
    :param token: 用户签名后的结果
    :return: usre,None
    '''

    serializer = Serializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    try:
        data = serializer.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user


def generate_verify_email_url(user):
    '''
    生成邮箱的验证链接
    :param user: 当前用户
    :return: verify_url
    '''
    serializer = Serializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    data = {
        'user_id': user.id,
        'email': user.email
    }
    token = serializer.dumps(data).decode()
    verify_url = settings.EMAIL_VERIFY_URL + '?token' + token
    return verify_url



def get_user_by_account(account):
    try:
        if re.match(r'^1[3-9]\d{9}', account):
            # 手机号登录
            user = User.objects.get(mobile=account)
        else:
            # 用户名登录
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user

class UsernameMobileAuthBackend(ModelBackend):
    """自定义用户认证后端"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重写认证方法，实现多账号登录
        :param request: 请求对象
        :param username: 用户名
        :param password: 密码
        :param kwargs: 其他参数
        :return: user
        """
        # 根据传入的username获取user对象。username可以是手机号也可以是账号
        user = get_user_by_account(username)
        # 校验user是否存在并校验密码是否正确
        if user and user.check_password(password):
            return user