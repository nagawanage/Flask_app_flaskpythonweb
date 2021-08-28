from flask import Flask

# appインスタンス作成。__name__には__main__が入り、app.py(=起動ファイル)が既定となる。
app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hello World</h1>'

@app.route('/hello')
def hello():
    return '<h2>Helloooo</h2>'

@app.route('/post/<int:post_id>/<post_name>')
def show_post(post_id, post_name):
    print(type(post_name))
    return f'{post_name}: {post_id}'

@app.route('/user/<string:user_name>/<int:user_no>')
def show_user(user_name, user_no):
    user_name_no = user_name + str(user_no)
    return f'<h1>{user_name_no}</h1>'

if __name__ == "__main__":
    app.run(debug = True)