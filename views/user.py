import pymysql, time, traceback
from flask import Blueprint, session, redirect, url_for, request, render_template

from . import verify, wrap_error, escape_para, rt_suc, with_con, rt_err, check_frz

# 用户管理
bp = Blueprint('user', __name__, url_prefix='/user')

menu_list = [
    {'name': '个人信息', 'url': 'user.self'},
    {'name': '浏览历史', 'url': 'user.his'}
]

@bp.route('/')
@verify('is_user')
def dft():
    return redirect(url_for('user.self'))

# 修改个人信息
@bp.route('/alter_info', methods=['POST'])
@verify(['is_user', 'is_manager'])
@wrap_error
@with_con
def alter_info(conn):
    id_ = session['login_id']
    pwd = escape_para('pwd')
    who = 'user' if 'is_user' in session else 'manager'
    cursor = conn.cursor()
    if pwd == '':
        # 为空则不修改密码
        cursor.execute('update '+who+' set nm="%s" where id=%d' % (escape_para('nm'), id_))
    else:
        cursor.execute('update '+who+' set nm="%s",pwd="%s" where id=%d' % (escape_para('nm'), pwd, id_))
    conn.commit()
    return rt_suc({'msg': '修改成功'})

# 获取个人信息
@bp.route('/self')
@verify('is_user')
@wrap_error
@with_con
def self(conn):
    dic_cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        dic_cursor.execute('select id,nm,act,frz from user where id=%d' % session['login_id'])
    except KeyError:
        return redirect(url_for('public.login') + '?url=' + request.url)
    return render_template('manager/self.html', menu_list=menu_list, self_info=dic_cursor.fetchone())

# 浏览历史界面
@bp.route('/his')
@verify('is_user')
def his():
    return render_template('manager/his.html', menu_list=menu_list)

# 添加评论
@bp.route('/add_ev', methods=['POST'])
@verify('is_user')
@wrap_error
@with_con
def add_ev(conn):
    try:
        user_id = session['login_id']
        if check_frz():
            return rt_err({'msg': '账号已被冻结!'})
        id_, star, txt = int(escape_para('id')), round(float(escape_para('star')), 1), escape_para('ev')
        cursor = conn.cursor()
        # 获取原有评分和评论长度
        cursor.execute('select star,json_length(ev) from movie where id=%d' % id_)
        old_star, ev_len = cursor.fetchone()
        old_star = round((old_star*ev_len+star)/(ev_len+1), 1)
        # json格式插入数据
        cursor.execute('update movie set ev=json_array_insert(ev, \'$[0]\', json_array(%d,%f,"%s","%s")),star=%f where id=%d'
                       % (user_id, star, txt, time.strftime('%Y-%m-%d', time.localtime()), old_star, id_))
        conn.commit()
        return rt_suc({'msg': '评论成功'})
    except KeyError:
        return rt_err({'msg': '验证登录信息失败'})

# 获取历史
@bp.route('/get_his', methods=['POST'])
@verify('is_user')
@wrap_error
@with_con
def get_his(conn):
    u_id = session['login_id']
    p, count = int(escape_para('p')), int(escape_para('count'))
    lis = []
    cursor = conn.cursor()
    cursor.execute('select json_length(his) from user where id=%d' % u_id)
    lis.append(cursor.fetchone()[0])
    # 根据参数获取指定页码和长度的浏览历史
    cursor.execute('select json_extract(his, \'$[%d to %d]\') from user where id=%d' % (p*count, count, u_id))
    his_lis = []
    re_lis = cursor.fetchone()[0]
    if re_lis:
        for i in eval(re_lis):
            item = [i]
            cursor.execute('select title,cov from movie where id=%d' % i)
            info = cursor.fetchone()
            # 检查影片是否已经被删除
            if info:
                item.extend(info)
            else:
                item.extend(['失效影片', 'invalid.jpg'])
            his_lis.append(item)
    lis.append(his_lis)
    return rt_suc({'data': lis})

# 删除历史
@bp.route('/del_his', methods=['POST'])
@verify('is_user')
@wrap_error
@with_con
def del_his(conn):
    u_id = session['login_id']
    id_ = int(escape_para('id'))
    cursor = conn.cursor()
    cursor.execute('select his from user where id=%d' % u_id)
    lis = eval(cursor.fetchone()[0])
    lis.remove(id_)
    cursor.execute('update user set his="%s" where id=%d' % (str(lis), u_id))
    conn.commit()
    return rt_suc({'msg': '删除成功'})
