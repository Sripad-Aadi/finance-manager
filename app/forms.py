from flask_wtf import FlaskForm
from app.models import User,TransactionType
from flask_login import current_user
from wtforms import StringField,SelectField,PasswordField,BooleanField,SubmitField,DecimalField,TextAreaField,DateField
from flask_wtf.file import FileField,FileAllowed
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError,NumberRange


class RegisterForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    email=StringField('Email',validators=[Email(),DataRequired()])
    password=PasswordField('Password', validators=[DataRequired(),Length(min=6)])
    confirmPassword=PasswordField('Confirm Password', validators=[DataRequired(),Length(min=6),
                                                                  EqualTo('password','Passmord must match')])
    submit=SubmitField("Register")
    
    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("User name already exit. Proceed with another one.")
    
    def validate_email(self,email):
        user=User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Already registered with this email. Please login")

class LoginForm(FlaskForm):
    email=StringField('Email',validators=[Email(),DataRequired()])
    password=PasswordField('Password', validators=[DataRequired(),Length(min=6)])
    remember= BooleanField("Remember me")
    submit=SubmitField("Login")
    
class UpdateAccount(FlaskForm):
    username=StringField("Username",validators=[DataRequired(),Length(min=2,max=20)])
    email=StringField("Email",validators=[DataRequired(),Email()])
    picture=FileField("Update Profile Pic",validators=[FileAllowed(["jpg","png"])])
    submit=SubmitField("Update")
    
    def validate_username(self,username):
        if current_user.username!=username.data:
            user=User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("User name already exit. Proceed with another one.")
    
    def validate_email(self,email):
        if current_user.email!=email.data:
            user=User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("Already registered with this email. Please login")

class TransactionForm(FlaskForm):
    type=SelectField('Type',choices=[(t.value,t.name.title()) for t in TransactionType],
                      validators=[DataRequired()])
    amount = DecimalField(
        'Amount',
        validators=[DataRequired(), NumberRange(min=0.01, max=99999999.99)]
    )
    category = SelectField('Category', validators=[DataRequired()])
    description = TextAreaField(
        'Description',
        validators=[Length(min=0, max=500)]
    )
    date = DateField('Date', validators=[DataRequired()])
    
    def validate_date(self, field):
        from datetime import date
        if field.data > date.today():
            raise ValidationError('Transaction date cannot be in the future')

class UpdatePassword(FlaskForm):
    old_password=PasswordField('Old Password', validators=[DataRequired(),Length(min=6)])
    new_password=PasswordField('New Password', validators=[DataRequired(),Length(min=6)])
    confirm_password=PasswordField('Confirm Password', validators=[DataRequired(),Length(min=6),
                                                                  EqualTo('new_password','Passmord must match')])
    submit=SubmitField("Update")
    
class ResetRequestForm(FlaskForm):
    email=StringField('Email',validators=[Email(),DataRequired()])
    submit=SubmitField("Request Password Reset")
    
    def validate_email(self,email):
        user=User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("There is no account with that email. Please register first.")

class ResetPasswordForm(FlaskForm):
    password=PasswordField('Password', validators=[DataRequired(),Length(min=6)])
    confirmPassword=PasswordField('Confirm Password', validators=[DataRequired(),Length(min=6),
                                                                  EqualTo('password','Passmord must match')])
    submit=SubmitField("Register")
    
    
    
    
