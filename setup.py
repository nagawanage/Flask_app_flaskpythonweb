from flaskr import create_app
from flask import render_template


# __init__.pyのcreate_app()をセット
app = create_app()


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
