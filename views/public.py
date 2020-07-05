from flask import Blueprint, render_template, session, redirect, url_for, request

from views import with_con

# 公共页面
bp = Blueprint('public', __name__, url_prefix='/')

# 主页
@bp.route('/')
def home():
    return render_template('home.html')

# 列表
@bp.route('/list')
def list_():
    return render_template('list.html')


# 登录
@bp.route('/login')
def login():
    return render_template('login.html')

# 注册
@bp.route('/reg')
def reg():
    return render_template('reg.html')

# 根据登录状态，跳转到对应后台
@bp.route('/self')
def self():
    url = request.url
    for i in ['super', 'manager', 'user']:
        if 'is_'+i in session:
            return redirect(url_for(i+'.self'))
    return redirect(url_for('public.login')+'?url='+url)

# 影片详情
@bp.route('/movie/<int:movie_id>')
@with_con
def movie(conn, movie_id):
    logined = False
    # 检查是否登录
    for i in ['is_user', 'is_manager', 'is_super']:
        if i in session:
            logined = True
            break
    if 'is_user' in session:
        # 添加浏览历史
        u_id = session['login_id']
        cursor = conn.cursor()
        cursor.execute('select his from user where id=%d' % u_id)
        his = eval(cursor.fetchone()[0])
        if movie_id in his:
            his.remove(movie_id)
        his.insert(0, movie_id)
        cursor.execute('update user set his="%s" where id=%d' % (str(his), u_id))
        conn.commit()
    return render_template('movie.html', logined=logined, is_user='is_user' in session)
