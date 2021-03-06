from datetime import datetime
from flask import (
    Blueprint, abort, request, render_template, redirect, url_for, flash,
    session, jsonify, current_app, g
)
from flask.helpers import make_response
from flask_login import login_user, login_required, logout_user, current_user
from flaskr.models import User, PasswordResetToken, UserConnect, Message
from flaskr import db
from flaskr.forms import (
    LoginForm, RegisterForm, ResetPasswordForm, ForgotPasswordForm, UserForm,
    ChangePasswordForm, UserSearchForm, ConnectForm, MessageForm
)
from flaskr.utils.message_format import (
    make_message_format, make_old_message_format
)
import logging
import time


bp = Blueprint('app', __name__, url_prefix='')


@bp.route('/')
def home():
    current_app.logger.info('Home')
    friends = requested_friends = requesting_friends = None
    connect_form = ConnectForm()
    session['url'] = 'app.home'
    if current_user.is_authenticated:
        friends = User.select_friends()
        requested_friends = User.select_requested_friends()
        requesting_friends = User.select_requesting_friends()

    return render_template(
        'home.html',
        friends=friends,
        requested_friends=requested_friends,
        requesting_friends=requesting_friends,
        connect_form=connect_form,
    )


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


@bp.route('/forgot_password', methods=['GET', 'POST'])
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
            print('パスワード再登録用URL: ', request_url)
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


@bp.route('/user_search', methods=['GET'])
@login_required
def user_search():
    form = UserSearchForm(request.form)
    connect_form = ConnectForm()
    session['url'] = 'app.user_search'
    users = None
    user_name = request.args.get('username', None, type=str)
    next_url = prev_url = None
    if user_name:
        page = request.args.get('page', 1, type=int)
        posts = User.search_by_name(user_name, page)  # paginationでhas_xxxx(bool)が返される
        next_url = url_for(
            'app.user_search', page=posts.next_num, username=user_name
        ) if posts.has_next else None
        prev_url = url_for(
            'app.user_search', page=posts.prev_num, username=user_name
        ) if posts.has_prev else None

        users = posts.items  # items: SQLの取得結果

    return render_template(
        'user_search.html', form=form, connect_form=connect_form, users=users,
        next_url=next_url, prev_url=prev_url
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


@bp.route('/message/<id>', methods=['GET', 'POST'])
@login_required
def message(id):
    if not UserConnect.is_friend(id):
        return redirect(url_for('app.home'))  # homeにリダイレクト

    form = MessageForm(request.form)
    messages = Message.get_friend_messages(current_user.get_id(), id)
    user = User.select_user_by_id(id)
    # 未読メッセージのid
    read_message_ids = \
        [message.id for message in messages
            if (not message.is_read) and (message.from_user_id == int(id))]
    # 相手の既読をまだ反映していないメッセージ（＝未チェック）
    not_checked_message_ids = \
        [message.id for message in messages
            if message.is_read
         and (not message.is_checked)
         and (message.from_user_id == int(current_user.get_id()))]
    print(f'{not_checked_message_ids=}')
    if not_checked_message_ids:
        with db.session.begin(subtransactions=True):
            Message.update_is_checked_by_ids(not_checked_message_ids)
        db.session.commit()
    # 既読ステータス更新
    if read_message_ids:
        with db.session.begin(subtransactions=True):
            Message.update_is_read_by_ids(read_message_ids)
        db.session.commit()

    if request.method == 'POST' and form.validate():
        new_message = Message(current_user.get_id(), id, form.message.data)
        with db.session.begin(subtransactions=True):
            new_message.create_message()
        db.session.commit()
        # 保存したデータを読み込むためGETでリダイレクトする
        return redirect(url_for('app.message', id=id))

    return render_template(
        'message.html', form=form, messages=messages, to_user_id=id, user=user)


@bp.route('/message_ajax', methods=['GET'])
@login_required
def message_ajax():
    user_id = request.args.get('user_id', -1, type=int)
    # 未読メッセージ取得
    user = User.select_user_by_id(user_id)
    not_read_messages = \
        Message.select_not_read_messages(user_id, current_user.get_id())
    not_read_message_ids = [message.id for message in not_read_messages]
    if not_read_message_ids:
        with db.session.begin(subtransactions=True):
            Message.update_is_read_by_ids(not_read_message_ids)
        db.session.commit()

    # 相手の既読をまだ反映していないメッセージ（＝未チェック）
    not_checked_messages = \
        Message.select_not_checked_messages(current_user.get_id(), user_id)
    not_checked_message_ids = \
        [not_checked_message.id for not_checked_message in not_checked_messages]
    if not_checked_message_ids:
        with db.session.begin(subtransactions=True):
            Message.update_is_checked_by_ids(not_checked_message_ids)
        db.session.commit()

    return jsonify(
        data=make_message_format(user, not_read_messages),
        checked_message_ids=not_checked_message_ids
    )


@bp.route('/load_old_messages', methods=['GET'])
@login_required
def load_old_messages():
    user_id = request.args.get('user_id', -1, type=int)
    offset_value = request.args.get('offset_value', -1, type=int)
    if user_id == -1 or offset_value == -1:
        return

    messages = Message.get_friend_messages(
        current_user.get_id(), user_id, offset_value * 100)
    user = User.select_user_by_id(user_id)
    return jsonify(data=make_old_message_format(user, messages))


@bp.app_errorhandler(404)
def page_not_found(e):
    return redirect(url_for('app.home'))


@bp.app_errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


@bp.before_request
def before_request():
    g.start_time = time.time()
    user_name = ''
    if current_user.is_authenticated:
        user_name = current_user.username

    current_app.logger.info(
        f'user: {user_name}, {request.remote_addr}, {request.method}, {request.url}, {request.data}'
    )


@bp.after_request
def after_request(response):
    user_name = ''
    if current_user.is_authenticated:
        user_name = current_user.username

    current_app.logger.info(
        f'user: {user_name}, {request.remote_addr}, {request.method}, {request.url}, {request.data}, {response.status}'
    )

    end_time = time.time()
    logging.getLogger('performance').info(
        f'{request.method}, {request.url}, execution time = {end_time - g.start_time}'
    )

    return response
