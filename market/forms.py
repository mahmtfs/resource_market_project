from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange
from market.models import User, Item


class Registration(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8, max=20)])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('The username has already been taken. Please choose a different one.')


class Login(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    submit = SubmitField('Submit')


class ItemForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=1, max=20)])
    item_type = StringField('Type',
                            validators=[DataRequired(), Length(min=1, max=20)])
    cost = FloatField('Cost per kg ($)',
                      validators=[DataRequired(), NumberRange(min=5, max=9999)])
    volume = FloatField('Volume (kg)',
                        validators=[DataRequired(), NumberRange(min=5, max=9999)])
    description = TextAreaField('Description',
                                validators=[DataRequired(), Length(min=1, max=300)])
    submit = SubmitField('Confirm')
    delete = SubmitField('Delete Item')


class ProfileForm(FlaskForm):
    description = TextAreaField('Description',
                                validators=[DataRequired(), Length(min=1, max=300)])
    submit = SubmitField('Confirm')
    delete = SubmitField('Ban User')


class BuyForm(FlaskForm):
    volume_to_buy = FloatField('Volume To Buy (kg)',
                               validators=[DataRequired(), NumberRange(min=0, max=9999)])
    submit = SubmitField('Buy')


class BalanceForm(FlaskForm):
    deposit = FloatField('Money', validators=[DataRequired(), NumberRange(min=5, max=1000)])
    submit = SubmitField('Deposit')


class SearchForm(FlaskForm):
    query = StringField("Item's name")
    submit = SubmitField('Search')
