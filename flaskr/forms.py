from wtforms.form import Form
from wtforms.fields import (
    StringField, FileField, PasswordField, SubmitField, HiddenField
)
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError

from flaskr.models import User


# ログイン用のForm
class LoginForm(Form):
    email = StringField(
        'メール: ', validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'パスワード: ',
        validators=[
            DataRequired(),
            EqualTo('confirm_password', message='パスワードが一致しません')
        ]
    )
    confirm_password = PasswordField(
        'パスワード再入力: ', validators=[DataRequired()]
    )
    submit = SubmitField('ログイン')


# 登録用のForm
class RegisterForm(Form):
    email = StringField(
        'メール: ', validators=[
            DataRequired(),
            Email('メールアドレスが誤っています')
        ]
    )
    username = StringField('名前: ', validators=[DataRequired()])
    submit = SubmitField('登録')

    def validate_email(self, field):
        """emailの重複チェック"""
        if User.select_user_by_email(field.data):
            raise ValidationError('メールアドレスはすでに登録されています')


# パスワード設定用のフォーム
class ResetPasswordForm(Form):
    password = PasswordField(
        'パスワード',
        validators=[
            DataRequired(),
            EqualTo('confirm_password', message='パスワードが一致しません')
        ]
    )
    confirm_password = PasswordField(
        'パスワード確認: ', validators=[DataRequired()]
    )
    submit = SubmitField('パスワードを更新する')

    def validate_password(self, field):
        """passwordチェック"""
        if len(field.data) < 8:
            raise ValidationError('パスワードは8文字以上です')
