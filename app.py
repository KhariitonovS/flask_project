import prometheus_client
from flask import Response, Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import time
import random
from dotenv import load_dotenv
import prometheus_client
from prometheus_client.core import CollectorRegistry
from prometheus_client import Summary, Counter, Histogram, Gauge
from prometheus_flask_exporter import PrometheusMetrics

# from config.development import DevelopmentConfig
# from config.production import ProductionConfig
# from config.testing import TestingConfig

load_dotenv()
DB_NAME = os.getenv('DB_NAME')
APP_HOST = os.getenv('APP_HOST')
APP_PORT = os.getenv('APP_PORT')
IS_DEBUG = os.getenv('IS_DEBUG')

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.debug = True
users_seen = {}

graphs = {}
graphs['c'] = Counter('python_request_operations_total', 'The total number of processed requests')
graphs['h'] = Histogram('python_request_duration_seconds', 'Histogram for the duration in seconds', buckets=(1, 2, 5, 6, 10))

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.3')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, DB_NAME)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config.from_object('config.base.Config')

# app.config['ENV'] = 'development'
#
# if app.config['ENV'] == 'development':
#     app.config.from_object(DevelopmentConfig())
# elif app.config['ENV'] == 'testing':
#     app.config.from_object(ProductionConfig())
# elif app.config['ENV'] == 'production':
#     app.config.from_object(TestingConfig())

db = SQLAlchemy(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()
    db.session.commit()


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)


@app.route('/')
def index():
    # show all todos
    todo_list = Todo.query.all()

    start = time.time()
    graphs['c'].inc()

    time.sleep(0.100)
    end = time.time()
    graphs['h'].observe(end - start)
    return render_template('base.html', todo_list=todo_list)


@app.route("/add", methods=["POST"])
def add():
    # add new item
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False)

    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/update/<int:todo_id>")
def update(todo_id):
    # update
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete

    db.session.commit()
    return redirect(url_for("index"))


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    # delete
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)

    db.session.commit()
    return redirect(url_for("index"))


@app.route("/metrics")
def requests_count():
    res = []
    for k, v in graphs.items():
        res.append(prometheus_client.generate_latest(v))
    return Response(res, mimetype="text/plain")


if __name__ == '__main__':
    app.run(host=APP_HOST, port=APP_PORT, debug=IS_DEBUG)
