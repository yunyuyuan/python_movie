from re import sub, match

import pymysql
from pymysql import escape_string

from os import mkdir, remove
from shutil import rmtree
from os.path import exists

from flask import Blueprint, session, redirect, url_for, request, render_template
from views import wrap_error, public_get_list, public_frz, public_del, rt_suc, escape_para, verify, with_con, rt_err, \
    check_frz

# 普通管理员
bp = Blueprint('manager', __name__, url_prefix='/manager')

# 项目绝对路径
from os.path import abspath
abs_path = abspath(__file__).replace('\\', '/').replace('/views/manager.py', '')

# 管理界面的菜单(super和user同)
menu_list = [
    {'name': '个人信息', 'url': 'manager.self'},
    {'name': '用户管理', 'url': 'manager.user'},
    {'name': '影片管理', 'url': 'manager.movie'}
]

# 默认跳转到主页
@bp.route('/')
@verify('is_manager')
def dft():
    return redirect(url_for('manager.self'))

# 管理员主页
@bp.route('/self')
@verify('is_manager')
@with_con
def self(conn):
    dic_cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        dic_cursor.execute('select id,nm,act,frz from manager where id=%d' % session['login_id'])
    except KeyError:
        return redirect(url_for('public.login') + '?url=' + request.url)
    return render_template('manager/self.html', menu_list=menu_list, self_info=dic_cursor.fetchone())

# 管理用户
@bp.route('/user')
@verify('is_manager')
def user():
    return render_template('manager/user.html', menu_list=menu_list)

# 管理影片
@bp.route('/movie')
@verify('is_manager')
def movie():
    return render_template('manager/movie.html', menu_list=menu_list)

# 获取用户列表
@bp.route('/get_list', methods=['POST'])
@verify(['is_manager', 'is_super'])
@wrap_error
def get_list():
    if check_frz():
        return rt_err({'msg': '账号已被冻结!'})
    return public_get_list("user")

# 冻结/解冻用户
@bp.route('/frz', methods=['POST'])
@verify(['is_manager', 'is_super'])
@wrap_error
def frz():
    if check_frz():
        return rt_err({'msg': '账号已被冻结!'})
    return public_frz("user")

# 删除用户
@bp.route('/del', methods=['POST'])
@verify(['is_manager', 'is_super'])
@wrap_error
def del_():
    if check_frz():
        return rt_err({'msg': '账号已被冻结!'})
    return public_del("user")


# 获取影片列表
@bp.route('/get_mv_list', methods=['POST'])
@verify(['is_manager', 'is_super'])
@wrap_error
def get_mv_list():
    if check_frz():
        return rt_err({'msg': '账号已被冻结!'})
    return public_get_list("movie")

# 添加/修改影片
@bp.route('/add_alter', methods=['POST'])
@verify(['is_manager', 'is_super'])
@wrap_error
@with_con
def add_alter(conn):
    if check_frz():
        return rt_err({'msg': '账号已被冻结!'})
    is_alter = str(request.form['is_alter']) == 'true'

    # 新建数据
    cursor = conn.cursor()
    if not is_alter:
        # 插入影片数据
        cursor.execute('insert into movie(title,ev) values("%s", "[]")'
                       % (escape_para('title')))
        conn.commit()
        # 获取刚插入的数据自增id
        cursor.execute('select last_insert_id() from movie')
        m_id = cursor.fetchone()[0]
    else:
        m_id = int(request.form['id'])

    cov_name = ''
    mv_list = []
    cate_lis = eval(request.form['cate'])

    if is_alter:
        # 删除原有封面和mp4
        if request.form['alter_cov'] == '1':
            cursor.execute('select cov from movie where id=%d' % m_id)
            remove(abs_path+'/static/img/cov/'+cursor.fetchone()[0])
        if request.form['alter_mv'] == '1':
            rmtree(abs_path+'/static/videos/'+str(m_id))

    # 保存文件
    for f in request.files:
        file = request.files[f]
        if f == 'cov':
            cov_name = str(m_id) + '.' + sub(r'[^.]*/(.*)$', '\\1', file.content_type)
            file.save(abs_path+'/static/img/cov/'+cov_name)
        elif match(r'mv\d+', f):
            # 按顺序1-n保存影片
            dir_ = abs_path+'/static/videos/'+str(m_id)
            if not exists(dir_):
                mkdir(dir_)
            mv_name = f.replace('mv', '')+'.'+sub(r'[^.]*/(.*)$', '\\1', file.content_type)
            file.save(dir_+'/'+mv_name)
            mv_list.append(mv_name)

    # 更新数据库信息
    if not is_alter:
        cursor.execute('update movie set cov="%s",src="%s",info="%s",cate="%s" where id=%d' % (cov_name, escape_string(str(mv_list).replace('\'', '"')), escape_para('info'), escape_para('cate'), m_id))
        conn.commit()
    else:
        # 删除修改后不存在的分类
        cursor.execute('select cate from movie where id=%d' % m_id)
        o_cate = eval(cursor.fetchone()[0])
        for i in cate_lis:
            if i in o_cate:
                o_cate.remove(i)
        update_s = ''
        if request.form['alter_cov'] == '1':
            update_s += ' cov="%s",' % cov_name
        if request.form['alter_mv'] == '1':
            update_s += ' src="%s",' % escape_string(str(mv_list).replace('\'', '"'))
        cursor.execute('update movie set '+update_s+'title="%s",info="%s",cate="%s" where id=%d' % (escape_para('title'), escape_para('info'), escape_para('cate'), m_id))
        conn.commit()
        del_cate(o_cate)

    # 更新分类
    cursor.execute('select cate from one_row where id=1')
    old_cate = eval(cursor.fetchone()[0])
    has_other = False
    for i in cate_lis:
        if i not in old_cate:
            old_cate.append(i)
            has_other = True
    if has_other:
        cursor.execute('update one_row set cate="%s" where id=1' % escape_string(str(list(old_cate)).replace("'", '"')))
        conn.commit()
    return rt_suc({'msg': ('修改' if is_alter else '添加')+'成功'})

# 删除影片
@bp.route('/del_mv', methods=['POST'])
@verify(['is_manager', 'is_super'])
@wrap_error
@with_con
def del_mv(conn):
    if check_frz():
        return rt_err({'msg': '账号已被冻结!'})
    m_id = int(request.form['id'])
    cursor = conn.cursor()
    cursor.execute('select cate from movie where id=%d')
    o_cate = eval(cursor.fetchone()[0])
    cursor.execute('delete from movie where id=%d' % m_id)
    # 删除封面和影片mp4
    rmtree(abs_path+'/static/videos/'+str(m_id))
    remove(abs_path+'/static/img/cov/'+request.form['cov'])
    conn.commit()
    del_cate(o_cate)
    return rt_suc({'msg': '删除成功'})


@with_con
def del_cate(conn, cate_lis):
    # 删除分类
    # 检查数据库，不删除存在的分类
    cursor = conn.cursor()
    cursor.execute('select cate from one_row where id=1')
    old_cate = eval(cursor.fetchone()[0])
    for c in cate_lis:
        cursor.execute('select count(*) from movie where json_contains(cate, json_quote("%s"), \'$\')' % c)
        if not cursor.fetchone():
            old_cate.remove(c)
    cursor.execute('update one_row set cate="%s" where id=1' % escape_string(str(old_cate).replace("'", '"')))
    conn.commit()
