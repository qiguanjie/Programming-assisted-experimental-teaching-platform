# encoding: utf-8

from flask import Flask, render_template, request, flash, Blueprint, Response, session, redirect, url_for,send_file
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import pymysql
from config import db
from decorators import login_limit
import time
import config

app = Flask(__name__)
app.config.from_object(config)


# 登录状态
@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        try:
            cur = db.cursor()
            sql = "select nickname,usertype from SDWZCS.userInformation where email = '%s'" % user_id
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchone()
            if result:
                return {'email':user_id,'nickname':result[0] ,'userType':result[1]}
        except Exception as e:
            print('sssssssssssssssss')
            raise e
    return {}


# 主页
@app.route('/')
def homepage():
    return render_template('HomePage.html')


@app.route('/homepage')
def homepage2():
    return render_template('HomePage.html')


# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not all([email, password]):
            flash('请填写完整信息')
        else:
            try:
                cur = db.cursor()
                sql = "select password from userInformation where email='%s'" % (email)
                db.ping(reconnect=True)
                cur.execute(sql)
                result = cur.fetchone()
                if result is None:
                    flash('无此用户')
                if check_password_hash(result[0], password):
                    session['user_id'] = email
                    session.permanent = True
                    return render_template('HomePage.html')
                else:
                    flash('密码错误')
                    return render_template('login.html')
            except Exception as e:
                flash('无此用户')
                return render_template('login.html')
                raise e
    return render_template('login.html')


# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        email = request.form.get('email')
        phone = request.form.get('phone')
        date = time.strftime("%Y-%m-%d %H:%M:%S")
        if not all([nickname, password1, password2, email, phone]):
            flash('信息未填写完整')
            render_template('register.html')
        elif password1 != password2:
            flash('两次密码输入不一致')
            return render_template('register.html')
        else:
            try:
                password = generate_password_hash(password1, method="pbkdf2:sha256", salt_length=8)
                cur = db.cursor()
                sql = "select * from SDWZCS.userInformation where email = '%s'" % email
                db.ping(reconnect=True)
                cur.execute(sql)
                result = cur.fetchone()
                if result is None:
                    cur = db.cursor()
                    sql = "insert into userInformation ( email, password, phone, nickname, usertype,creat_time_user) VALUE ('%s','%s','%s','%s','%s','%s')" % (
                    email, password, phone, nickname,0,date)
                    db.ping(reconnect=True)
                    cur.execute(sql)
                    db.commit()
                    flash('注册成功')
                    return render_template('register.html')
                else:
                    flash('该用户已存在')
                    render_template('register.html')
            except Exception as e:
                raise e
    return render_template('register.html')


# 博客界面
@app.route('/blog', methods=['GET', 'POST'])
def blog():
    return render_template('Blog.html')


# 博客文章界面
@app.route('/blog/<art>')
def blog_art(art):
    return render_template('%s.html' % art)


# 个人中心
@app.route('/personal')
@login_limit
def personal():
    cur = db.cursor()
    usernameGet = session.get('user_id')
    sql = "select email, phone, nickname, usertype, creat_time_user  from SDWZCS.userInformation where email = '%s'" % usernameGet
    db.ping(reconnect=True)
    cur.execute(sql)
    userInformation = cur.fetchone()
    email = userInformation[0]
    phone = userInformation[1]
    nickname = userInformation[2]
    return render_template('personal.html', email=email, phone=phone, nickname=nickname)


# 个人中心我的关注
@app.route('/personal/attention')
@login_limit
def personal_attention():
    return render_template('personal_attention.html')


# 个人中心 我的博客
@app.route('/personal/blog')
@login_limit
def personal_blog():
    return render_template('personal_blog.html')


# 个人中心 修改个人信息
@app.route('/personal/change', methods=['GET', 'POST'])
@login_limit
def personal_change():
    if request.method == 'GET':
        cur = db.cursor()
        username_get = session.get('user_id')
        sql = "select * from SDWZCS.userInformation where email = '%s'" % username_get
        db.ping(reconnect=True)
        cur.execute(sql)
        userinformation = cur.fetchone()
        username = userinformation[0]
        email = userinformation[2]
        phone = userinformation[3]
        nickname = userinformation[4]
        return render_template('personal_change.html', username=username, email=email, phone=phone, nickname=nickname)
    else:
        cur = db.cursor()
        username_get = session.get('user_id')
        nickname = request.form.get('nickname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        sql = "update userInformation set SDWZCS.userInformation.nickname = '%s', SDWZCS.userInformation.email = '%s', SDWZCS.userInformation.phone = '%s' where SDWZCS.userInformation.username = '%s'" % (
        nickname, email, phone, username_get)
        try:
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            return redirect(url_for('personal'))
        except Exception as e:
            raise e


# 个人中心 我的收藏
@app.route('/personal/collect')
@login_limit
def personal_collect():
    return render_template('personal_collect.html')


# 个人中心 我的粉丝
@app.route('/personal/fans')
@login_limit
def personal_fans():
    return render_template('personal_fans.html')


# 用户注销
@app.route('/logout')
def logout():
    session.clear()
    return render_template('HomePage.html')


