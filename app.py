from flask import Flask, render_template
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


if __name__ == "__main__":
    app.run(debug=True)
