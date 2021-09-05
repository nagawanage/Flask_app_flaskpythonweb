# mysite2/views.py
from flask import Blueprint, render_template

# BluePrintを作成
mysite2_bp = Blueprint('mysite2', __name__, url_prefix='/site2')


# http://wwww.*/site2/hello
@mysite2_bp.route('/hello')
def hello():
    return render_template('mysite2/hello.html')
