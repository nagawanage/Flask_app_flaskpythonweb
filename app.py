from typing import ClassVar
from flask import Flask, render_template, redirect
from flask.globals import request
from wtforms import StringField, SubmitField, IntegerField
from wtforms.form import Form
import os


app = Flask(__name__)

# os.urandom(16) の結果をコピペ
app.config['SECRRET_KEY'] = b'\xd8m\x1d\xd2\x0f\xc8\xf2\x1b^R\x8d1\xd6>\x0c\xb0'


class UserForm(Form):
    name = StringField('名前')
    age = IntegerField('年齢')
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    name = age = ''
    form = UserForm(request.form)

    if request.method == 'POST':
        # ユーザーの入力内容
        # 型チェック
        if form.validate():
            # 取得
            name = form.name.data
            age = form.age.data
            form = UserForm()
        else:
            print('入力内容に誤りがあります')

    return render_template('index.html', form=form, name=name, age=age)


if __name__ == "__main__":
    app.run(debug=True)
