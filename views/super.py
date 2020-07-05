import pymysql
from flask import Blueprint, render_template, redirect, request, url_for

from . import wrap_error, rt_suc, public_del, public_frz, public_get_list, verify, with_con, escape_para

from os import remove

# 超级管理员
from .manager import abs_path

bp = Blueprint('super', __name__, url_prefix='/super')

menu_list = [
    {'name': '配置', 'url': 'super.conf'},
    {'name': '管理员', 'url': 'super.manager'},
    {'name': '用户管理', 'url': 'super.user'},
    {'name': '影片管理', 'url': 'super.movie'}
]

@bp.route('/')
def dft():
    return redirect(url_for('super.manager'))

@bp.route('/self')
def self():
    return redirect(url_for('super.manager'))

# 修改配置页
@bp.route('/conf')
@verify('is_super')
def conf():
    return render_template('manager/conf.html', menu_list=menu_list)

# 管理员页
@bp.route('/manager')
@verify('is_super')
def manager():
    return render_template('manager/manager.html', menu_list=menu_list)

# 用户页
@bp.route('/user')
@verify('is_super')
def user():
    return render_template('manager/user.html', menu_list=menu_list)

# 影片页
@bp.route('/movie')
@verify('is_super')
def movie():
    return render_template('manager/movie.html', menu_list=menu_list)

# 获取配置信息
@bp.route('/get_conf', methods=['POST'])
@verify('is_super')
@wrap_error
@with_con
def get_conf(conn):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('select swp,act from one_row where id=1')
    return rt_suc({'data': cursor.fetchone()})

# 修改配置信息
@bp.route('/submit_conf', methods=['POST'])
@verify('is_super')
@wrap_error
@with_con
def submit_conf(conn):
    cursor = conn.cursor()
    cursor.execute(('update one_row set act="%s",swp="%s"'+((',pwd="%s"' % escape_para('pwd')) if 'pwd' in request.form else '')+' where id=1') %
                   (escape_para('act'), escape_para('swp')))
    conn.commit()
    # 修改主页滑动内容
    for i in eval(request.form['del_img']):
        remove(abs_path+'/static/img/swp/'+i)
    for s in request.files:
        f = request.files[s]
        f.save(abs_path+'/static/img/swp/'+s)
    return rt_suc({'msg': '修改成功'})

# 添加管理员
@bp.route('/add', methods=['POST'])
@verify('is_super')
@wrap_error
@with_con
def add_manager(conn):
    cursor = conn.cursor()
    cursor.execute('insert into manager(nm,act,pwd,his) values("管理员","%s","%s","[]")' % (request.form['act'], request.form['pwd']))
    conn.commit()
    return rt_suc({'msg': '添加成功'})

# 获取管理员列表
@bp.route('/get_list', methods=['POST'])
@verify('is_super')
@wrap_error
def get_list():
    return public_get_list("manager")

# 冻结/解冻
@bp.route('/frz', methods=['POST'])
@verify('is_super')
@wrap_error
def frz():
    return public_frz("manager")

# 删除管理员
@bp.route('/del', methods=['POST'])
@verify('is_super')
@wrap_error
def del_():
    return public_del("manager")
