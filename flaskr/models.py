# models.py
from flaskr import db, login_manager
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user

from datetime import datetime, timedelta
from uuid import uuid4

# テーブルjoin用
from sqlalchemy.orm import aliased
from sqlalchemy import and_, or_


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(
        db.String(128),
        default=generate_password_hash('snsflaskapp'))
    picture_path = db.Column(db.Text)
    is_active = db.Column(db.Boolean, unique=False, default=False)  # 有効フラグ
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    @classmethod
    def select_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def select_user_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def search_by_name(cls, username):
        user_connect1 = aliased(UserConnect)  # from_user_id=検索相手、to_user_id=ログインユーザでUserConnectに紐付ける
        user_connect2 = aliased(UserConnect)  # to_user_id=検索相手、from_user_id=ログインユーザでUserConnectに紐付ける
        # クエリ長いのはsql接続を1回だけにしたいため
        return cls.query.filter(
            cls.username.like(f'%{username}%'),
            cls.id != int(current_user.get_id()),  # 自分以外
            cls.is_active == True
        ).outerjoin(
            user_connect1,
            and_(
                user_connect1.from_user_id == cls.id,
                user_connect1.to_user_id == current_user.get_id()
            )
        ).outerjoin(
            user_connect2,
            and_(
                user_connect2.from_user_id == current_user.get_id(),
                user_connect2.to_user_id == cls.id
            )
        ).with_entities(
            # 取得項目を限定
            cls.id, cls.username, cls.picture_path,
            user_connect1.status.label('joined_status_to_from'),  # AS
            user_connect2.status.label('joined_status_from_to'),  # AS
        ).all()

    def validate_password(self, password):
        return check_password_hash(self.password, password)

    def create_new_user(self):
        db.session.add(self)

    def save_new_password(self, new_password):
        self.password = generate_password_hash(new_password)
        self.is_active = True


# パスワードリセット時に利用する
class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(
        db.String(64),
        unique=True,
        index=True,
        server_default=str(uuid4)
    )
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expire_at = db.Column(db.DateTime, default=datetime.now)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, token, user_id, expire_at):
        self.token = token
        self.user_id = user_id
        self.expire_at = expire_at

    @classmethod
    def publish_token(cls, user):
        # password設定用のURL生成
        token = str(uuid4())
        new_token = cls(
            token,
            user.id,
            datetime.now() + timedelta(days=1)
        )
        db.session.add(new_token)
        return token

    @classmethod
    def get_user_id_by_token(cls, token):
        now = datetime.now()
        record = cls.query.filter_by(token=str(token)) \
            .filter(cls.expire_at > now).first()
        if record:
            return record.user_id
        else:
            return None

    @classmethod
    def delete_token(cls, token):
        cls.query.filter_by(token=str(token)).delete()


class UserConnect(db.Model):
    __tablename__ = 'user_connects'

    id = db.Column(db.Integer, primary_key=True)
    # 誰からの友達申請か
    from_user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), index=True
    )
    # 誰への友達申請か
    to_user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), index=True
    )
    # 1:申請中, 2:承認済み
    status = db.Column(db.Integer, unique=False, default=1)

    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, from_user_id, to_user_id):
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id

    def create_new_connect(self):
        db.session.add(self)

    @classmethod
    def select_by_from_user_id(cls, from_user_id):
        return cls.query.filter_by(
            from_user_id=from_user_id,
            to_user_id=current_user.get_id()
        ).first()

    def update_status(self):
        self.status = 2
        self.update_at = datetime.now()
