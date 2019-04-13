from app import db, SystemRole, JobRole, StaffMember, User, generate_password_hash, SystemRights


def drop_all_tables():
  db.drop_all()
  return None


def create_all_tables():
  db.create_all()
  return None


def create_system_roles():
  a = SystemRole(name='User')
  b = SystemRole(name='Staff')
  c = SystemRole(name='Admin')
  db.session.add_all([a,b,c])
  db.session.commit()
  return None


def create_system_rights():
  user_role_id = SystemRole.query.filter_by(name='User').first().id
  staff_role_id = SystemRole.query.filter_by(name='Staff').first().id
  admin_role_id = SystemRole.query.filter_by(name='Admin').first().id

  a = SystemRights(
        system_role_id=admin_role_id,
        name='ADMIN:NO RESTRICTIONS',
        description='Admin / developer - no restrictions on the system.')

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


if __name__ == "__main__":
  drop_all_tables()
  create_all_tables()
  create_system_roles()
  create_job_roles()
  create_system_rights()
  create_main_users()