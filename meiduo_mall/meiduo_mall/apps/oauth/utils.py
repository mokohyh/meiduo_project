from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings

from oauth import constants


def generate_eccess_token(openid):
    '''
    签名openid
    :param openid: 用户的openid
    :return: 加密的access_token
    '''
    serializer = Serializer(settings.SECRET_KEY, expires_in=constants.ACCESS_TOKEN_EXPIRES)
    data = {'openid': openid}
    token = serializer.dumps(data)
    return token.decode()

def check_access_token(openid):
    '''
    反序列openid
    :param openid: 用户传来的id
    :return: 解码的openid
    '''
    serializer = Serializer(settings.SECRET_KEY, expires_in=constants.ACCESS_TOKEN_EXPIRES)
    token = serializer.loads(openid)
    return token