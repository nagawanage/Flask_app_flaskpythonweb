from flask import(
    Blueprint, abort, request, render_template, redirect, url_for, flash
)
from flask_login import login_user, login_required, logout_user
from flaskr.models import User, PasswordResetToken
from flaskr import db
from flaskr.forms import LoginForm, RegisterForm, ResetPasswordForm, ForgotPasswordForm


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
