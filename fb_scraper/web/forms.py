from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, URLField
from wtforms.validators import DataRequired, URL, Email

class LoginForm(FlaskForm):
    email    = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])

class GroupForm(FlaskForm):
    group_id = StringField("Group ID", validators=[DataRequired()])
    url      = URLField("Facebook URL", validators=[DataRequired(), URL()])
