from flask import url_for, render_template, flash, redirect, request
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm, BookingForm, BookingNotesForm, BookingUpdateForm, ServiceForm, SendMessageForm, UpdateUser, UpdateUserAccount, SearchForUserForm
import datetime
from datetime import date, timedelta
import json
from sqlalchemy import desc
from myModels import app

Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

moment = Moment(app)
from myModels import db, Role, User, StaffMember, JobRole, Booking, BookingNote, Service, Message

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
@app.route('/home')
@app.route('/index')
def index():
    return render_template('public/index.html')



# Registration route
@app.route('/registo', methods=['GET','POST'])
def registo():
  form = RegisterForm()
  if request.method == 'POST' and form.validate_on_submit():
    hashed_password = generate_password_hash(form.password.data, method='sha256')
    new_user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    flash('A sua conta foi criada com sucesso!', 'success')
    return redirect(url_for('login'))

  return render_template('public/registo.html', form=form)



# Login route
@app.route('/login', methods=['GET','POST'])
def login():
  form = LoginForm()
  if request.method == 'POST' and form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user:
      if check_password_hash(user.password, form.password.data):
        login_user(user)
        return redirect(url_for('profile'))
      else:
        flash('A palavra passe nao esta correcta.', 'info')
    else:
      flash('Esse email nao se encontra registado.', 'info')
    return redirect(url_for('login'))

  return render_template('public/login.html', form=form)



# Profile route
@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
  return render_template('protected/profile.html')










# Admin route for Admin users
@app.route('/admin', methods=['GET'])
@login_required
def admin():
  ADMIN = Role.query.filter_by(name='Admin').first().id
  if current_user.role == ADMIN:
    return render_template('protected/admin.html')
  flash('Area restrista para administradores.', 'danger')
  return redirect(url_for('profile'))




# Admin route to edit services
@app.route('/admin/admin_services_list/service/<service_id>', methods=['GET'])
@login_required
def admin_service(service_id):
  ADMIN = Role.query.filter_by(name='Admin').first().id
  if current_user.role == ADMIN:
    return render_template('protected/admin.html')
  flash('Area restrista para administradores.', 'danger')
  return redirect(url_for('profile'))







@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
  #  REFACTOR THIS OUT TO AN API
  bookings_array = Booking.query.all()
  bookings_stats = {
    'total': len(bookings_array),
    'today':0,
    'week':0,
    'month':0,
  }
  _today = datetime.datetime.utcnow().date()
  _fiveDaysAgo = _today - timedelta(7)
  _thirtyDaysAgo = _today - timedelta(30)

  for booking in bookings_array:
    booking_date = booking.timestamp.date()
    if booking_date == _today:
      bookings_stats['today'] += 1
    if booking_date >= _fiveDaysAgo and booking_date <= _today:
      bookings_stats['week'] += 1
    if booking_date >= _thirtyDaysAgo and booking_date <= _today:
      bookings_stats['month'] += 1
  # REFACTOR END

  return render_template('protected/admin_dashboard.html', bookings_stats=bookings_stats)


@app.route('/admin/messages')
@login_required
def admin_messages():
  admin_id = User.query.filter_by(name='Admin').first().id
  messages_array = Message.query.filter_by(to_user_id=admin_id).order_by(Message.timestamp.desc()).all()

  return render_template('protected/admin_messages.html', messages_array=messages_array)



@app.route('/admin/users_list')
@login_required
def admin_users_list():
  users_array = User.query.all()
  form = SearchForUserForm()

  return render_template('protected/admin_users_list.html', users_array=users_array, form=form)


@app.route('/admin/admin_bookings_list')
@login_required
def admin_bookings_list():
  bookings_array = Booking.query.all()
  return render_template('protected/admin_bookings_list.html', bookings_array=bookings_array)



