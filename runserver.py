from datetime import timedelta
from flask import Flask
from views import create_app

app = Flask(__name__)
# 修改jinja2模板语法，防止与vue冲突
app.jinja_env.variable_start_string = '<%'
app.jinja_env.variable_end_string = '%>'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# 修改session过期时间为12小时
app.permanent_session_lifetime = timedelta(hours=12)
create_app(app)

# 运行
if __name__ == '__main__':
    app.run()
