
from flask import Flask, render_template, url_for, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import PasswordField, EmailField, BooleanField
from wtforms.validators import InputRequired, Length
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/changapp.db'
app.config['SECRET_KEY'] = 'mysupersecretultrasecretkey1234'
db  = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String(200))
    user_last_name = db.Column(db.String(200))
    user_desc = db.Column(db.String(200))
    user_email = db.Column(db.String(200))
    user_pass = db.Column(db.String(200))
    user_done = db.Column(db.Boolean(200))


class Job(db.Model):
    job_id = db.Column(db.Integer,primary_key=True)
    job_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    job_name = db.Column(db.String(200))
    job_desc = db.Column(db.String(200))
    job_price = db.Column(db.String(200))
    job_done = db.Column(db.Boolean(200))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    email = EmailField('email', validators=[InputRequired(), Length(min=4, max=25)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


@app.route("/", methods=['POST','GET'])
def index():
    return render_template("index.html", user=current_user)


@app.route("/login", methods=['POST','GET'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.email.data).first()
        if user:
            print()
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))

        return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)


@app.route('/register', methods=['POST','GET'])
def register(): 
    if request.method == 'POST':
        user = User(
            user_name=request.form['name'],
            user_last_name=request.form['last_name'],
            user_desc=request.form['desc'],
            user_email=request.form['email'],
            user_pass=request.form['password'],
            user_done = False
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('register.html')


@app.route('/create-job', methods=['POST','GET'])
@login_required
def create_job():
    print(request.method)
    if request.method == 'POST':
        job = Job(
            job_user_id=current_user.id,
            job_name=request.form['job_name'],
            job_desc=request.form['job_desc'],
            job_price=request.form['job_price'],
            job_done = False
        )
        print('Hola entre aca')
        print(job)
        db.session.add(job)
        db.session.commit()
        return redirect(url_for('find_job'))
    else:
        print('entre en GET')
        return render_template('create_job.html')


@app.route('/find-job', methods=['GET'])
@login_required
def find_job():
    jobs= Job.query.all()
    print("asdasdasd")
    print(current_user.id)
    return render_template('find_job.html', jobs=jobs)


@app.route('/user', methods=['GET'])
@login_required
def profile():
    jobs = Job.query.filter_by(job_user_id=current_user.id)
    return render_template('user.html', jobs=jobs)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)