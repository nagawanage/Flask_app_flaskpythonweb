from flask import Flask, render_template, redirect, request, session, url_for
from wtforms import Form
from wtforms import (
    StringField, SubmitField, IntegerField, BooleanField, DateField,
    PasswordField, RadioField, SelectField, TextAreaField
)
from wtforms.widgets import TextArea


app = Flask(__name__)

# os.urandom(16) の結果をコピペ
app.config['SECRET_KEY'] = b'\xd8m\x1d\xd2\x0f\xc8\xf2\x1b^R\x8d1\xd6>\x0c\xb0'


class UserForm(Form):
    # name = StringField('名前：', default='田中　太郎')
    name = StringField('名前：', widget=TextArea(), default='田中　太郎')
    age = IntegerField('年齢：')
    password = PasswordField('パスワード：')
    birthday = DateField('誕生日：', format='%Y/%m/%d',
                         render_kw={"placeholder": "yyyy/mm/dd"})
    gender = RadioField(
        '性別：', choices=[('man', '男性'), ('woman', '女性')], default='man')
    major = SelectField('専攻：', choices=[
        ('bungaku', '文学部'), ('hougaku', '法学部'), ('rigaku', '理学部')])

    is_japanese = BooleanField('日本人？')
    message = TextAreaField('message：')
    submit = SubmitField('Submit')


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
