from flask import Flask, render_template, redirect, request, session, url_for, flash
from wtforms import Form
from wtforms import (
    StringField, SubmitField, IntegerField, BooleanField, DateField,
    PasswordField, RadioField, SelectField, TextAreaField
)
from wtforms.widgets import TextArea
from wtforms.validators import (
    DataRequired, EqualTo, Length, NumberRange, ValidationError
)
from datetime import date

app = Flask(__name__)

# os.urandom(16) の結果をコピペ
app.config['SECRET_KEY'] = b'\xd8m\x1d\xd2\x0f\xc8\xf2\x1b^R\x8d1\xd6>\x0c\xb0'


def validate_name2(form, field):
    if field.data == 'fuga':
        raise ValidationError('その名前は使用できません(validate_name2)')


class UserForm(Form):
    # name = StringField('名前：', default='田中　太郎')
    name = StringField('名前：',
                       # validators=[DataRequired('名前を入力してください')],
                       validators=[validate_name2,
                                   DataRequired('名前を入力してください')],
                       default='田中　太郎')
    age = IntegerField('年齢：',
                       validators=[NumberRange(0, 100, '誤りがあります')])
    password = PasswordField(
        'パスワード：',
        validators=[Length(1, 10, '10文字以内にしてください'),
                    EqualTo('confirm_password', 'パスワードが一致しません')]
    )
    confirm_password = PasswordField('パスワード確認用：')
    birthday = DateField('誕生日：', format='%Y/%m/%d',
                         render_kw={"placeholder": "yyyy/mm/dd"})
    gender = RadioField(
        '性別：', choices=[('man', '男性'), ('woman', '女性')], default='man')
    major = SelectField('専攻：', choices=[
        ('bungaku', '文学部'), ('hougaku', '法学部'), ('rigaku', '理学部')])
    is_japanese = BooleanField('日本人？')
    message = TextAreaField('message：')
    submit = SubmitField('Submit')

    # def validate_<対象のfield名> でそのfieldに対するvalidation
    def validate_name(self, field):
        """"nameのvalidation"""
        if field.data == 'hoge':
            raise ValidationError('その名前は使用できません')

    def validate(self):
        # 既存のvalidation
        if not super(UserForm, self).validate():
            return False

        today = date.today()
        birthday = self.birthday.data
        birthday_of_this_age = birthday.replace(
            year=birthday.year + self.age.data)
        if 0 <= (today - birthday_of_this_age).days <= 365:
            return True

        flash('年齢と誕生日の関係に誤りがあります')
        return False


@app.route('/', methods=['GET', 'POST'])
def index():
    form = UserForm(request.form)
    if request.method == "POST" and form.validate():
        session['name'] = form.name.data
        session['age'] = form.age.data
        session['birthday'] = form.birthday.data
        session['gender'] = form.gender.data
        session['major'] = form.major.data
        session['nationality'] = '日本人' if \
            form.is_japanese.data else '外国人'
        session['message'] = form.message.data
        return redirect(url_for('show_user'))

    return render_template('user_regist.html', form=form)


@app.route('/show_user')
def show_user():
    return render_template('show_user.html')


if __name__ == "__main__":
    app.run(debug=True)
