import traceback
from functools import wraps

from flask import request, session, redirect, url_for
import pymysql
from DBUtils.PooledDB import PooledDB
from pymysql import escape_string

# 数据库连接池
POOL = PooledDB(
    creator=pymysql,  # 使用链接数据库的模块
    maxconnections=10,  # 连接池允许的最大连接数，0和None表示不限制连接数
    mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建


    maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
    maxshared=3,  # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
    blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
    maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
    setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
    ping=0,
    # ping MySQL服务端，检查是否服务可用。
    # 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always
    host='127.0.0.1',
    port=3306,
    user='root',
    password='111',
    database='movie',
    charset='utf8mb4'
)

# 给予conn连接
def with_con(func):
    @wraps(func)
    def inner(*args, **kwargs):
        # 给指定的函数加一个conn参数为数据库连接
        conn = POOL.connection()
        re = func(conn, *args, **kwargs)
        conn.close()
        return re
    return inner

# 验证登录
def verify(lis):
    def wrapper(f):
        @wraps(f)
        def inner():
            if isinstance(lis, str):
                # 若不符合权限，重定向到登录界面，否则正常运行
                return f() if lis in session else redirect(url_for('public.login') + '?url=' + request.url)
            else:
                for s in lis:
                    if s in session:
                        return f()
                return redirect(url_for('public.login')+'?url='+request.url)
        return inner
    return wrapper

# 处理错误
def wrap_error(f):
    @wraps(f)
    def inner():
        try:
            return f()
        except Exception as e:
            traceback.print_exc()
            return {'state': 'error', 'msg': str(e)}
    return inner

# 转义request参数
def escape_para(s):
    return escape_string(request.form[s])

# 移除session属性
def rm_ss(lis):
    for s in lis:
        try:
            session.pop(s)
        except KeyError:
            pass

# 返回正确success数据
def rt_suc(dic):
    d = {'state': 'success'}
    d.update(dic)
    return d

# 返回错误的error数据
def rt_err(dic):
    d = {'state': 'error'}
    d.update(dic)
    return d

# 通用获取列表函数
@with_con
def public_get_list(conn, who):
    p, count = int(request.form['p']), int(request.form['count'])
    lis = []
    cursor = conn.cursor()
    dic_cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('select count(*) from '+who)
    lis.append(cursor.fetchone()[0])
    # 根据参数决定查询哪个表
    dic_cursor.execute('select '+('id,nm,act,frz' if who != 'movie' else 'id,title,cov,json_length(src) as src,info,cate')+' from '+who+' limit %d,%d' % (p*count, count))
    lis.append(dic_cursor.fetchall())
    return rt_suc({'data': lis})

# 通用冻结/解冻
@with_con
def public_frz(conn, who):
    cursor = conn.cursor()
    # 根据参数决定修改哪个表
    cursor.execute('update '+who+' set frz=%d where id=%d' % (request.form['f'] == 'true', int(request.form['id'])))
    conn.commit()
    return rt_suc({})

# 通用检查冻结
@with_con
def check_frz(conn):
    if 'is_super' in session:
        return False
    try:
        what = 'user' if 'is_user' in session else 'manager'
        cursor = conn.cursor()
        # 根据参数决定修改哪个表
        cursor.execute('select frz from '+what+' where id=%d' % session['login_id'])
        return cursor.fetchone()[0] == 1
    except (KeyError, IndexError):
        return True


# 删除
@wrap_error
@with_con
def public_del(conn, who):
    cursor = conn.cursor()
    # 删除管理员或用户
    cursor.execute('delete from '+who+' where id=%d' % (int(request.form['id'])))
    conn.commit()
    rt_suc({'msg': '删除成功'})

from .super import bp as bp1
from .manager import bp as bp2
from .user import bp as bp3
from .public import bp as bp4
from .ajax import bp as bp5

# 注册蓝图，创建flask app
def create_app(app):
    for bp in [bp1, bp2, bp3, bp4, bp5]:
        app.register_blueprint(bp)