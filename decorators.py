from functools import wraps
from flask import session, url_for, redirect
from config import db

#登录限制
def login_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('user_id'):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

# 限制管理员页面
def admin_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('user_id'):
            try:
                cur = db.cursor()
                sql = "select usertype from SDWZCS.userInformation where email = '%s'" % session.get('user_id')
                db.ping(reconnect=True)
                cur.execute(sql)
                result = cur.fetchone()
                if result[0] == 233:
                    return func(*args, **kwargs)
                cur.close()
            except Exception as e:
                raise e
        else:
            return redirect(url_for('homepage'))
        return func(*args, **kwargs)
    return wrapper

