from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, DecimalField, SelectField, DateTimeField, TimeField, IntegerField, SelectMultipleField, DateField, FileField
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


class UpdateUser(FlaskForm):
    email = StringField('O seu email', validators=[InputRequired(), Email(message='Email invalido!')])
    password = PasswordField('A sua password atual', validators=[InputRequired(), Length(min=6, max=40, message='Escolha uma palavra passe com pelo menos 6 letras, numeros e simbolos.')])
    new_password = PasswordField('Nova password')


class UpdateUserAccount(FlaskForm):
    role = SelectField('Tipo de utilizador', id='formRoleSelect', coerce=int)
    premium = BooleanField('Conta Premium?')
    staffRole = SelectField('Posto de Staff', coerce=int)




class ServiceForm(FlaskForm):
    name = StringField('Nome do servico', validators=[InputRequired()])
    description = TextAreaField('Descricao', validators=[InputRequired()])
    price = DecimalField('Preco')



class BookingForm(FlaskForm):
    propertyType = SelectField('Tipo de Casa', choices=[('T1','T1'),('T2','T2'),('T3','T3'),('T4','T4'),('T5+','T5+'),('Escritorios','Escritorios')] ,validators=[InputRequired()])
    service = SelectField('Servico', id='form1', coerce=int, validators=[InputRequired()])
    date_from = DateField('De', format='%d-%m-%Y', validators=[InputRequired()], id='datepicker1')
    date_to = DateField('A', format='%d-%m-%Y', validators=[InputRequired()], id='datepicker2')
    time = SelectField('Hora', choices=[('5:00', '5:00'), ('5:10', '5:10'), ('5:20', '5:20'), ('5:30', '5:30'), ('5:40', '5:40'), ('5:50', '5:50'), ('6:00', '6:00'), ('6:10', '6:10'), ('6:20', '6:20'), ('6:30', '6:30'), ('6:40', '6:40'), ('6:50', '6:50'), ('7:00', '7:00'), ('7:10', '7:10'), ('7:20', '7:20'), ('7:30', '7:30'), ('7:40', '7:40'), ('7:50', '7:50'), ('8:00', '8:00'), ('8:10', '8:10'), ('8:20', '8:20'), ('8:30', '8:30'), ('8:40', '8:40'), ('8:50', '8:50'), ('9:00', '9:00'), ('9:10', '9:10'), ('9:20', '9:20'), ('9:30', '9:30'), ('9:40', '9:40'), ('9:50', '9:50'), ('10:00', '10:00'), ('10:10', '10:10'), ('10:20', '10:20'), ('10:30', '10:30'), ('10:40', '10:40'), ('10:50', '10:50'), ('11:00', '11:00'), ('11:10', '11:10'), ('11:20', '11:20'), ('11:30', '11:30'), ('11:40', '11:40'), ('11:50', '11:50'), ('12:00', '12:00'), ('12:10', '12:10'), ('12:20', '12:20'), ('12:30', '12:30'), ('12:40', '12:40'), ('12:50', '12:50'), ('13:00', '13:00'), ('13:10', '13:10'), ('13:20', '13:20'), ('13:30', '13:30'), ('13:40', '13:40'), ('13:50', '13:50'), ('14:00', '14:00'), ('14:10', '14:10'), ('14:20', '14:20'), ('14:30', '14:30'), ('14:40', '14:40'), ('14:50', '14:50'), ('15:00', '15:00'), ('15:10', '15:10'), ('15:20', '15:20'), ('15:30', '15:30'), ('15:40', '15:40'), ('15:50', '15:50'), ('16:00', '16:00'), ('16:10', '16:10'), ('16:20', '16:20'), ('16:30', '16:30'), ('16:40', '16:40'), ('16:50', '16:50'), ('17:00', '17:00'), ('17:10', '17:10'), ('17:20', '17:20'), ('17:30', '17:30'), ('17:40', '17:40'), ('17:50', '17:50'), ('18:00', '18:00'), ('18:10', '18:10'), ('18:20', '18:20'), ('18:30', '18:30'), ('18:40', '18:40'), ('18:50', '18:50'), ('19:00', '19:00'), ('19:10', '19:10'), ('19:20', '19:20'), ('19:30', '19:30'), ('19:40', '19:40'), ('19:50', '19:50'), ('20:00', '20:00'), ('20:10', '20:10'), ('20:20', '20:20'), ('20:30', '20:30'), ('20:40', '20:40'), ('20:50', '20:50'), ('21:00', '21:00'), ('21:10', '21:10'), ('21:20', '21:20'), ('21:30', '21:30'), ('21:40', '21:40'), ('21:50', '21:50'), ('22:00', '22:00'), ('22:10', '22:10'), ('22:20', '22:20'), ('22:30', '22:30'), ('22:40', '22:40'), ('22:50', '22:50'), ('23:00', '23:00'), ('23:10', '23:10'), ('23:20', '23:20'), ('23:30', '23:30'), ('23:40', '23:40'), ('23:50', '23:50'), ('24:00', '24:00'), ('24:10', '24:10'), ('24:20', '24:20'), ('24:30', '24:30'), ('24:40', '24:40'), ('24:50', '24:50')], validators=[InputRequired()])
    duration = SelectField('Quantas horas por dia necessita?', coerce=int, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)], id='durationTime' ,validators=[InputRequired()])
    address = StringField('Morada', validators=[InputRequired()])
    comments = TextAreaField('Comentarios')


class BookingNotesForm(FlaskForm):
    text = TextAreaField('Texto', validators=[InputRequired(), Length(min=5)])



class BookingUpdateForm(FlaskForm):
    service = SelectField('Servico', coerce=int)
    amount_paid = DecimalField('Nova Quantia')
    confirmed = BooleanField('Confirmado')
    completed = BooleanField('Completo')
    cancelled = BooleanField('Cancelado')
    cleaner = SelectField('Empregado/a', coerce=int)
    supervisor = SelectField('Supervisor/a', coerce=int)



class SendMessageForm(FlaskForm):
    message = TextAreaField('Mensagem:', validators=[InputRequired()])


class SearchForUserForm(FlaskForm):
    search_field = StringField('Pesquisar')



class UpdateUserProfile(FlaskForm):
    image = FileField('Imagem / Logo')
    company = StringField('Nome da empresa')
    address = StringField('Morada')
    postcode = StringField('Codigo-Postal')
    favourite_services = SelectMultipleField('Servicos Favoritos', coerce=int)
