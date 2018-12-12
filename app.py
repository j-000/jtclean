from flask import Flask, url_for, render_template, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_login import UserMixin, login_required, current_user, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

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

# MODELS
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    surname = db.Column(db.String(30))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(85))
    role = db.Column(db.String(20))

# USER LOADER
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
  flash('Por favor entre na sua conta para aceder ao seu perfile.')
  return redirect(url_for('login'))



# FORMS
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Email invalido!')])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=40, message='Escolha uma palavra passe com pelo menos 6 letras, numeros e simbolos.')])

class RegisterForm(FlaskForm):
    name  = StringField('Nome / Empresa', validators=[InputRequired()])
    surname = StringField('Apelido (Opcional)')
    email = StringField('Email', validators=[InputRequired(), Email(message='Email invalido!')])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=40, message='Escolha uma palavra passe com pelo menos 6 letras, numeros e simbolos.')])
    password2 = PasswordField('Confirme Password', validators=[InputRequired(), Length(min=6, max=40, message='Escolha uma palavra passe com pelo menos 6 letras, numeros e simbolos.')])
    company = BooleanField('Negocio / Empresa')



# ROUTES

@app.route('/')
def index():
    return render_template('index.html')


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
              role = role)
      db.session.add(new_user)
      db.session.commit()
      flash('A sua conta foi criada com sucesso!')
      return redirect(url_for('login'))

    return render_template('registo.html', form=form)


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

    return render_template('login.html', form=form)



@app.route('/admin', methods=['GET','POST'])
@login_required
def admin():
    return render_template('admin.html')


@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    return render_template('profile.html')


@app.route('/logout')
@login_required
def logout():
  logout_user();
  return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
