# mysite1/views.py
from flask import Blueprint, render_template

# BluePrintを作成
# mysite1はurl_for()で使用する名前
mysite1_bp = Blueprint('mysite1', __name__, url_prefix='/site1')


# http://wwww.*/site1/hello
@mysite1_bp.route('/hello')
def hello():
    return render_template('mysite1/hello.html')
