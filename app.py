from flask import Flask, url_for, render_template, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import UserMixin ,login_required, current_user, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm, BookingForm, BookingNotesForm, BookingUpdateForm, ServiceForm
import datetime

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

  def get_user_bookings(self):
    return Booking.query.filter_by(user_id=self.id).all()

  def get_total_bookings(self):
    return len(Booking.query.filter_by(user_id=self.id).all())

  def get_total_paid(self):
    total = 0
    for i in self.get_user_bookings():
      total += i.amount_paid
    return total

  def get_total_vat(self):
    total = self.get_total_paid()
    vat = total - ( total / 1.2 )
    return round(vat, 2)














class Booking(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer)
  service_id = db.Column(db.Integer)
  amount_paid = db.Column(db.Float())
  completed = db.Column(db.Boolean(), default=False)
  cleaner = db.Column(db.String(10), nullable=True, default=None)
  supervisor = db.Column(db.String(10), nullable=True, default=None)

  def get_booking_user(self):
    return User.query.filter_by(id=self.user_id).first()

  def get_booking_notes(self):
    return BookingNote.query.filter_by(booking_id=self.id).all()

  def get_booking_service(self):
    return Service.query.filter_by(id=self.service_id).first()




class BookingNote(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  booking_id = db.Column(db.Integer)
  user_id = db.Column(db.Integer)
  text = db.Column(db.Text())
  created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

  def get_note_user(self):
    return User.query.filter_by(id=self.user_id).first()







class Service(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(20))
  description = db.Column(db.Text())
  price = db.Column(db.Float())
  active = db.Column(db.Boolean(), default=True)






















# USER LOADER
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
  flash('Por favor entre na sua conta para aceder ao seu perfile.', 'info')
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
    flash('A sua conta foi criada com sucesso!', 'success')
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
      flash('A palavra passe nao esta correcta.', 'info')
    else:
      flash('Esse email nao se encontra registado.', 'info')
    return redirect(url_for('login'))

  return render_template('public/login.html', form=form)














# Profile route
@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
  existing_bookings_count = len(Booking.query.filter_by(user_id=current_user.id, completed=False).all())

  return render_template('protected/profile.html', existing_bookings_count=existing_bookings_count)























# Admin route for Admin users
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
  if current_user.role == 'Admin':
    form = ServiceForm()
    if form.validate_on_submit():
      new_service = Service(name=form.name.data,
                            description=form.description.data,
                            price=form.price.data)
      db.session.add(new_service)
      db.session.commit()
      flash('Servico adicionado com sucesso', 'success')
      return redirect(url_for('admin'))

    users_array = User.query.all()
    bookings_array = Booking.query.all()
    services_array = Service.query.all()
    return render_template('protected/admin.html',
                            users_array=users_array,
                            bookings_array=bookings_array,
                            services_array=services_array,
                            form=form)

  flash('Area restrista para administradores.', 'danger')
  return redirect(url_for('profile'))











# Admin route for Admins to modify users
@app.route('/admin/user/<user_id>', methods=['GET', 'POST'])
@login_required
def admin_user(user_id):
  if current_user.role == 'Admin':
    user = User.query.filter_by(id=user_id).first()
    if user:
      return render_template('protected/admin_user.html', user=user)
    else:
      flash('Esse user nao existe.', 'danger')
      return redirect(url_for('admin'))
  flash('Area restrista para administradores.', 'danger')
  return redirect(url_for('profile'))










# Admin route for Admins to modify bookings
@app.route('/admin/booking/<booking_id>', methods=['GET', 'POST'])
@login_required
def admin_booking(booking_id):
  if current_user.role == 'Admin':
    form = BookingNotesForm()
    form2 = BookingUpdateForm()

    if form.validate_on_submit():
      new_note = BookingNote(
                    user_id=current_user.id,
                    booking_id=booking_id,
                    text=form.text.data)
      db.session.add(new_note)
      db.session.commit()
      flash('Nota adicionada com sucesso.', 'info')
      return redirect(url_for('admin_booking', booking_id=booking_id))

    if form2.validate_on_submit():

      if form2.service.data == None or form2.amount_paid.data == None:
        flash('Erro - Corrija o servico ou o valor do servico.', 'danger')
        return redirect(url_for('admin_booking', booking_id=booking_id))
      else:
        updated_booking = Booking.query.filter_by(id=booking_id).first()
        updated_booking.service = form2.service.data
        updated_booking.amount_paid = form2.amount_paid.data
        updated_booking.completed = form2.completed.data
        updated_booking.cleaner = form2.cleaner.data
        updated_booking.supervisor = form2.supervisor.data
        db.session.commit()
        flash('Booking modificado com sucesso.', 'success')
        return redirect(url_for('admin_booking',booking_id=booking_id))

    booking = Booking.query.filter_by(id=booking_id).first()
    if booking:
      return render_template('protected/admin_booking.html', booking=booking, form=form, form2=form2)
    else:
      flash('Esse booking nao e valido.', 'danger')
      return redirect(url_for('admin'))

  flash('Area restrista para administradores.', 'danger')
  return redirect(url_for('profile'))































# New booking route
@app.route('/book', methods=['GET','POST'])
@login_required
def book():
  available_services = Service.query.filter_by(active=True).all()
  form = BookingForm()
  form.service.choices = [(i.id, i.name) for i in available_services]
  if form.validate_on_submit():
    new_booking = Booking(
                  user_id = current_user.id,
                  service=form.service.data,
                  amount_paid=19.99,
                  completed=False)
    db.session.add(new_booking)
    db.session.commit()
    flash('A sua limpeza foi agendada com sucesso!', 'success')
    return redirect(url_for('profile'))

  existing_bookings = Booking.query.filter_by(user_id=current_user.id).all()

  return render_template('protected/book.html', form=form, existing_bookings=existing_bookings)




@app.route('/api/service/<service_id>', methods=['GET', 'POST'])
@login_required
def api_services(service_id):
  service = Service.query.filter_by(id=service_id).first()
  return str(service.price)








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
