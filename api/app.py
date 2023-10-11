from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "<img src='https://t4.ftcdn.net/jpg/01/36/70/67/360_F_136706734_KWhNBhLvY5XTlZVocpxFQK1FfKNOYbMj.jpg' width='250px'>"

if __name__ == "__main__":
    app.run(debug=True)