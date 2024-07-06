from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888,debug=True)

# from flask import Flask
# app = Flask(__name__)
# @app.route('/')
# def home():
#     return "Hello, World!"
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', use_reloader=False)
