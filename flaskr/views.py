from datetime import datetime
from flask import (
    Blueprint, abort, request, render_template, redirect, url_for, flash,
    session
)
from flask_login import login_user, login_required, logout_user, current_user
from flaskr.models import User, PasswordResetToken, UserConnect
from flaskr import db
from flaskr.forms import (
    LoginForm, RegisterForm, ResetPasswordForm, ForgotPasswordForm, UserForm,
    ChangePasswordForm, UserSearchForm, ConnectForm
)


bp = Blueprint('app', __name__, url_prefix='')


@bp.route('/')
def home():
    return render_template('home.html')


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('app.home'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.select_user_by_email(form.email.data)
        if user and user.is_active and user.validate_password(form.password.data):
            login_user(user, remember=True)  # ログイン済みユーザーとして記録 & cookieを使い remember me
            next = request.args.get('next')
            if not next:
                next = url_for('app.home')
                return redirect(next)
        elif not user:
            flash('存在しないユーザです')
        elif not user.is_active:
            flash('無効なユーザです。パスワードを再設定してください')
        elif not user.validate_password(form.password.data):
            flash('メールアドレスとパスワードの組み合わせが誤っています')

    return render_template('login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        with db.session.begin(subtransactions=True):
            user.create_new_user()
        db.session.commit()

        token = ''
        with db.session.begin(subtransactions=True):
            token = PasswordResetToken.publish_token(user)
        db.session.commit()
        # 実際はメールで通知するべき
        print(f'パスワード設定用URL: http://localhost:5000/reset_password/{token}')
        flash('パスワード設定用URLを送信しました。ご確認ください。')
        return redirect(url_for('app.login'))
    return render_template('register.html', form=form)


@bp.route('/reset_password/<uuid:token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm(request.form)
    reset_user_id = PasswordResetToken.get_user_id_by_token(token)
    if not reset_user_id:
        abort(500)
    if request.method == 'POST' and form.validate():
        password = form.password.data
        user = User.select_user_by_id(reset_user_id)
        with db.session.begin(subtransactions=True):
            user.save_new_password(password)
            PasswordResetToken.delete_token(token)
        db.session.commit()
        flash('パスワードを更新しました。')
        return redirect(url_for('app.login'))
    return render_template('reset_password.html', form=form)


@bp.route('forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        user = User.select_user_by_email(email)
        if user:
            with db.session.begin(subtransactions=True):
                token = PasswordResetToken.publish_token(user)
            db.session.commit()
            # 実際はメールで通知するべき
            request_url = f'http://localhost:5000/reset_password/{token}'
            print(f'パスワード再登録用URL: ', request_url)
            flash('パスワード設定用URLを送信しました。ご確認ください。')
        else:
            flash('存在しないユーザです')
    return render_template('forgot_password.html', form=form)


# ユーザ情報更新
@bp.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        user = User.select_user_by_id(user_id)
        with db.session.begin(subtransactions=True):
            user.username = form.username.data
            user.email = form.email.data
            file = request.files[form.picture_path.name].read()
            if file:
                file_name = user_id + '_' + \
                    str(int(datetime.now().timestamp())) + '.jpg'
                picture_path = 'flaskr/static/user_image/' + file_name
                open(picture_path, 'wb').write(file)
                user.picture_path = 'user_image/' + file_name
        db.session.commit()
        flash('ユーザ情報を更新しました')
    return render_template('user.html', form=form)


@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.select_user_by_id(current_user.get_id())
        password = form.password.data
        with db.session.begin(subtransactions=True):
            user.save_new_password(password)
        db.session.commit()
        flash('パスワードを更新しました')
        return redirect(url_for('app.user'))
    return render_template('change_password.html', form=form)


@bp.route('/user_search', methods=['GET', 'POST'])
@login_required
def user_search():
    form = UserSearchForm(request.form)
    connect_form = ConnectForm()
    session['url'] = 'app.user_search'
    users = None
    if request.method == 'POST' and form.validate():
        # 検索結果のユーザを取得
        username = form.username.data
        # UserテーブルとUserConnectテーブルを紐付けて、UserConnect.statusを取得
        users = User.search_by_name(username)

    return render_template(
        'user_search.html', form=form, connect_form=connect_form, users=users
    )


@bp.route('/connect_user', methods=['POST'])
@login_required
def connect_user():
    form = ConnectForm(request.form)
    if request.method == 'POST' and form.validate():
        if form.connect_condition.data == 'connect':
            new_connect = UserConnect(current_user.get_id(), form.to_user_id.data)
            with db.session.begin(subtransactions=True):
                new_connect.create_new_connect()
            db.session.commit()
        elif form.connect_condition.data == 'accept':
            # 相手から自分へのUserConnectを取得
            connect = UserConnect.select_by_from_user_id(form.to_user_id.data)
            if connect:
                with db.session.begin(subtransactions=True):
                    connect.update_status()  # status: 1 -> 2
                db.session.commit()

    next_url = session.pop('url', 'app:home')  # sessionから情報取得
    return redirect(url_for(next_url))


@bp.app_errorhandler(404)
def page_not_found(e):
    return redirect(url_for('app.home'))


@bp.app_errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
