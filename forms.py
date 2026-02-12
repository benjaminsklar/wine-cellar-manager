from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, IntegerField, FloatField,
    TextAreaField, SelectField, DateField, BooleanField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, Optional, NumberRange, ValidationError
)
from models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')


class WineForm(FlaskForm):
    # ── Wine Information ──
    name = StringField('Name', validators=[DataRequired(), Length(max=200)])
    vintage = IntegerField('Vintage', validators=[Optional(), NumberRange(min=1900, max=2030)])
    producer = StringField('Producer', validators=[DataRequired(), Length(max=200)])
    wine_type = SelectField('Type', choices=[
        ('Red', 'Red'), ('White', 'White'), ('Rosé', 'Rosé'),
        ('Sparkling', 'Sparkling'), ('Dessert', 'Dessert'), ('Fortified', 'Fortified')
    ])
    appellation = StringField('Appellation', validators=[Optional(), Length(max=200)])
    varietal1 = StringField('Varietal 1', validators=[Optional(), Length(max=100)])
    varietal2 = StringField('Varietal 2', validators=[Optional(), Length(max=100)])
    varietal3 = StringField('Varietal 3', validators=[Optional(), Length(max=100)])
    varietal4 = StringField('Varietal 4', validators=[Optional(), Length(max=100)])
    size_ml = IntegerField('Size (ml)', validators=[Optional(), NumberRange(min=1)], default=750)
    alcohol_pct = FloatField('Alcohol %', validators=[Optional(), NumberRange(min=0, max=100)])
    description = TextAreaField('Description', validators=[Optional()])

    # ── Acquisition Information ──
    acq_date = DateField('Date', validators=[Optional()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)], default=1)
    price = FloatField('Price ($)', validators=[Optional(), NumberRange(min=0)])
    acq_from = StringField('From', validators=[Optional(), Length(max=200)])
    on_order = BooleanField('On Order')
    stored = StringField('Stored', validators=[Optional(), Length(max=200)])
    acq_description = TextAreaField('Description', validators=[Optional()])

    # ── Drinking window & rating (kept for cellar tracking) ──
    drink_from = IntegerField('Drink From (Year)', validators=[Optional(), NumberRange(min=1900, max=2100)])
    drink_to = IntegerField('Drink To (Year)', validators=[Optional(), NumberRange(min=1900, max=2100)])
    rating = IntegerField('Rating (1-100)', validators=[Optional(), NumberRange(min=1, max=100)])
    status = SelectField('Status', choices=[
        ('cellar', 'In Cellar'), ('wishlist', 'Wish List'), ('consumed', 'Consumed')
    ], default='cellar')

    submit = SubmitField('Save Wine')


class TastingNoteForm(FlaskForm):
    tasting_date = DateField('Tasting Date', validators=[DataRequired()])
    appearance = StringField('Appearance', validators=[Optional(), Length(max=200)])
    nose = TextAreaField('Nose / Aroma', validators=[Optional()])
    palate = TextAreaField('Palate', validators=[Optional()])
    finish = TextAreaField('Finish', validators=[Optional()])
    overall = TextAreaField('Overall Impression', validators=[Optional()])
    score = IntegerField('Score (1-100)', validators=[Optional(), NumberRange(min=1, max=100)])
    submit = SubmitField('Save Tasting Note')


class SearchForm(FlaskForm):
    class Meta:
        csrf = False

    query = StringField('Search', validators=[Optional()])
    wine_type = SelectField('Type/Color', choices=[
        ('', 'Any Type/Color'),
        ('Red', 'red'), ('White', 'white'), ('Rosé', 'rose'),
        ('Sparkling', 'sparkling white'), ('Dessert', 'sweet white'),
        ('Fortified', 'fortified')
    ], validators=[Optional()])
    appellation = StringField('Appellation', validators=[Optional()])
    varietal = StringField('Varietal', validators=[Optional()])
    min_vintage = IntegerField('Min Vintage', validators=[Optional()])
    max_vintage = IntegerField('Max Vintage', validators=[Optional()])
    sort_by = SelectField('Sorted by', choices=[
        ('name', 'Name'), ('vintage', 'Vintage'), ('producer', 'Producer'),
        ('appellation', 'Appellation'), ('varietal', 'Varietal'),
        ('wine_type', 'Type/Color'), ('rating', 'Rating'),
        ('price', 'Price'), ('date_added', 'Date Added')
    ], default='name', validators=[Optional()])
