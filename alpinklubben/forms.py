from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, SelectField, DateField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from alpinklubben.models import User, Skipakke
import datetime


class RegistrationForm(FlaskForm):
    username = StringField('Brukernavn', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Passord', validators=[DataRequired()])
    confirm_password = PasswordField('Gjenta Passord', validators=[
                                     DataRequired(), EqualTo('password')])
    tos = BooleanField('Jeg har lest og godtar vilkår for bruk',
                       validators=[DataRequired()])
    submit = SubmitField('Fullfør')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'Brukernavnet er tatt, velg et annet')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Epostadressen er allerede registrert')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Passord', validators=[DataRequired()])
    remember = BooleanField('Husk meg')
    submit = SubmitField('Logg inn')


class UpdateAccountForm(FlaskForm):
    username = StringField('Brukernavn', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Oppdater Profilbilde', validators=[
                        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Oppdater profil')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'Brukernavnet er tatt, velg et annet')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'Epostadressen er allerede registrert')


class OrderHeiskortForm(FlaskForm):
    card_type = SelectField('Korttype', choices=[(c, c) for c in [
                            'Dagskort', 'Ukeskort', 'Sesongkort']])  # Heiskort.query.all() Heiskort.type Heiskort.age

    card_age = SelectField('Prisgruppe', choices=[(c, c) for c in [
        'Voksen', 'Barn']])  # Heiskort.query.all().filter()

    fromdate = DateField('Fra dato', format="%Y-%m-%d",
                         default=datetime.datetime.today())
    submit = SubmitField('Fullfør bestillingen')


class OrderSkipakkeForm(FlaskForm):
    skipakker = Skipakke.query.all()
    # Hent disse ifra databasen? hardcoded not optimal
    rent_types = ['Time', 'Dag', 'Uke']

    skipakke = SelectField('Skipakke', choices=[
                           (str(c.id), c.name) for c in skipakker])
    rent_type = SelectField('Leietype', choices=[
                            (c, c) for c in rent_types])
    rent_length = SelectField('Leielengde', choices=[
                              (str(c), str(c)) for c in range(1, 10)])
    #fromdate = DateField('Fra dato', format="%Y-%m-%d")
    fromdate = DateTimeField(
        'Fra dato', format='%Y-%m-%d %H:%M', default=datetime.datetime.today())
    submit = SubmitField('Fullfør bestillingen')