# 用户密码重置-测试版
@app.route('/password_reset')
def password_reset():
    try:
        cur = db.cursor()
        sql = "update userInformation set SDWZCS.userInformation.password = '" + generate_password_hash('12321',
                                                                                                        method="pbkdf2:sha256",
                                                                                                        salt_length=8) + "'where username = 'demo1';"
        db.ping(reconnect=True)
        cur.execute(sql)
        db.commit()
    except Exception as e:
        raise e


# 论坛页面
@app.route('/formula',methods=['GET'])
def formula():
    if request.method == 'GET':
        page = request.values.get('page')
        if page is None:
            page = int(1)
        page = int(page)
        try:
            cur = db.cursor()
            sql = "select count(*) from SDWZCS.formula_post"
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            result = cur.fetchone()[0]
            if result is None:
                article_nums = 0
            else:
                article_nums = int(result)
            page_num = int(article_nums/5 + 0.9)
            # 防止页码溢出
            if page < 1:
                page = int(1)
            if page > page_num:
                page = int(page_num)

            if article_nums > 0:
                sql = "select formula_id,title,creat_time,nickname from SDWZCS.formula_post, SDWZCS.userInformation where formula_post.author = userInformation.email order by formula_id DESC "
                cur.execute(sql)
                db.commit()
                result = cur.fetchall()
                formula_article = []
                for iter in result:
                    sql = "select content from question_detail where formula_id = '%s' and qno = '1'" % iter[0]
                    cur.execute(sql)
                    db.commit()
                    content = cur.fetchone()[0]
                    content = (content,)
                    formula_article.append(iter[:] +content[:])
                # print(formula_article)
                cur.close()
                db.close()
                return render_template('formula.html', article_nums=article_nums, formula_article=formula_article,page=page,page_num=page_num)
            else:
                return render_template('formula.html', article_nums=article_nums,page=page,page_num=page_num)
        except Exception as e:
            raise e


# 发布问答
@app.route('/formula/post_questions', methods=['GET', 'POST'])
@login_limit
def post_questions():
    if request.method == 'GET':
        return render_template('formula_post_question.html')
    else:
        try:
            cur = db.cursor()
            email = session.get('user_id')
            title = request.form.get('question_title')
            content = request.form.get('question_content')
            date = time.strftime("%Y-%m-%d %H:%M:%S")
            sql = "select max(formula_id) from SDWZCS.formula_post"
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchone()[0]
            if result is None:
                formula_id = 1
            else:
                formula_id = int(result) + 1
            sql = "insert into SDWZCS.formula_post(SDWZCS.formula_post.formula_id, SDWZCS.formula_post.author, " \
                  "SDWZCS.formula_post.title,SDWZCS.formula_post.creat_time) values ('%s','%s','%s','%s')" % (
                formula_id,email,title,date)
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            sql = "insert into question_detail(formula_id, qno, content, datetime, author) VALUES ('%s','1','%s','%s','%s')" % (formula_id,content,date,email)
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            return redirect(url_for('formula'))
        except Exception as e:
            raise e


# 问题详情
@app.route('/formula/detail_question', methods=['GET', 'POST'])
# @login_limit
def detail_question():
    formula_id = request.values.get('formula_id')
    if formula_id is None:
        return redirect(url_for('formula'))
    if request.method == 'GET':
        page = request.values.get('page')
        if page is None:
            page = int(1)
        page = int(page)
        try:
            cur = db.cursor()
            sql = "select max(qno) from question_detail where formula_id = '%s'" % formula_id
            db.ping(reconnect=True)
            cur.execute(sql)
            question = cur.fetchone()[0]
            page_num = int(question/20 + 0.96)
            # 防止页码溢出
            if page < 1:
                page = int(1)
            if page > page_num:
                page = int(page_num)
            cur = db.cursor()
            sql = "select title from SDWZCS.formula_post where formula_id = '%s'" % formula_id
            db.ping(reconnect=True)
            cur.execute(sql)
            title = cur.fetchone()[0]
            sql = "select formula_id, qno, content, datetime, nickname from question_detail,SDWZCS.userInformation where question_detail.author = userInformation.email and formula_id = '%s'" % formula_id
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchall()
            return render_template('detail_question.html', question_inf=result,title = title,page=page,page_num = page_num,formula_id=formula_id)
        except Exception as e:
            raise e
    if request.method == 'POST':
        content = request.form.get('editorValue')
        datetime = date = time.strftime("%Y-%m-%d %H:%M:%S")
        username = session.get('user_id')
        try:
            cur = db.cursor()
            sql = "select max(qno) from question_detail where formula_id = '%s'" % formula_id
            db.ping(reconnect=True)
            cur.execute(sql)
            qno = int(cur.fetchone()[0])+1
            sql = "insert into question_detail(formula_id, qno, content, datetime, author) VALUES ('%s','%s','%s','%s','%s')" %(formula_id,qno,content,datetime,username)
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            return redirect(url_for('detail_question',formula_id = formula_id))
        except Exception as e:
            raise e


# OJ页面
@app.route('/onlinejudge')
def onlinejudge():
    return render_template('onlinejudge.html')


# OJ题目界面
@app.route('/onlinejudge/<oj>')
def onlinejudge_oj(oj):
    return render_template('%s.html' % oj)

# # demo
# @app.route('/demo')
# def demo():
#     return render_template('bootstrap.html')

# 下载测试
@app.route('/download_os')
def download_os():
    return send_file("/home/download_os/learn-cos-ubuntu64.box", as_attachment=True)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005)
