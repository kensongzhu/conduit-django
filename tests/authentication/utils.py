import jwt

from conduit import settings


def gen_user_token(pk, dt):
    token = jwt.encode({
        'id': pk,
        'exp': int(dt.strftime('%s'))
    }, settings.SECRET_KEY, algorithm='HS256')

    return token.decode('utf-8')
