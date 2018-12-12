from flask import Flask, url_for, render_template, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import UserMixin ,login_required, current_user, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm, BookingForm

app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'r25hetAJAOWEHH2829292DJDOFUSODFUOSDJFweewefe515615'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# login_manager.login_message = 'Por favor entre na sua conta.' # overiden by unauthorized_handler


class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(30))
  surname = db.Column(db.String(30))
  email = db.Column(db.String(50), unique=True)
  password = db.Column(db.String(85))
  role = db.Column(db.String(20))
  premium = db.Column(db.Boolean())


class Booking(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer)
  service = db.Column(db.String(50))
  amount_paid = db.Column(db.Float())
  completed = db.Column(db.Boolean())



# USER LOADER
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
  flash('Por favor entre na sua conta para aceder ao seu perfile.')
  return redirect(url_for('login'))


# ROUTES
# Index route - main page
@app.route('/')
def index():
    return render_template('public/index.html')


# Registration route
@app.route('/registo', methods=['GET','POST'])
def registo():
  form = RegisterForm()
  if form.validate_on_submit():
    hashed_password = generate_password_hash(form.password.data, method='sha256')
    if form.company.data:
        role = 'Empresa'
    else:
        role = 'Cliente'
    new_user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            password=hashed_password,
            role = role,
            premium=False)
    db.session.add(new_user)
    db.session.commit()
    flash('A sua conta foi criada com sucesso!')
    return redirect(url_for('login'))

  return render_template('public/registo.html', form=form)











# Login route
@app.route('/login', methods=['GET','POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user:
      if check_password_hash(user.password, form.password.data):
        login_user(user)
        return redirect(url_for('profile'))
      flash('A palavra passe nao esta correcta.')
    else:
      flash('Esse email nao se encontra registado.')
    return redirect(url_for('login'))

  return render_template('public/login.html', form=form)














# Profile route
@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
  existing_bookings_count = len(Booking.query.filter_by(user_id=current_user.id, completed=False).all())

  return render_template('protected/profile.html', existing_bookings_count=existing_bookings_count)























# Admin route for Admin users
@app.route('/admin', methods=['GET','POST'])
@login_required
def admin():
    return render_template('protected/admin.html')





# New booking route
@app.route('/book', methods=['GET','POST'])
@login_required
def book():
  form = BookingForm()
  if form.validate_on_submit():
    new_booking = Booking(
                  user_id = current_user.id,
                  service=form.service.data,
                  amount_paid=19.99,
                  completed=False)
    db.session.add(new_booking)
    db.session.commit()
    flash('A sua limpeza foi agendada com sucesso!')
    return redirect(url_for('profile'))

  existing_bookings = Booking.query.filter_by(user_id=current_user.id).all()

  return render_template('protected/book.html', form=form, existing_bookings=existing_bookings)





# Dashboard route
@app.route('/profile/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
  return render_template('protected/dashboard.html')



# Messages route
@app.route('/profile/messages', methods=['GET','POST'])
@login_required
def messages():
  return render_template('protected/messages.html')


@app.route('/profile/settings', methods=['GET','POST'])
@login_required
def profile_settings():
  return render_template('protected/profile_settings.html')


# Logout route
@app.route('/logout')
@login_required
def logout():
  logout_user();
  return redirect(url_for('index'))



# 404 route
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


# Start app
if __name__ == '__main__':
    app.run(debug=True)
