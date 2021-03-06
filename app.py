from flask import url_for, render_template, flash, redirect, request, escape
from flask_mail import Mail
from flask_mail import Message as MailMessage
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm, BookingForm, BookingNotesForm, BookingUpdateForm, ServiceForm, SendMessageForm, UpdateUser, UpdateUserAccount, SearchForUserForm, UpdateUserProfile,RecoverPasswordForm, ResetPasswordForm
import datetime
from datetime import date, timedelta
import json
from sqlalchemy import desc
from myModels import app
from itsdangerous import URLSafeTimedSerializer
import requests
from functools import wraps
from werkzeug.utils import secure_filename
import os
import uuid
from threading import Thread

# File uploads
# THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
# UPLOAD_FOLDER = THIS_FOLDER + '/static/images/uploads/'
# ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'svg'])
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# file = request.files['image']
    # if file and allowed_file(file.filename):
    #   filename = str(uuid.uuid4())[:6] + secure_filename(file.filename)
#     #   file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
# def allowed_file(filename):
#   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config.update(
  DEBUG=False,
  MAIL_SERVER='smtp.gmail.com',
  MAIL_PORT=465,
  MAIL_USE_SSL=True,
  MAIL_USERNAME = 'jtcleaningltd@gmail.com',
  MAIL_PASSWORD = 'JTcleaning123',
  MAIL_DEFAULT_SENDER = 'jtcleaningltd@gmail.com'
  )

mail = Mail(app)

Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

moment = Moment(app)
from myModels import db, SystemRole, User, StaffMember, JobRole, Booking, BookingNote, Service, Message, UserProfile, SystemRights

# USER LOADER
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
  flash('Por favor entre na sua conta para aceder ao seu perfile.', 'info')
  return redirect(url_for('login', next=request.url))


def send_async_email(app, msg):
  with app.app_context():
    mail.send(msg)


def sendEmail(email_subject, recipients, email_text=None, email_html=None):
  msg = MailMessage(email_subject, recipients=recipients)
  msg.body = email_text
  msg.html = email_html
  Thread(target=send_async_email, args=(app, msg)).start()




def generate_confirmation_token(email):
  serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
  return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
  serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
  try:
    email = serializer.loads(
        token,
        salt=app.config['SECURITY_PASSWORD_SALT'],
        max_age=expiration
    )
  except:
      return False
  return email


# custom decorator to ensure accounts are confirmed
def confirmed_account_required(fn):
  @wraps(fn)
  def wrapper(*args,**kwargs):
    if not current_user.confirmed:
      flash('Confirme a sua conta primeiro atraves do link enviado para o seu email.','danger')
      return redirect(url_for('profile'))
    else:
      return fn(*args, **kwargs)
  return wrapper


# ROUTES
# Index route - main page
@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
  return render_template('public/index.html')


# Registration route
@app.route('/register', methods=['GET','POST'])
def registo():
  if current_user.is_authenticated:
    return redirect(url_for('profile'))
  else:
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
      if form.password.data != form.password2.data:
        flash('As palavras passe nao sao identicas. Faca o registo de novo.','danger')
        return redirect(url_for('registo'))
      hashed_password = generate_password_hash(form.password.data, method='sha256')
      new_user = User(
              name = escape(form.name.data),
              surname = escape(form.surname.data),
              email = escape(form.email.data),
              password = hashed_password)
      db.session.add(new_user)
      db.session.commit()

      new_profile = UserProfile(user_id=User.query.filter_by(email=escape(form.email.data)).first().id)
      db.session.add(new_profile)
      db.session.commit()

      token = generate_confirmation_token(escape(form.email.data))
      url = url_for('confirm_email', token=token, _external=True)
      print(url)
      html = render_template('email_templates/welcome_email.html', confirm_url=url)
      sendEmail(email_subject='Confirme a sua conta!',
                recipients=[escape(form.email.data)],
                email_html=html)

      flash('A sua conta foi criada com sucesso! Faca confirmacao da sua conta atraves do link enviado para o seu email.', 'success')
      return redirect(url_for('login'))
    else:
      return render_template('public/registo.html', form=form)


