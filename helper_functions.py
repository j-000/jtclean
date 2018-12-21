from app import db, Role, JobRole, StaffMember, User, generate_password_hash


def drop_all_tables():
  db.drop_all()
  return None

def create_all_tables():
  db.create_all()
  return None

def create_account_roles():
  a = Role(name='User')
  b = Role(name='Staff')
  c = Role(name='Admin')
  db.session.add_all([a,b,c])
  db.session.commit()
  return None


def create_job_roles():
  a = JobRole(name='Cleaner')
  b = JobRole(name='Supervisor')
  c = JobRole(name='Manager')
  db.session.add_all([a,b,c])
  db.session.commit()
  return None


def add_staff_member(user_name, user_role, jobRole):
  user_id = User.query.filter_by(name=user_name,role=user_role).first().id
  staff = StaffMember(
      user_id=user_id,
      name=user_name,
      jobRole=jobRole)
  db.session.add(staff)
  db.session.commit()
  return None


def create_main_users():
  admin_user = User(
    name='Admin',
    surname='Office',
    email='admin@jt.com',
    password=generate_password_hash('tina1234', method='sha256'),
    role=3,
    premium=True,
    confirmed=True)

  cleaner_user = User(
    name='Cleaner',
    surname='Office',
    email='cleaner@jt.com',
    password=generate_password_hash('tina1234', method='sha256'),
    role=2,
    premium=True,
    confirmed=True)


  supervisor_user = User(
    name='Supervisor',
    surname='Office',
    email='supervisor@jt.com',
    password=generate_password_hash('tina1234', method='sha256'),
    role=2,
    premium=True,
    confirmed=True)


  manager_user = User(
    name='Manager',
    surname='Office',
    email='manager@jt.com',
    password=generate_password_hash('tina1234', method='sha256'),
    role=2,
    premium=True,
    confirmed=True)


  customer_user = User(
    name='User',
    surname='Office',
    email='user@jt.com',
    password=generate_password_hash('tina1234', method='sha256'),
    premium=True,
    confirmed=True)

  db.session.add_all([admin_user, cleaner_user, supervisor_user, manager_user, customer_user])
  db.session.commit()

  add_staff_member('Cleaner',2,1)
  add_staff_member('Supervisor',2,2)
  add_staff_member('Manager',2,3)

  return None