@app.route('/admin/admin_services_list', methods=['GET', 'POST'])
@login_required
def admin_services_list():
  ADMIN = Role.query.filter_by(name='Admin').first().id
  if current_user.role == ADMIN:
    form = ServiceForm()
    services_array = Service.query.all()

    if request.method == 'POST' and form.validate_on_submit():
      new_service = Service(name=form.name.data,
                                    description=form.description.data,
                                    price=form.price.data)
      db.session.add(new_service)
      db.session.commit()
      flash('Servico adicionado com sucesso', 'success')
      return redirect(url_for('admin_services_list'))
    else:
      return render_template('protected/admin_services_list.html', services_array=services_array, form=form)
  else:
    flash('Area restrista para administradores.', 'danger')
    return redirect(url_for('profile'))



# Admin route for Admins to modify users
@app.route('/admin/user/<user_id>', methods=['GET', 'POST'])
@login_required
def admin_user(user_id):
  ADMIN = Role.query.filter_by(name='Admin').first().id
  if current_user.role is ADMIN:
    user = User.query.filter_by(id=user_id).first()

    if user:
      form = UpdateUserAccount(obj=user)
      roleChoices = [(i.id, i.name) for i in Role.query.all()]
      form.role.choices = roleChoices

      if request.method == 'POST' and form.validate_on_submit():
        user.role = form.role.data
        user.premium = form.premium.data
        db.session.commit()

        flash('User modificado com successo', 'success')
        return redirect(url_for('admin_user', user_id=user_id))

      return render_template('protected/admin_user.html', user=user, form=form)

    else:
      flash('Esse user nao existe.', 'danger')
      return redirect(url_for('admin'))

  else:
    flash('Area restrista para administradores.', 'danger')
    return redirect(url_for('profile'))




def add_booking_note(user_id, booking_id, text):
  try:
    new_note = BookingNote(user_id=user_id, booking_id=booking_id, text=text)
    db.session.add(new_note)
    db.session.commit()
    return True
  except Exception as e:
    return False


# Admin route for Admins to modify bookings
@app.route('/admin/booking/<booking_id>', methods=['GET', 'POST'])
@login_required
def admin_booking(booking_id):
  ADMIN = Role.query.filter_by(name='Admin').first().id
  if current_user.role == ADMIN:
    form = BookingNotesForm()
    form2 = BookingUpdateForm()
    services_array = Service.query.filter_by(active=True).all()
    job_cleaner_id = JobRole.query.filter_by(name='Cleaner').first().id
    cleaners = [(i.id, i.name) for i in StaffMember.query.filter_by(id=job_cleaner_id,available=True).all()]
    job_supervisors_id = JobRole.query.filter_by(name='Supervisor').first().id
    supervisors = [(i.id, i.name) for i in StaffMember.query.filter_by(id=job_supervisors_id,available=True).all()]
    form2.service.choices = [(i.id, i.name) for i in services_array]
    form2.cleaner.choices = cleaners
    form2.supervisor.choices = supervisors

    if request.method == 'POST' and form.validate_on_submit():
      if add_booking_note(current_user.id, booking_id, form.text.data):
        flash('Nota adicionada com sucesso.', 'info')
        return redirect(url_for('admin_booking', booking_id=booking_id))

    if request.method == 'POST' and form2.validate_on_submit():
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
        return redirect(url_for('admin_booking', booking_id=booking_id))

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
  bookingForm = BookingForm()
  choices = [(0,'Escolha um servico')] + [(i.id, i.name) for i in available_services]
  bookingForm.service.choices = choices

  if request.method == 'POST' and bookingForm.validate_on_submit():

    service_price = Service.query.filter_by(id=bookingForm.service.data).first().price

    new_booking = Booking(
                  user_id = current_user.id,
                  property_type = bookingForm.propertyType.data,
                  service_id=bookingForm.service.data,
                  date_from=bookingForm.date_from.data,
                  date_to=bookingForm.date_to.data,
                  start_time=bookingForm.time.data,
                  duration=bookingForm.duration.data,
                  amount_paid=service_price,
                  comment=bookingForm.comments.data)

    db.session.add(new_booking)
    db.session.commit()
    flash('A sua limpeza foi agendada com sucesso!', 'success')
    return redirect(url_for('profile'))

  return render_template('protected/book.html', form=bookingForm)




