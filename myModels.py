import datetime
from __main__ import app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy(app)

class Role(db.Model):
  ''' ID |
      1 - User - Cliente or Company
      2 - Staff - Empregado/a, Supervisora, Manager
      3 - Admin - Administrador
  '''
  id = db.Column(db.Integer, primary_key=True)
  active = db.Column(db.Boolean(), default=True)
  name = db.Column(db.String(20), unique=True)





class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  timestamp = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
  name = db.Column(db.String(30))
  surname = db.Column(db.String(30))
  email = db.Column(db.String(50), unique=True)
  password = db.Column(db.String(85))
  role = db.Column(db.Integer, default=1)
  premium = db.Column(db.Boolean(), default=False)

  def get_user_role(self):
    return Role.query.filter_by(id=self.role).first()

  def is_admin(self):
    return self.role == Role.query.filter_by(name='Admin').first().id

  def is_staff(self):
    return self.role == Role.query.filter_by(name='Staff').first().id

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

  def get_messages_from_user(self):
    return Message.query.filter_by(from_user_id=self.id).order_by(Message.timestamp.desc()).all()

  def get_messages_to_user(self):
    return Message.query.filter_by(to_user_id=self.id).order_by(Message.timestamp.desc()).all()

  def get_total_messages_to_user(self):
    return len(Message.query.filter_by(to_user_id=self.id).all())

  def get_total_unread_messages_to_user(self):
    return len(Message.query.filter_by(to_user_id=self.id, read=False).all())

  def get_staffMemeber_details(self):
    return StaffMember.query.filter_by(user_id=self.id).all()






class PaymentMethod(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer)
  default = db.Column(db.Boolean(), default=True)
  active = db.Column(db.Boolean(), default=True)





class StaffMember(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer)
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
  start_time = db.Column(db.String(10))
  duration = db.Column(db.Integer)
  amount_paid = db.Column(db.Float())
  comment = db.Column(db.Text()) # customer's coment
  completed = db.Column(db.Boolean(), default=False)
  cleaner = db.Column(db.String(10), nullable=True, default=None)
  supervisor = db.Column(db.String(10), nullable=True, default=None)

  def get_booking_user(self):
    return User.query.filter_by(id=self.user_id).first()

  def get_booking_notes(self): # admin staff's notes
    return BookingNote.query.filter_by(booking_id=self.id).all()

  def get_booking_service(self):
    return Service.query.filter_by(id=self.service_id).first()

  def get_assignable_staff(self):
    return Cleaner.query.filter_by(available=True).all()

  def get_service(self):
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





class Message(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  from_user_id = db.Column(db.Integer)
  to_user_id = db.Column(db.Integer)
  timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
  message = db.Column(db.Text())
  read = db.Column(db.Boolean(), default=False)

  def get_message_sender(self):
    return User.query.filter_by(id=self.from_user_id).first()

  def get_message_receiver(self):
    return User.query.filter_by(id=self.to_user_id).first()








