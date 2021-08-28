from flask import Flask, render_template, redirect, url_for, abort
from datetime import datetime

app = Flask(__name__)  # flaskアプリ用のインスタンス作成（基準ファイル）


@app.template_filter('reverse_name')
def reverse(name):
    return name[-1::-1]


@app.template_filter('born_year')
def calcurate_born_year(age):
    now_timestamp = datetime.now()
    return str(now_timestamp.year - int(age)) + '年'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home/<string:user_name>/<int:age>')
def home(user_name, age):
    # login_user = user_name
    login_user = {
        'name': user_name,
        'age': age
    }
    # 指定のhtmlに引数を渡す
    return render_template('home.html', user_info=login_user)


class UserInfo:
    def __init__(self, name, age) -> None:
        self.name = name
        self.age = age


@app.route('/userlist')
def user_list():
    # users = ['Taro', 'Jiro', 'Hanako']
    users = [
        UserInfo('Taro', 21),
        UserInfo('Jiro', 22),
        UserInfo('Hanako', 23),
    ]
    is_login = True
    return render_template('userlist.html', users=users, is_login=is_login)


@app.route('/user/<string:user_name>/<int:age>')
def user(user_name, age):
    if user_name in ['Taro', 'Jiro', 'Saburo']:
        return redirect(url_for('home', user_name=user_name, age=age))
    else:
        abort(500, 'そのユーザーはリダイレクトできません。')


@app.errorhandler(404)
def page_not_found(erro):
    return render_template('not_found.html'), 404


@app.errorhandler(500)
def system_error(error):
    error_description = error.description
    return render_template(
        'system_error.html', error_description=error_description), 500


if __name__ == "__main__":
    app.run(debug=True)
