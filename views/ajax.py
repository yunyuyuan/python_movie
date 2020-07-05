import pymysql
from flask import Blueprint, request, session
from . import wrap_error, escape_para, rt_suc, rm_ss, with_con

# ajax
bp = Blueprint('ajax', __name__, url_prefix='/ajax')

# 主页
@bp.route('/get_home', methods=['POST'])
@wrap_error
@with_con
def get_home(conn):
    cursor = conn.cursor()
    # 获取滑动信息
    cursor.execute('select swp,cate from one_row where id=1')
    re = [cursor.fetchone()]
    # 获取6部最热影片
    cursor.execute('select id,title,cov from movie order by json_length(ev) desc limit 0,6')
    re.append(list(cursor.fetchall()))
    return rt_suc({'data': re})

# 登录
@bp.route('/login', methods=['POST'])
@wrap_error
@with_con
def login(conn):
    err_re = {'state': 'error', 'msg': '账号/密码错误'}
    suc_re = rt_suc({'msg': '登录成功'})
    at, act, pwd = request.form['at'], request.form['act'], request.form['pwd']
    cursor = conn.cursor()
    if at == '超级管理员':
        # 验证超级管理员账户密码
        cursor.execute('select act,pwd from one_row where id=1')
        if (act, pwd) == cursor.fetchone():
            # 删除已登录的session信息，重设为超管
            rm_ss(['is_manager', 'is_user'])
            session['is_super'] = 't'
            return suc_re
    else:
        tp = ('user' if at == '用户' else 'manager')
        # 验证普通用户账户密码
        cursor.execute('select id from ' + tp + ' where act="%s" and pwd="%s"' % (act, pwd))
        res = cursor.fetchone()
        if res:
            # 删除已登录的session信息
            rm_ss(['is_super', 'is_' + ('user' if tp == 'manager' else 'manager'), 'login_id'])
            session['is_' + tp] = 't'
            session['login_id'] = res[0]
            return suc_re
    return err_re

# 登出
@bp.route('/logout', methods=['POST'])
@wrap_error
def logout():
    # 移除session中的登录信息
    rm_ss(['is_super', 'is_manager', 'is_user', 'login_id'])
    return rt_suc({'msg': '登出成功'})

# 注册
@bp.route('/rg', methods=['POST'])
@wrap_error
@with_con
def rg(conn):
    cursor = conn.cursor()
    # user表中插入一条数据
    cursor.execute('insert into user(nm, act, pwd, fav, his) VALUES("%s","%s","%s","[]","[]")'
                   % (escape_para('nm'), escape_para('act'), escape_para('pwd')))
    conn.commit()
    return rt_suc({'msg': '注册成功'})

# 影片详情
@bp.route('/mv_detail', methods=['POST'])
@wrap_error
@with_con
def mv_detail(conn):
    dic_cursor = conn.cursor(pymysql.cursors.DictCursor)
    # 返回影片的详情信息
    dic_cursor.execute('select title,cov,src,info,star,cate from movie where id=%d' % int(escape_para('id')))
    return rt_suc({'data': dic_cursor.fetchone()})

# 获取列表
@bp.route('/get_mv_list', methods=['POST'])
@wrap_error
@with_con
def get_mv_list(conn):
    t, s, p, count = escape_para('t'), escape_para('s'), int(escape_para('p')), int(escape_para('count'))
    cursor = conn.cursor()
    lis = []
    if t == 'cate':
        # 根据参数决定数据库查询条件语句
        sql = (' where json_contains(cate, json_quote("%s"), \'$\') ' % s)
    else:
        if s == '':
            sql = ''
        else:
            sql = (' where title like \'%%%%%s%%%%\' ' % s)
    cursor.execute(('select count(*) as c from movie ' + sql))
    lis.append(cursor.fetchone()[0])
    # 查询列表
    cursor.execute(('select id, title, cov from movie '+sql+' limit %d,%d')
                   % (p * count, count))
    lis.append(cursor.fetchall())
    return rt_suc({'data': lis})

# 获取评论
@bp.route('/get_ev', methods=['POST'])
@wrap_error
@with_con
def get_ev(conn):
    p, count, id_ = int(escape_para('p')), int(escape_para('count')), int(escape_para('id'))
    lis = []
    cursor = conn.cursor()
    cursor.execute('select json_length(ev) from movie where id=%d' % id_)
    lis.append(cursor.fetchone()[0])
    # 根据参数查询指定页码和数目的评论
    cursor.execute('select json_extract(ev, \'$[%d to %d]\') from movie where id=%d' % (p * count, count, id_))
    try:
        ev_lis = eval(cursor.fetchone()[0])
        for ev in ev_lis:
            # 根据id获取name
            cursor.execute('select nm from user where id=%d' % ev[0])
            ev[0] = cursor.fetchone()[0]
        lis.append(ev_lis)
    except TypeError:
        lis.append([])
    return rt_suc({'data': lis})
