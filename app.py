from flask import Flask, render_template, redirect, url_for, abort


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home/<string:user_name>/<int:age>')
def home(user_name, age):
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