@app.route('/confirm_email/<token>')
@login_required
def confirm_email(token):
  try:
    email = confirm_token(token)
  except:
    pass

  if email:
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
      flash('A sua conta ja se encontra verificada.','success')
    else:
      user.confirmed = True
      db.session.commit()
      flash('A sua conta foi verificada com sucesso!','success')
  else:
    flash('O link nao e valido ou expirou. Verifique a sua conta com o novo link que acabou de ser enviado.', 'danger')
    token = generate_confirmation_token(current_user.email)
    url = url_for('confirm_email', token=token, _external=True)
    html = render_template('email_templates/welcome_email.html', confirm_url=url)
    sendEmail(email_subject='Confirme a sua conta de novo!',
                recipients=[current_user.email],
                email_html=html)

  return redirect(url_for('profile'))


# Login route
@app.route('/login', methods=['GET','POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('profile'))
  else:
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
      user = User.query.filter_by(email = escape(form.email.data)).first()
      if user:
        if check_password_hash(user.password, form.password.data):
          login_user(user)
          return redirect(url_for('profile'))
        else:
          flash('A palavra passe ou o email nao estao correctos.', 'info')
      else:
        flash('Esse email nao se encontra registado.', 'info')
      return redirect(url_for('login'))
    else:
      return render_template('public/login.html', form=form)


@app.route('/help', methods=['GET', 'POST'])
def help():
  recover_password_form = RecoverPasswordForm()
  if request.method == 'POST' and recover_password_form.validate_on_submit():
    email = escape(recover_password_form.email.data)
    user = User.query.filter_by(email=email).first()
    if user:
      recover_token = user.get_recover_password_token()
      url = url_for('recover_password', recover_token=recover_token, _external=True)
      html = render_template('email_templates/reset_password.html', confirm_url=url)
      sendEmail(email_subject='Reponha a sua palavra passe',
                recipients=[email],
                email_html=html)

      flash('Foi enviado um email com instrucoes para repor a sua palavra passe.','info')
    else:
      flash('Esse email nao se encontra registado','info')
    return redirect(url_for('login'))

  return render_template('public/help.html', form=recover_password_form)


@app.route('/recover_password/<recover_token>', methods=['GET','POST'])
def recover_password(recover_token):
  if current_user.is_authenticated:
    return redirect(url_for('profile'))

  user = User.verify_reset_password_token(recover_token)
  if not user:
    flash('O link para recuperar a palavra passe e invalido ou expirou.', 'info')
    return redirect(url_for('login'))

  form = ResetPasswordForm()
  if request.method == 'POST' and form.validate_on_submit():
    if form.password.data != form.password2.data:
      flash('As palavras passe nao sao identicas. Tente de novo.','danger')
      return redirect(url_for('login'))

    hashed_password = generate_password_hash(form.password.data, method='sha256')
    user.password = hashed_password
    db.session.commit()
    flash('A sua palavra passe foi alterada com sucesso. Entre na sua conta.', 'success')
    return redirect(url_for('login'))

  return render_template('public/reset_password.html',form=form, token=recover_token)


# Profile route
@app.route('/profile', methods=['GET'])
@login_required
def profile():
  if not current_user.confirmed:
    flash('Deve confirmar a sua conta atraves do link enviado para o seu email.','danger')
  return render_template('protected/menu.html')



@app.route('/profile/services', methods=['GET'])
@login_required
@confirmed_account_required
def new_booking():
  return render_template('protected/new_booking.html')


@app.route('/profile/messages/<booking_id>', methods=['GET','POST'])
@login_required
@confirmed_account_required
def messages(booking_id):
  messageForm = SendMessageForm()
  escaped_booking_id = escape(booking_id)
  if request.method == 'POST' and messageForm.validate_on_submit():
    new_message = Message(
                  from_user_id = current_user.id,
                  booking_id = escaped_booking_id,
                  message = messageForm.message.data)
    db.session.add(new_message)
    db.session.commit()
    flash('Mensagem enviada com sucesso.', 'success')
    return redirect(url_for('open_booking', booking_id=escaped_booking_id))
  else:
    return redirect(url_for('profile'))


# New booking route
@app.route('/profile/services/book', methods=['GET','POST'])
@login_required
@confirmed_account_required
def book():
  available_services = Service.query.filter_by(active=True).all()
  user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()

  # user default settings
  if user_profile:
    bookingForm = BookingForm(obj=user_profile)
  else:
    bookingForm = BookingForm()

  choices = [(0,'Escolha um servico')] + [(i.id, i.name) for i in available_services]
  bookingForm.service.choices = choices
  if request.method == 'POST' and bookingForm.validate_on_submit():
    service_price = Service.query.filter_by(id=escape(bookingForm.service.data)).first().price
    new_booking = Booking(
      user_id = current_user.id,
      property_type = escape(bookingForm.propertyType.data),
      service_id = escape(bookingForm.service.data),
      date_from = escape(bookingForm.date_from.data),
      date_to = escape(bookingForm.date_to.data),
      address = escape(bookingForm.address.data),
      start_time = escape(bookingForm.time.data),
      duration = escape(bookingForm.duration.data),
      amount_paid = service_price,
      comment = escape(bookingForm.comments.data))
    db.session.add(new_booking)
    db.session.commit()

    # refactor this to an object to be user on the template... booking.property_type..
    html = render_template('email_templates/new_booking.html',
      property_type=escape(bookingForm.propertyType.data),
      date_from=escape(bookingForm.date_from.data),
      date_to=escape(bookingForm.date_to.data),
      address = escape(bookingForm.address.data),
      start_time = escape(bookingForm.time.data),
      duration = escape(bookingForm.duration.data),
      amount_paid = service_price,
      comment = escape(bookingForm.comments.data))
    sendEmail(email_subject='[JTClean] - A sua limpeza esta a ser approvada',
                recipients=[current_user.email],
                email_html=html)
    flash('A sua limpeza foi agendada com sucesso! Recebera um email dentro de momentos com os detalhes todos.', 'success')
    return redirect(url_for('my_bookings'))
  else:
    return render_template('protected/book.html', form=bookingForm)



@app.route('/profile/services/my_bookings', methods=['GET'])
@login_required
@confirmed_account_required
def my_bookings():
  return render_template('protected/mybookings.html')


@app.route('/profile/services/historical_bookings')
@login_required
@confirmed_account_required
def historical_bookings():
  return render_template('protected/historical_bookings.html')


@app.route('/profile/services/my_bookings/<booking_id>', methods=['GET','POST'])
@login_required
@confirmed_account_required
def open_booking(booking_id):
  escaped_booking_id = escape(booking_id)
  booking = Booking.query.filter_by(id=escaped_booking_id).first()
  if booking:
    # Update all unread messages to read.
    messages_to_user = Message.query.filter_by(booking_id=escaped_booking_id, read=False).all()
    for unread_message in messages_to_user:
      unread_message.read = True
    db.session.commit()

    # Handle send message form
    messageForm = SendMessageForm()
    if request.method == 'POST' and messageForm.validate_on_submit():
      new_message = Message(
                    from_user_id = current_user.id,
                    booking_id = booking.id,
                    message = escape(messageForm.message.data))
      db.session.add(new_message)
      db.session.commit()
      flash('Mensagem enviada com sucesso.', 'success')
      return redirect(url_for('open_booking', booking_id=escaped_booking_id))
    else:
      return render_template('protected/open_booking.html', booking=booking, form=messageForm)
  else:
    flash('Esse booking nao existe.','danger')
    return redirect(url_for('my_bookings'))


# User Profile settings route
@app.route('/profile/settings', methods=['GET','POST'])
@login_required
@confirmed_account_required
def profile_settings():
  form = UpdateUser()
  if request.method == 'POST' and form.validate_on_submit():
    user = User.query.filter_by(id=current_user.id).first()
    email_exists = User.query.filter_by(email=escape(form.email.data)).first()
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
  else:
    return render_template('protected/profile_settings.html', form=form)




# Dashboard route
@app.route('/profile/user', methods=['GET','POST'])
@login_required
@confirmed_account_required
def user_profile():
  form = UpdateUserProfile(obj=UserProfile.query.filter_by(user_id=current_user.id).first_or_404())
  form.favourite_services.choices = [(i.id, str(i.id) + ') ' + i.name) for i in Service.query.all()]

  if request.method == 'POST' and form.validate_on_submit():

    profile_exists = UserProfile.query.filter_by(user_id=current_user.id).first()
    if profile_exists:
      profile_exists.company = form.company.data
      profile_exists.address = form.address.data
      profile_exists.post_code = form.post_code.data
      profile_exists.favourite_services = str(form.favourite_services.data)
      db.session.commit()
    else:
      new_profile = UserProfile(
        user_id=current_user.id,
        company = form.company.data,
        address=form.address.data,
        post_code=form.post_code.data,
        favourite_services=str(form.favourite_services.data))
      db.session.add(new_profile)
      db.session.commit()

    flash('Perfile modificado com sucesso.','success')
    return redirect(url_for('user_profile'))

  return render_template('protected/user_profile.html', form=form)



# Dashboard route
@app.route('/profile/dashboard', methods=['GET'])
@login_required
@confirmed_account_required
def dashboard():
  return render_template('protected/dashboard.html')


# Logout route
@app.route('/logout', methods=['GET'])
@login_required
def logout():
  logout_user();
  return redirect(url_for('index'))



################################# API ###########################################
# API route PUBLIC
@app.route('/api/service/<service_id>', methods=['GET', 'POST'])
@login_required
def api_services(service_id):
  try:
    service = Service.query.filter_by(id=service_id).first()
    response = str(service.price)
  except Exception as e:
    response = str(0)

  return response


# API route PRIVATE
@app.route('/api/admin/dashboard/', methods=['GET'])
@login_required
def api_admin_dashboard():
  if current_user.is_admin():

    _today = datetime.datetime.utcnow().date()
    _fiveDaysAgo = _today - timedelta(7)
    _thirtyDaysAgo = _today - timedelta(30)

    # Bookings Stats
    response = {}
    bookings_array = Booking.query.all()
    bookings_stats = {
      'created':{
        'total': len(bookings_array),
        'today':0,
        'week':0,
        'month':0,
      },
      'confirmed':{
        'total':0,
        'today':0,
        'week':0,
        'month':0
      },
      'cancelled':{
        'total':0,
        'today':0,
        'week':0,
        'month':0
      },
      'unconfirmed':0,
    }

    for booking in bookings_array:
      booking_date = booking.timestamp.date()
      if booking_date == _today:
        bookings_stats['created']['today'] += 1
      if booking_date >= _fiveDaysAgo and booking_date <= _today:
        bookings_stats['created']['week'] += 1
      if booking_date >= _thirtyDaysAgo and booking_date <= _today:
        bookings_stats['created']['month'] += 1

      if booking.confirmed:
        bookings_stats['confirmed']['total'] += 1
        confirmed_date = booking.confirmed_on.date()
        if confirmed_date == _today:
          bookings_stats['confirmed']['today'] += 1
        if confirmed_date >= _fiveDaysAgo and confirmed_date <= _today:
          bookings_stats['confirmed']['week'] += 1
        if confirmed_date >= _thirtyDaysAgo and confirmed_date <= _today:
          bookings_stats['confirmed']['month'] += 1

      if booking.cancelled:
        bookings_stats['cancelled']['total'] += 1
        cancelled_date = booking.confirmed_on.date()
        if cancelled_date == _today:
          bookings_stats['cancelled']['today'] += 1
        if cancelled_date >= _fiveDaysAgo and cancelled_date <= _today:
          bookings_stats['cancelled']['week'] += 1
        if cancelled_date >= _thirtyDaysAgo and cancelled_date <= _today:
          bookings_stats['cancelled']['month'] += 1


      if not booking.confirmed and not booking.cancelled:
        bookings_stats['unconfirmed'] += 1



    response['bookings_stats'] = bookings_stats
    # End booking stats

    # Users Stats
    users_array = User.query.all()
    users_stast = {
      'created':{
        'total':len(users_array),
        'today':0,
        'week':0,
        'month':0
      }
    }
    for user in users_array:
      user_created_date = user.timestamp.date()
      if user_created_date == _today:
        users_stast['created']['today'] += 1
      if user_created_date > _fiveDaysAgo and user_created_date <= _today:
        users_stast['created']['week'] += 1
      if user_created_date >= _thirtyDaysAgo and user_created_date <= _today:
        users_stast['created']['month'] += 1

    response['users_stats'] = users_stast
    response['unread_messages'] = {}
    unread_messages = Message.query.filter_by(read=False).all()
    response['unread_messages']['total'] = len(unread_messages)
    response['unread_messages']['bookings_array'] = list(set([(i.booking_id) for i in unread_messages]))
    return json.dumps(response)

  else:
    flash('Area restricta para developers. Precisa de aceder ao nosso API? Contacte a nossa equipa.','info')
    return redirect(url_for('login'))














##################################ADMIN ROUTES##################################



# Admin route for Admin users
@app.route('/admin', methods=['GET'])
@login_required
def admin():
  if current_user.is_admin():
    return render_template('protected/admin/admin.html')
  else:
    flash('Area restrista para administradores.', 'danger')
    return redirect(url_for('profile'))



@app.route('/admin/dashboard', methods=['GET'])
@login_required
def admin_dashboard():
  if current_user.is_admin():
    api_url=url_for('api_admin_dashboard', _external=True)
    return render_template('protected/admin/admin_dashboard.html', api_url=api_url)
  else:
    flash('Area restrista para administradores.', 'danger')
    return redirect(url_for('profile'))


@app.route('/admin/messages', methods=['GET'])
@login_required
def admin_messages():
  if current_user.is_admin():
    admin_id = User.query.filter_by(name='Admin').first().id
    messages_array = Message.query.filter_by(to_user_id=admin_id).order_by(Message.timestamp.desc()).all()
    return render_template('protected/admin/admin_messages.html', messages_array=messages_array)
  else:
    flash('Area restrista para administradores.', 'danger')
    return redirect(url_for('profile'))


@app.route('/admin/users_list', methods=['GET'])
@login_required
def admin_users_list():
  if current_user.is_admin():
    users_array = User.query.all()
    form = SearchForUserForm()
    return render_template('protected/admin/admin_users_list.html', users_array=users_array, form=form)
  else:
    flash('Area restrista para administradores.', 'danger')
    return redirect(url_for('profile'))


@app.route('/admin/admin_bookings_list', methods=['GET'])
@login_required
def admin_bookings_list():
  if current_user.is_admin():
    bookings_array = Booking.query.all()
    return render_template('protected/admin/admin_bookings_list.html', bookings_array=  bookings_array)
  else:
    flash('Area restrista para administradores.', 'danger')
    return redirect(url_for('profile'))



@app.route('/admin/admin_services_list', methods=['GET', 'POST'])
@login_required
def admin_services_list():
  if current_user.is_admin():
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
      return render_template('protected/admin/admin_services_list.html', services_array=services_array, form=form)
  else:
    flash('Area restrista para administradores.', 'danger')
    return redirect(url_for('profile'))



# Admin route for Admins to modify users
@app.route('/admin/user/<user_id>', methods=['GET', 'POST'])
@login_required
def admin_user(user_id):
  if current_user.is_admin():
    user = User.query.filter_by(id=user_id).first()
    role_staff_id = SystemRole.query.filter_by(name='Staff').first().id
    if user:
      form = UpdateUserAccount(obj=user)
      roleChoices = [(i.id, i.name) for i in SystemRole.query.all()]
      form.role.choices = roleChoices
      form.staffRole.choices = [(i.id, i.name) for i in JobRole.query.all()]

      if request.method == 'POST' and form.validate_on_submit():
        if form.role.data == role_staff_id:
          find_staff = StaffMember.query.filter_by(user_id=user.id).first_or_404()
          if find_staff:
            update_staff = find_staff
            update_staff.jobRole = form.staffRole.data
          else:
            add_user_as_staff = StaffMember(
              user_id=user.id,
              name=user.name,
              jobRole=form.staffRole.data)
            db.session.add(add_user_as_staff)

        user.role = form.role.data
        user.premium = form.premium.data
        db.session.commit()
        flash('User modificado com successo', 'success')
        return redirect(url_for('admin_user', user_id=user_id))
      else:
        return render_template('protected/admin/admin_user.html', user=user, form=form)
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
  if current_user.is_admin():
    booking = Booking.query.filter_by(id=booking_id).first()
    if booking:

      # Handle Booking Notes
      form = BookingNotesForm()

      # Handle Changes to Booking
      form2 = BookingUpdateForm(obj=booking)
      services_array = Service.query.filter_by(active=True).all()
      job_cleaner_id = JobRole.query.filter_by(name='Cleaner').first().id
      cleaners = [(i.id, i.name) for i in StaffMember.query.filter_by(id=job_cleaner_id, available=True).all()]
      job_supervisors_id = JobRole.query.filter_by(name='Supervisor').first().id
      supervisors = [(i.id, i.name) for i in StaffMember.query.filter_by(id=job_supervisors_id,available=True).all()]
      form2.service.choices = [(i.id, i.name) for i in services_array]
      form2.cleaner.choices = cleaners
      form2.supervisor.choices = supervisors

      # Handle Chat
      form3 = SendMessageForm()

      return render_template('protected/admin/admin_booking.html', booking=booking, form=form, form2=form2, form3=form3)
    else:
      flash('Esse booking nao e valido.', 'danger')
      return redirect(url_for('admin'))

  flash('Area restrista para administradores.', 'danger')
  return redirect(url_for('profile'))




@app.route('/admin/add_note/booking/<booking_id>', methods=['GET', 'POST'])
@login_required
def admin_booking_notes(booking_id):
  if current_user.is_admin():
    escaped_booking_id = escape(booking_id)
    form = BookingNotesForm()
    if request.method == 'POST' and form.validate_on_submit():
      escaped_note = escape(form.text.data)
      if add_booking_note(current_user.id, escaped_booking_id, escaped_note):
        flash('Nota adicionada com sucesso.', 'success')
        return redirect(url_for('admin_booking', booking_id=booking_id))
    else:
      flash('Por favor reveja a nota.', 'info')
      return redirect(url_for('admin_booking', booking_id=escaped_booking_id))
  else:
    flash('Area restrista para administradores.','danger')
    return redirect(url_for('profile'))



@app.route('/admin/send_message/booking/<booking_id>', methods=['GET','POST'])
@login_required
def admin_booking_send_message(booking_id):
  if current_user.is_admin():
    form3 = SendMessageForm()
    escaped_booking_id = escape(booking_id)
    escaped_message = escape(form3.message.data)
    if request.method == 'POST' and form3.validate_on_submit():
      new_message = Message(
                  from_user_id = current_user.id,
                  booking_id = escaped_booking_id,
                  message = escaped_message)
      db.session.add(new_message)
      db.session.commit()
      flash('Mensagem enviada com sucesso.', 'success')
      return redirect(url_for('admin_booking', booking_id=escaped_booking_id))
  else:
    flash('Area restrista para administradores.','danger')
    return redirect(url_for('profile'))



@app.route('/admin/update/booking/<booking_id>', methods=['GET','POST'])
@login_required
def admin_booking_update(booking_id):
  form2 = BookingUpdateForm()
  services_array = Service.query.filter_by(active=True).all()
  job_cleaner_id = JobRole.query.filter_by(name='Cleaner').first().id
  cleaners = [(i.id, i.name) for i in StaffMember.query.filter_by(id=job_cleaner_id, available=True).all()]
  job_supervisors_id = JobRole.query.filter_by(name='Supervisor').first().id
  supervisors = [(i.id, i.name) for i in StaffMember.query.filter_by(id=job_supervisors_id,available=True).all()]
  form2.service.choices = [(i.id, i.name) for i in services_array]
  form2.cleaner.choices = cleaners
  form2.supervisor.choices = supervisors

  if current_user.is_admin():

    if request.method == 'POST' and form2.validate_on_submit():
      escaped_booking_id = escape(booking_id)

      updated_booking = Booking.query.filter_by(id=escaped_booking_id).first()
      updated_booking.service = form2.service.data
      updated_booking.amount_paid = form2.amount_paid.data

      updated_booking.confirmed = form2.confirmed.data
      if form2.confirmed.data:
        updated_booking.confirmed_on = datetime.datetime.utcnow()

      updated_booking.completed = form2.completed.data
      if form2.completed.data:
        updated_booking.completed_on = datetime.datetime.utcnow()

      updated_booking.cancelled = form2.cancelled.data
      if form2.cancelled.data:
        updated_booking.cancelled_on = datetime.datetime.utcnow()

      updated_booking.cleaner = form2.cleaner.data
      updated_booking.supervisor = form2.supervisor.data
      db.session.commit()

      flash('Booking modificado com sucesso.', 'success')
      return redirect(url_for('admin_booking', booking_id=escaped_booking_id))
    else:

      flash('Reveja a modificacao do booking.','info')
      return redirect(url_for('admin_booking', booking_id=booking_id))

  else:
    flash('Area restrista para administradores.','danger')
    return redirect(url_for('profile'))




# 404 route
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


#Start app
if __name__ == '__main__':
  app.run(debug=True)