# API route
@app.route('/api/service/<service_id>', methods=['GET', 'POST'])
@login_required
def api_services(service_id):
  try:
    service = Service.query.filter_by(id=service_id).first()
    response = str(service.price)
  except Exception as e:
    response = str(0)

  return response



# Dashboard route
@app.route('/profile/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
  return render_template('protected/dashboard.html')



# Messages route
@app.route('/profile/messages', methods=['GET','POST'])
@login_required
def messages():
  messageForm = SendMessageForm()
  if request.method == 'POST' and messageForm.validate_on_submit():
    new_message = Message(
                  from_user_id = current_user.id,
                  to_user_id = messageForm.to_user.data,
                  message = messageForm.message.data
      )
    db.session.add(new_message)
    db.session.commit()
    flash('Mensagem enviada com sucesso.', 'success')
    return redirect(url_for('messages'))

  return render_template('protected/messages.html', form=messageForm)



# Open message route
@app.route('/profile/messages/<message_id>', methods=['GET'])
@login_required
def open_message(message_id):
  message = Message.query.filter_by(id=message_id).first()
  if message:
    if message.to_user_id == current_user.id or message.from_user_id == current_user.id:
      messageForm = SendMessageForm()

      if not message.read:
        message.read = True
        db.session.commit()

      return render_template('protected/open_message.html', message=message, form=messageForm)
  flash('Essa mensagem nao existe.', 'danger')
  return redirect(url_for('messages'))



# User Profile settings route
@app.route('/profile/settings', methods=['GET','POST'])
@login_required
def profile_settings():
  form = UpdateUser()
  if request.method == 'POST' and form.validate_on_submit():
    user = User.query.filter_by(id=current_user.id).first()
    email_exists = User.query.filter_by(email=form.email.data).first()
    if check_password_hash(user.password, form.password.data) and not email_exists:
      user.email = form.email.data
      if form.new_password.data:
        user.password = generate_password_hash(form.new_password.data, method='sha256')
      db.session.commit()
      flash('A sua conta foi alterada com sucesso. Faca o login novamente.', 'success')
      logout_user()
      return redirect(url_for('login'))
    else:
      flash('Palavra passe errada ou email ja existe.', 'danger')
      return redirect(url_for('profile'))

  return render_template('protected/profile_settings.html', form=form)



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



############## HELPER DUMMY FUCNTIONS

def create_roles():
  # Add Roles
  u = Role(name='User')
  s = Role(name='Staff')
  a = Role(name='Admin')
  db.session.add(u)
  db.session.add(s)
  db.session.add(a)
  db.session.commit()
  return None


def create_job_roles():
  # Add JobRoles
  cl = JobRole(name='Cleaner')
  sp = JobRole(name='Supervisor')
  mn = JobRole(name='Manager')
  db.session.add(cl)
  db.session.add(sp)
  db.session.add(mn)
  db.session.commit()
  return None

def create_sample_users():
  admin_user = User(name='Admin',
                  surname='Office',
                  email='a@jt.com',
                  password=generate_password_hash('tina1234', method='sha256'),
                  role=3,
                  premium=True)
  db.session.add(admin_user)

  # add a cleaner
  cleaner_user = User(name='Tina',
                surname='Silva',
                email='t@jt.com',
                password=generate_password_hash('tina1234', method='sha256'),
                role=2)
  db.session.add(cleaner_user)

  # add a customer
  customer_user = User(name='Bob',
                surname='Dowie',
                email='b@jt.com',
                password=generate_password_hash('tina1234', method='sha256'))
  db.session.add(customer_user)

  db.session.commit()
  return None

############## END HELPER DUMMY FUNCTIONS



# Start app
if __name__ == '__main__':
  # create_roles()
  # create_job_roles()
  # create_sample_users()
  app.run(debug=True)
