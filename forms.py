from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length


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
