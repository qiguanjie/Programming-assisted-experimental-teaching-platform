from functools import wraps
from flask import session, url_for, redirect


# 登录限制
# def login_limit(func):
    # @wraps(func)
    # def wrapper(*args, **kwargs):
    #     if session.get('user_id'):
    #         return func(*args, **kwargs)
    #     else:
    #         return redirect(url_for('login'))
    #     return func(*args, **kwargs)
    # return wrapper

