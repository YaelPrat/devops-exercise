import os
from flask import Flask, request, render_template, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import boto3

db_username = os.environ['DB_USERNAME']
db_password = os.environ['DB_PASSWORD']
db_name = os.environ['DB_NAME']
db_host = os.environ['DB_HOST']
db_port = os.environ['DB_PORT']
db_uri = f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
print(f"Connecting db @{db_uri}")
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app,db)

s3 = boto3.client('s3')

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def __init__(self, name, password):
        self.name = name
        self.password = password


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        password = request.form.get("password")
        username = request.form.get("username")
        print(username, password)
        new_user = User(
            name=username,
            password=password
        )
        db.session.add(new_user)
        db.session.commit()

        # bucket_name = 'yaelzbuk165'
        # media_url = f'https://{bucket_name}.s3.amazonaws.com/aws-image.png'
        # print(media_url)
        return render_template("home.html", username=username, media_url="/image")
    return render_template("index.html")

@app.route('/image')
def image():
    # Presuming you have AWS credentials set up in your environment or using IAM roles in EC2
    s3 = boto3.client('s3')
    bucket_name = "yaelzbuk165"
    image_file = "aws-image.png"

    # Get the image object from S3
    image_object = s3.get_object(Bucket=bucket_name, Key=image_file)

    # Serve the image as a response
    return Response(
        image_object['Body'].read(),
        mimetype='image/png',
        headers={
            "Content-Disposition": "inline; filename={}".format(image_file)
        }
    )


@app.route('/users', methods=['POST'])
def add_user():
    request_data = request.get_json()
    u_name = request_data['name']
    new_user = User(
        name=u_name)
    db.session.add(new_user)
    db.session.commit()
    return "User added successfully"


@app.route('/users')
def show_users():
    users = User.query.all()
    user_list = {}
    for user in users:
        user_list[user.id] = user.name
    return user_list


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5555)