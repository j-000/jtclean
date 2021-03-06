import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from time import time
import jwt

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SECRET_KEY'] = 'r25hetAJAOWEHH2829292DJDOFUSODFUOSDJFweewefe515615'
app.config['SECURITY_PASSWORD_SALT'] = 'r25hetAJAOWEHH2829292DJDOFUSODFUOSDJFweewefe515615'
db = SQLAlchemy(app)

class SystemRole(db.Model):
  ''' ID
      1 - User - Cliente or Company
      2 - Staff - Empregado/a, Supervisora, Manager
      3 - Admin - Administrador
      4 - Custom - Custom roles
  '''
  id = db.Column(db.Integer, primary_key=True)
  active = db.Column(db.Boolean(), default=True)
  name = db.Column(db.String(20), unique=True, nullable=False)

  def get_role_rights(self):
    return SystemRights.query.filter_by(system_role_id=self.id).all()



class SystemRights(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean(), default=True)
    system_role_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text(), nullable=False)











class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  timestamp = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
  name = db.Column(db.String(30))
  surname = db.Column(db.String(30))
  email = db.Column(db.String(50), unique=True)
  password = db.Column(db.String(85))
  role = db.Column(db.Integer, default=1)
  premium = db.Column(db.Boolean(), default=False)
  confirmed = db.Column(db.Boolean(), default=False)
  # payment_method_set // boolean

  def get_recover_password_token(self, expires_in=600):
    return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

  @staticmethod
  def verify_reset_password_token(token):
    try:
        id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
    except:
        return
    return User.query.get(id)

  def get_user_role(self):
    return SystemRole.query.filter_by(id=self.role).first()

  def get_profile(self):
    return UserProfile.query.filter_by(user_id=self.id).first()

  def is_admin(self):
    return self.role == SystemRole.query.filter_by(name='Admin').first().id

  def is_staff(self):
    return self.role == SystemRole.query.filter_by(name='Staff').first().id

  def get_staffMemeber_details(self):
    return StaffMember.query.filter_by(user_id=self.id).first()

  def get_user_bookings(self):
    return Booking.query.filter_by(user_id=self.id).all()

  def get_user_confirmed_bookings(self, confirmed=True):
    ''' change "confirmed" to False for negation '''
    return len(Booking.query.filter_by(user_id=self.id, confirmed=confirmed).all())


  def get_total_active_bookings(self, completed=False):
    ''' change "completed" to True for negation '''
    return len(Booking.query.filter_by(user_id=self.id, completed=completed).all())

  def get_all_messages_for_booking(self, booking_id):
    messages = Message.query.filter_by(booking_id=booking_id).order_by(Message.timestamp.asc()).all()
    return messages

  def get_total_unread_messages_for_booking(self, booking_id):
    messages = Message.query.filter_by(read=False, booking_id=booking_id).all()
    return len(messages)



  def get_total_paid(self):
    total = 0
    for i in self.get_user_bookings():
      total += i.amount_paid
    return total

  def get_total_vat(self):
    total = self.get_total_paid()
    vat = total - ( total / 1.2 )
    return round(vat, 2)










class PaymentMethod(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer)
  default = db.Column(db.Boolean(), default=True)
  active = db.Column(db.Boolean(), default=True)





class StaffMember(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer)
  name = db.Column(db.String(20))
  jobRole = db.Column(db.Integer, default=1)
  rate = db.Column(db.Float(), default=5)
  available = db.Column(db.Boolean(), default=True)

  def get_user(self):
    return User.query.filter_by(id=user_id).first()

  def get_jobRole(self):
    return JobRole.query.filter_by(id=self.jobRole).first()



class JobRole(db.Model):
  '''
    1 - Cleaner
    2 - Supervisor
    3 - Manager
  '''
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(30))



class Booking(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
  user_id = db.Column(db.Integer)
  property_type = db.Column(db.String(20))
  service_id = db.Column(db.Integer)
  date_from = db.Column(db.String(25))
  date_to = db.Column(db.String(25))
  address = db.Column(db.String(50))
  start_time = db.Column(db.String(10))
  duration = db.Column(db.Integer)
  amount_paid = db.Column(db.Float())
  comment = db.Column(db.Text())
  confirmed = db.Column(db.Boolean(), default=False)
  confirmed_on = db.Column(db.DateTime, default=None)
  completed = db.Column(db.Boolean(), default=False)
  completed_on = db.Column(db.DateTime, default=None)
  cancelled = db.Column(db.Boolean(), default=False)
  cancelled_on = db.Column(db.DateTime, default=None)
  cleaner = db.Column(db.String(10), nullable=True, default=None)
  supervisor = db.Column(db.String(10), nullable=True, default=None)

  def get_booking_user(self):
    return User.query.filter_by(id=self.user_id).first()

  def get_booking_notes(self):
    return BookingNote.query.filter_by(booking_id=self.id).order_by(BookingNote.created_on.desc()).all()

  def get_booking_total_notes(self):
    return len(BookingNote.query.filter_by(booking_id=self.id).all())

  def get_booking_service(self):
    return Service.query.filter_by(id=self.service_id).first()

  def get_staff_member(self, staffID):
    try:
      s = StaffMember.query.filter_by(id=staffID).first().id
      if s:
        return User.query.filter_by(id=s).first()
    except:
      return None


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





class Message(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  from_user_id = db.Column(db.Integer)
  to_user_id = db.Column(db.Integer)
  booking_id = db.Column(db.Integer)
  timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
  message = db.Column(db.Text())
  read = db.Column(db.Boolean(), default=False)

  def get_message_sender(self):
    return User.query.filter_by(id=self.from_user_id).first()

  def get_message_receiver(self):
    return User.query.filter_by(id=self.to_user_id).first()






class Activity(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer)
  action = db.Column(db.String(100))
  timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

  def get_user_name(self):
    return User.query.filter_by(id=user_id).first()



class UserProfile(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, unique=True)
  filename = db.Column(db.String(50), nullable=True)
  company = db.Column(db.String(50),nullable=True)
  address = db.Column(db.String(50), nullable=True)
  post_code = db.Column(db.String(15), nullable=True)
  favourite_services = db.Column(db.String(50), nullable=True)


