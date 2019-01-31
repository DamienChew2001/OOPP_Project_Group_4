import os
import secrets
from _datetime import datetime
from PIL import Image
from flask import Flask, render_template, url_for, redirect, request, flash, session, logging,abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_mail import Message, Mail
from itsdangerous import URLSafeTimedSerializer,SignatureExpired
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed,FileField
from wtforms import StringField, SubmitField, TextAreaField, HiddenField,IntegerField,RadioField,PasswordField,BooleanField
from wtforms.fields.html5 import DateField,DateTimeField
from wtforms.validators import DataRequired, length, InputRequired,Email,Length,NumberRange,EqualTo,ValidationError
from sqlalchemy.orm import column_property

app = Flask(__name__)

app.config['SECRET_KEY'] = '35bd600b45b32b926604c408427893c7'
#Bcrypt
bcrypt = Bcrypt(app)
# Config SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

#config email

app.config.from_pyfile('emailConfig.cfg')
mail = Mail(app)
timer = URLSafeTimedSerializer("2")

@login_manager.user_loader
def load_user(user_id):
    return Teacher.query.get(int(user_id)) or Student.query.get(int(user_id)) or Alumni.query.get(int(user_id)) or Admin.query.get(int(user_id))


db.create_all()


class Events(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), length(max=20)])
    link = StringField('Link', validators=[DataRequired(), length(max=100)])
    participants = IntegerField('Number of people allowed in Event', validators=[DataRequired('Please enter a valid number.')])
    date = DateField('Closing date', validators=[DataRequired()], format="%Y-%m-%d", )
    content = TextAreaField('Main Details', validators=[DataRequired(), length(max=100)])
    picture = FileField('Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Submit')

class EventsDB(db.Model):
    __searchable__ = ['data', 'title']
    __tablename__ = 'Events'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    title = db.Column('title', db.String(), nullable=False)
    link = db.Column('link', db.String(), nullable=False)
    participants = db.Column('participants', db.String(), nullable=False)
    date = db.Column('date', db.String(), nullable=False)
    data = db.Column('data', db.String(), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="Dom.jpeg")

    def __repr__(self):
        return f"User('{self.data}', '{self.title}', '{self.image_file}', '{self.link}', '{self.participants}', '{self.date}')"

class Eventsearch(FlaskForm):
    name = HiddenField(validators=[InputRequired('No Search')], id="input")




class AdvancedSearchForm(FlaskForm):
    category=HiddenField(validators=[InputRequired("NO CATEGORY")],id="category")
    table=HiddenField(validators=[InputRequired("NO TABLE")],id="table")
    input=HiddenField(validators=[InputRequired("NO INPUT")],id="input")
    by=HiddenField(id="by")

class PostForm(FlaskForm):
    title = StringField('Title of Review', validators=[DataRequired()], render_kw={"placeholder": "Write the title of the review here"})
    content = TextAreaField('General Review', validators=[DataRequired()], render_kw={"placeholder": "What did you like or dislike about the school?"})
    content2 = TextAreaField('Facilities', render_kw={"placeholder": "Describe the facilities at the school (optional)"})
    content3 = TextAreaField('Staff', render_kw={"placeholder": "Describe the staff at the school (optional)"})
    content4 = TextAreaField('Advice to school', render_kw={"placeholder": "Give advice to the school management (optional)"})
    rating = RadioField('Overall Rating of school', validators=[DataRequired()], choices=[('5', ''), ('4', ''), ('3', ''), ('2', ''), ('1', '')], id='str',default="")
    submit = SubmitField('Review')

class Eventsearch(FlaskForm):
    name = HiddenField(validators=[InputRequired('No Search')], id="input")

class Name(FlaskForm):
    name = StringField('Name of School', validators=[DataRequired()])
    address = StringField(' Address of School', validators=[DataRequired()])
    zone = RadioField("Zone",choices=[("north","North"),("south","South"),("east","East"),("west","West")],validators=[DataRequired()])
    contact = StringField('Contact Number of School', validators=[DataRequired()])
    year = IntegerField('Year of Establishment', validators=[DataRequired()])
    website = StringField('URL for School Website', validators=[DataRequired()])
    type=RadioField("Type of School",choices=[("PSLE","Secondary"),("L1R4","Polytechnic/Centralises Institute"),("L1R5","Junior College")],validators=[DataRequired()])
    Adscore=IntegerField("Admission Score of School",validators=[DataRequired()])
    achievement = TextAreaField("Enter School's Academic Achievement", validators=[DataRequired()])
    achievement_1 = TextAreaField("Enter School's Non-Academic Achievement", validators=[DataRequired()])
    niche = StringField("Enter School's Niche area", validators=[DataRequired()])
    motto = StringField("Enter School's Motto", [DataRequired()])
    submit = SubmitField('Add')


class Choice(FlaskForm):
    submit = SubmitField('Accept')

class passwordForm(FlaskForm):
    password=PasswordField('Enter new Password',validators=[DataRequired("Password cannot be empty")])
    submit=SubmitField("Change Password")

class EmailForm(FlaskForm):
    category=RadioField('Account type:',choices=[('student','student'),('teacher','teacher'),('alumni','alumni')])
    email=StringField('Enter Email',validators=[DataRequired("NO Input"),Email("Invalid email")])
    submit=SubmitField('Send Email')

class RegFormTeacher(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=1, max=25)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=25)])
    school = StringField('School/Institute', validators=[DataRequired(), Length(min=5, max=100)])
    faculty = StringField("Faculty",validators=[DataRequired()])
    awards = TextAreaField('Awards/Short Description', render_kw={"rows":10, "cols":12})
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=10, max=99, message="Not a valid input")])
    email = StringField('School Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = Student.query.filter_by(email=email.data).first()
        user1 = Teacher.query.filter_by(email=email.data).first()
        user2 = Alumni.query.filter_by(email=email.data).first()
        user3 = Admin.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one')
        elif user1:
            raise ValidationError('That email is taken. Please choose a different one')
        elif user2:
            raise ValidationError('That email is taken. Please choose a different one')
        elif user3:
            raise ValidationError('That email is taken. Please choose a different one')

class RegFormStudent(FlaskForm):
        username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
        school = StringField('School/Institute', validators=[DataRequired(), Length(min=5, max=100)])
        email = StringField('School Email', validators=[DataRequired(), Email()])
        password = PasswordField('Password', validators=[DataRequired()])
        confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
        submit = SubmitField('Sign Up')

        def validate_username2(self, username):
            user = Student.query.filter_by(username=username.data).first()
            user2 = Alumni.query.filter_by(username=username.data).first()
            user3 = Admin.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one')
            elif user2:
                raise ValidationError('That username is taken. Please choose a different one')
            elif user3:
                raise ValidationError('That username is taken. Please choose a different one')

        def validate_email2(self, email):
            user = Student.query.filter_by(email=email.data).first()
            user1 = Teacher.query.filter_by(email=email.data).first()
            user2 = Alumni.query.filter_by(email=email.data).first()
            user3 = Admin.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one')
            elif user1:
                raise ValidationError('That email is taken. Please choose a different one')
            elif user2:
                raise ValidationError('That email is taken. Please choose a different one')
            elif user3:
                raise ValidationError('That email is taken. Please choose a different one')


class RegFormAlumni(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    school = StringField('School/Institute', validators=[DataRequired(), Length(min=5, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username3(self, username):
        user = Student.query.filter_by(username=username.data).first()
        user2 = Alumni.query.filter_by(username=username.data).first()
        user3 = Admin.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one')
        elif user2:
            raise ValidationError('That username is taken. Please choose a different one')
        elif user3:
            raise ValidationError('That username is taken. Please choose a different one')

    def validate_email3(self, email):
        user = Student.query.filter_by(email=email.data).first()
        user1 = Teacher.query.filter_by(email=email.data).first()
        user2 = Alumni.query.filter_by(email=email.data).first()
        user3 = Admin.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one')
        elif user1:
            raise ValidationError('That email is taken. Please choose a different one')
        elif user2:
            raise ValidationError('That email is taken. Please choose a different one')
        elif user3:
            raise ValidationError('That email is taken. Please choose a different one')


class RegFormAdmin(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    admincode = StringField('Admin Code', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username4(self, username):
        user = Student.query.filter_by(username=username.data).first()
        user2 = Alumni.query.filter_by(username=username.data).first()
        user3 = Admin.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one')
        elif user2:
            raise ValidationError('That username is taken. Please choose a different one')
        elif user3:
            raise ValidationError('That username is taken. Please choose a different one')

    def validate_email4(self, email):
        user = Student.query.filter_by(email=email.data).first()
        user1 = Teacher.query.filter_by(email=email.data).first()
        user2 = Alumni.query.filter_by(email=email.data).first()
        user3 = Admin.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one')
        elif user1:
            raise ValidationError('That email is taken. Please choose a different one')
        elif user2:
            raise ValidationError('That email is taken. Please choose a different one')
        elif user3:
            raise ValidationError('That email is taken. Please choose a different one')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateStudentAcc(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    school = StringField('School/Institute', validators=[DataRequired(), Length(min=5, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')


    def validate_username2(self, username):
        if username.data != current_user.username:
            user = Student.query.filter_by(username=username.data).first()
            user2 = Alumni.query.filter_by(username=username.data).first()
            user3 = Admin.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one')
            elif user2:
                raise ValidationError('That username is taken. Please choose a different one')
            elif user3:
                raise ValidationError('That username is taken. Please choose a different one')

    def validate_email2(self, email):
        if email.data != current_user.email:
            user = Student.query.filter_by(email=email.data).first()
            user1 = Teacher.query.filter_by(email=email.data).first()
            user2 = Alumni.query.filter_by(email=email.data).first()
            user3 = Admin.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one')
            elif user1:
                raise ValidationError('That email is taken. Please choose a different one')
            elif user2:
                raise ValidationError('That email is taken. Please choose a different one')
            elif user3:
                raise ValidationError('That email is taken. Please choose a different one')

class UpdateTeacherAcc(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=1, max=25)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=25)])
    school = StringField('School/Institute', validators=[DataRequired(), Length(min=5, max=100)])
    faculty = StringField("Faculty", validators=[DataRequired()])
    awards = TextAreaField('Awards/Short Description', render_kw={"rows": 10, "cols": 12})
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=15, max=100, message="Not a Valid Range")])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Student.query.filter_by(email=email.data).first()
            user1 = Teacher.query.filter_by(email=email.data).first()
            user2 = Alumni.query.filter_by(email=email.data).first()
            user3 = Admin.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one')
            elif user1:
                raise ValidationError('That email is taken. Please choose a different one')
            elif user2:
                raise ValidationError('That email is taken. Please choose a different one')
            elif user3:
                raise ValidationError('That email is taken. Please choose a different one')

class UpdateAlumniAcc(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    school = StringField('School/Institute', validators=[DataRequired(), Length(min=5, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')


    def validate_username3(self, username):
        if username.data != current_user.username:
            user = Student.query.filter_by(username=username.data).first()
            user2 = Alumni.query.filter_by(username=username.data).first()
            user3 = Admin.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one')
            elif user2:
                raise ValidationError('That username is taken. Please choose a different one')
            elif user3:
                raise ValidationError('That username is taken. Please choose a different one')

    def validate_email3(self, email):
        if email.data != current_user.email:
            user = Student.query.filter_by(email=email.data).first()
            user1 = Teacher.query.filter_by(email=email.data).first()
            user2 = Alumni.query.filter_by(email=email.data).first()
            user3 = Admin.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one')
            elif user1:
                raise ValidationError('That email is taken. Please choose a different one')
            elif user2:
                raise ValidationError('That email is taken. Please choose a different one')
            elif user3:
                raise ValidationError('That email is taken. Please choose a different one')

class UpdateAdminAcc(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=15, max=100, message="Not a Valid Range")])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')


    def validate_username4(self, username):
        if username.data != current_user.username:
            user = Student.query.filter_by(username=username.data).first()
            user2 = Alumni.query.filter_by(username=username.data).first()
            user3 = Admin.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one')
            elif user2:
                raise ValidationError('That username is taken. Please choose a different one')
            elif user3:
                raise ValidationError('That username is taken. Please choose a different one')

    def validate_email4(self, email):
        if email.data != current_user.email:
            user = Student.query.filter_by(email=email.data).first()
            user1 = Teacher.query.filter_by(email=email.data).first()
            user2 = Alumni.query.filter_by(email=email.data).first()
            user3 = Admin.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one')
            elif user1:
                raise ValidationError('That email is taken. Please choose a different one')
            elif user2:
                raise ValidationError('That email is taken. Please choose a different one')
            elif user3:
                raise ValidationError('That email is taken. Please choose a different one')






def save_picture2(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img', picture_fn)
    output_size = (1920, 1080)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

class Post(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    content2 = db.Column(db.Text)
    content3 = db.Column(db.Text)
    content4 = db.Column(db.Text)
    rating = db.Column(db.Integer)
    author = db.Column(db.Integer, nullable=False)#db.foreignkey

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Teacher(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(25), nullable=False)
    lastname = db.Column(db.String(25),  nullable=False)
    username = column_property(firstname+" "+lastname)
    faculty = db.Column(db.String(100), nullable=False)
    school = db.Column(db.String(100), nullable=False)
    awards = db.Column(db.Text(200), nullable=False)
    age = db.Column(db.String(2), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    true=db.Column(db.String(60),nullable=False)

    def __repr__(self):
        return f"User('{self.firstname}', '{self.lastname}', '{self.school}', '{self.age}', '{self.email}', '{self.awards}', '{self.image_file}')"

class Student(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    school = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    true=db.Column(db.String(60),nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.school}', '{self.email}', '{self.image_file}')"

class Alumni(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    school = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    true=db.Column(db.String(60),nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.school}', '{self.email}', '{self.image_file}')"

class Admin(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    true=db.Column(db.String(60),nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class School(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(200))
    address = db.Column(db.String(200))
    zone=db.Column(db.String(200))
    contact = db.Column(db.String(200))
    website = db.Column(db.String(200))
    achievement = db.Column(db.String(1000))
    achievement_1 = db.Column(db.String(1000))
    niche = db.Column(db.String(200))
    motto = db.Column(db.String(200))
    year = db.Column(db.String(10))
    PSLE = db.Column(db.Integer)
    L1R5 = db.Column(db.Integer)
    L1R4 = db.Column(db.Integer)
    type= db.Column(db.String(100))
    def __repr__(self):
        return f"School('self.name')"


class ConfirmedSchool(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(200))
    address = db.Column(db.String(200))
    zone=db.Column(db.String(200))
    contact = db.Column(db.String(200))
    website = db.Column(db.String(200))
    achievement = db.Column(db.String(1000))
    achievement_1 = db.Column(db.String(1000))
    niche = db.Column(db.String(200))
    motto = db.Column(db.String(200))
    year = db.Column(db.String(10))
    PSLE = db.Column(db.Integer)
    L1R5 = db.Column(db.Integer)
    L1R4 = db.Column(db.Integer)
    def __repr__(self):
        return f"confirmed('self.name')"

db.create_all()

@app.route('/', methods=("GET","POST"))
def homepage():
    send=None
    form = Eventsearch()
    advanced_search_link = url_for('advanced_search')
    if request.method == "POST":
        if form.validate_on_submit():
            input = form.name.data
            database = db.session.query(ConfirmedSchool.name).all()
            sortlist = {}
            for k in database:
                for u in k:
                    count = u.count(input)
                    if not count == 0:
                        sortlist[u] = count
            search = []
            for w in sorted(sortlist, key=sortlist.get, reverse=True):
                search.append(w)
            send=[]
            for w in search:
                s=db.session.query(ConfirmedSchool).filter(ConfirmedSchool.name==w).first()
                send.append(s)
    return render_template('homepage.html',form=form,search=send,advanced_search=advanced_search_link)

@app.route('/homestudent', methods=("GET","POST"))
def studenthome():
    send = None
    form = Eventsearch()
    advanced_search_link = url_for('advanced_search')
    if request.method == "POST":
        if form.validate_on_submit():
            input = form.name.data
            database = db.session.query(ConfirmedSchool.name).all()
            sortlist = {}
            for k in database:
                for u in k:
                    count = u.count(input)
                    if not count == 0:
                        sortlist[u] = count
            search = []
            for w in sorted(sortlist, key=sortlist.get, reverse=True):
                search.append(w)
            send = []
            for w in search:
                    s = db.session.query(ConfirmedSchool).filter(ConfirmedSchool.name == w).first()
                    send.append(s)
    return render_template('indexstudent.html',form=form,search=send,advanced_search=advanced_search_link)

@app.route('/hometeacher', methods=("GET","POST"))
def teacherhome():
    send = None
    form = Eventsearch()
    advanced_search_link = url_for('advanced_search')
    if request.method == "POST":
        if form.validate_on_submit():
            input = form.name.data
            database = db.session.query(ConfirmedSchool.name).all()
            sortlist = {}
            for k in database:
                for u in k:
                    count = u.count(input)
                    if not count == 0:
                        sortlist[u] = count
            search = []
            for w in sorted(sortlist, key=sortlist.get, reverse=True):
                search.append(w)
            send = []
            for w in search:
                s = db.session.query(ConfirmedSchool).filter(ConfirmedSchool.name == w).first()
                send.append(s)
    return render_template('indexteacher.html',form=form,search=send,advanced_search=advanced_search_link)

@app.route('/homealumni', methods=("GET","POST"))
def alumnihome():
    send= None
    form = Eventsearch()
    advanced_search_link = url_for('advanced_search')
    if request.method == "POST":
        if form.validate_on_submit():
            input = form.name.data
            database = db.session.query(ConfirmedSchool.name).all()
            sortlist = {}
            for k in database:
                for u in k:
                    count = u.count(input)
                    if not count == 0:
                        sortlist[u] = count
            search = []
            for w in sorted(sortlist, key=sortlist.get, reverse=True):
                search.append(w)
            send = []
            for w in search:
                    s = db.session.query(ConfirmedSchool).filter(ConfirmedSchool.name == w).first()
                    send.append(s)
    return render_template('indexalumni.html',form=form,search=send,advanced_search=advanced_search_link)

@app.route('/homeadmin', methods=("GET","POST"))
def adminhome():
    send = None
    form = Eventsearch()
    advanced_search_link = url_for('advanced_search')
    if request.method == "POST":
        if form.validate_on_submit():
            input = form.name.data
            database = db.session.query(ConfirmedSchool.name).all()
            sortlist = {}
            for k in database:
                for u in k:
                    count = u.count(input)
                    if not count == 0:
                        sortlist[u] = count
            search = []
            for w in sorted(sortlist, key=sortlist.get, reverse=True):
                search.append(w)
            send = []
            for w in search:
                s = db.session.query(ConfirmedSchool).filter(ConfirmedSchool.name == w).first()
                send.append(s)
    return render_template('indexadmin.html',form=form,search=send,advanced_search=advanced_search_link)

@app.route('/AdvancedSearch', methods=("GET","POST"))
def advanced_search():
    message=None
    table=None
    displaylist=None
    form=AdvancedSearchForm()
    if request.method=="POST":
        if form.validate_on_submit():
            category=form.category.data
            table=form.table.data
            input=form.input.data
            if table=="schools":
                if category=="name":
                    database=db.session.query(ConfirmedSchool.name).all()
                elif category == "zone":
                    database=db.session.query(ConfirmedSchool.zone).all()
                elif category == "address":
                    database=db.session.query(ConfirmedSchool.address).all()
                elif category == "L1R4" or category=="L1R5" or category=="PSLE":
                    check=0
                    by=form.by.data
                    if by=="range":
                         range=input.split("-")
                         if len(range)!=2:
                             message="invalid range"
                             check=1
                         elif range[0].isdigit()==False or range[1].isdigit==False:
                             message="Range is not a number"
                             check=1
                    elif by=="min":
                        if input.isdigit()==False:
                            message="min is not a number"
                            check=1
                    if check==0:
                        if by=="range":
                            range=input.split("-")
                            range.sort()
                            _min =range[0]
                            _max =range[1]
                            if category=="L1R4":
                                database=db.session.query(ConfirmedSchool).filter(ConfirmedSchool.L1R4>=_min,ConfirmedSchool.L1R4<=_max).order_by(ConfirmedSchool.L1R4.asc()).all()
                            elif category == "L1R5":
                                database=db.session.query(ConfirmedSchool).filter(ConfirmedSchool.L1R5>=_min,ConfirmedSchool.L1R4<=_max).order_by(ConfirmedSchool.L1R5.asc()).all()
                            elif category=="PSLE":
                                database=db.session.query(ConfirmedSchool).filter(ConfirmedSchool.PSLE>=_min,ConfirmedSchool.PSLE<=_max).order_by(ConfirmedSchool.PSLE.desc()).all()
                        elif by=="min":
                            _min=input
                            if category=="L1R4":
                                database=db.session.query(ConfirmedSchool).filter(ConfirmedSchool.L1R4>=_min).order_by(ConfirmedSchool.L1R4.asc()).all()
                            elif category == "L1R5":
                                database=db.session.query(ConfirmedSchool).filter(ConfirmedSchool.L1R5>=_min).order_by(ConfirmedSchool.L1R5.asc()).all()
                            elif category=="PSLE":
                                database=db.session.query(ConfirmedSchool).filter(ConfirmedSchool.PSLE>=_min).order_by(ConfirmedSchool.PSLE.desc()).all()
                    else:
                        database=""
                else:
                    message="Invalid schools category"
                    database=""
            elif table=="teachers":
                if category=="name":
                    database=db.session.query(Teacher.username).all()
                elif category=="faculty":
                    database=db.session.query(Teacher.faculty).all()
                elif category=="school":
                    database=db.session.query(Teacher.school).all()
                else:
                    message="Invalid teachers category"
                    database=""
            else:
                message="table value invalid"
                database=""
            if database!="":
                if database==[]:
                    message="NO results"
                else:
                    datalist=[]
                    sortlist={}
                    for k in database:
                        if category=="L1R5" or category=="L1R4" or category=="PSLE":
                            entry={}
                            entry["name"]=k.name
                            entry["zone"]=k.zone
                            entry["address"]=k.address
                            entry["link"]="http://127.0.0.1:5000/DisplaySchool/"+k.name
                            if category=="L1R5":
                                entry["adscore"]=k.L1R5
                            elif category=="L1R4":
                                entry["adscore"]=k.L1R4
                            elif category=="PSLE":
                                entry["adscore"]=k.PSLE
                            else:
                                entry["adscore"]="error"
                            datalist.append(entry)
                        else:
                            for u in k:
                                count=u.count(input)
                                if not count==0:
                                    sortlist[u]=count
                    if len(sortlist)==0:
                        table=category
                        displaylist=datalist
                    elif len(datalist)==0:
                        displaylist=[]
                        classlist=[]
                        search=[]
                        for w in sorted(sortlist,key=sortlist.get,reverse=True):
                            search.append(w)
                        for query in search:
                            if table=="schools":
                                if category=="name":
                                    object=db.session.query(ConfirmedSchool).filter(ConfirmedSchool.name==query)
                                    classlist.append(object)
                                elif category=="zone":
                                    object = db.session.query(ConfirmedSchool).filter(ConfirmedSchool.zone == query)
                                    classlist.append(object)
                                elif category == "address":
                                    object = db.session.query(ConfirmedSchool).filter(ConfirmedSchool.address == query)
                                    classlist.append(object)
                            elif table=="teachers":
                                if category == "name":
                                    object = db.session.query(Teacher).filter(Teacher.username == query)
                                    classlist.append(object)
                                elif category == "faculty":
                                    object = db.session.query(Teacher).filter(Teacher.faculty == query)
                                    classlist.append(object)
                                elif category == "school":
                                    object = db.session.query(Teacher).filter(Teacher.school == query)
                                    classlist.append(object)
                        for dog in classlist:
                            for k in dog:
                                if table=="schools":
                                    entry={}
                                    entry["name"]=k.name
                                    entry["zone"]=k.zone
                                    entry["address"]=k.address
                                    entry["link"]="/directory/"+str(k.id)
                                    displaylist.append(entry)
                                elif table=="teachers":
                                    entry={}
                                    entry["name"]=k.username
                                    entry["faculty"]=k.faculty
                                    entry["school"]=k.school
                                    entry["link"]="/AdvancedSearch/Teachers/"+k.username
                                    displaylist.append(entry)
            if displaylist==[]:
                message="Empty table"
        else:
            message="Validation failed"
    return render_template("Advanced_Search.html",form=form,message=message,table=displaylist,category=table)

@app.route('/events', methods=("GET","POST"))
def events():
    log=1
    search=None
    events = EventsDB.query.all()
    form = Eventsearch(request.form)
    if request.method == 'POST':
            input=form.name.data
            database=db.session.query(EventsDB.title).all()
            sortlist={}
            for k in database:
                for u in k:
                    count=u.count(input)
                    if not count==0:
                        sortlist[u]=count
            search=[]
            for w in sorted(sortlist,key=sortlist.get,reverse=True):
                search.append(w)
            events=[]
            for s in search:
                events.append(db.session.query(EventsDB).filter(EventsDB.title == s).first())

    return render_template('events.html', events=events, title='Events', form=form,search=search)

@app.route('/events/new', methods=['GET','POST'])
@login_required
def new_event():
    form = Events()
    if form.validate_on_submit():
        post = EventsDB(title=form.title.data, data=form.content.data, link=form.link.data, participants=form.participants.data, date=form.date.data)
        if form.picture.data:
            picture_file = save_picture2(form.picture.data)
            post.image_file = picture_file
        db.session.add(post)
        db.session.commit()
        flash('Event created!', 'success')
        return redirect(url_for('events'))
    image_file = url_for('static', filename='img/' + EventsDB.image_file)
    return render_template('create_events.html', title='New Event', form=form, legend='New Event', image_file=image_file)

@app.route('/events/<int:eventpage_id>')
def eventpage(eventpage_id):
    eventpage = EventsDB.query.get_or_404(eventpage_id)
    return render_template('eventpage.html', title=eventpage.title, eventpage=eventpage)

@app.route('/events/<int:eventpage_id>/update', methods=['GET','POST'])
@login_required
def update_event(eventpage_id):
    eventpage = EventsDB.query.get_or_404(eventpage_id)
    form = Events()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture2(form.picture.data)
            eventpage.image_file = picture_file
        eventpage.title = form.title.data
        eventpage.link = form.link.data
        eventpage.participants = form.participants.data
        eventpage.date = form.date.data
        eventpage.data = form.content.data
        db.session.commit()
        flash('Your Event has been updated!', 'success')
        return redirect(url_for('events'))
    elif request.method == 'GET':
        form.title.data = eventpage.title
        form.link.data = eventpage.link
        form.participants.data = eventpage.participants
        form.date.format = eventpage.date
        form.content.data = eventpage.data
    image_file = url_for('static', filename='img/' + EventsDB.image_file)
    return render_template('create_events.html', title='Edit Event', form=form, legend='Edit Event', image_file=image_file)

@app.route('/events/<int:eventpage_id>/delete', methods=['GET','POST'])
def delete_event(eventpage_id):
    eventpage = EventsDB.query.get_or_404(eventpage_id)
    db.session.delete(eventpage)
    db.session.commit()
    flash('Your Event has been deleted!', 'success')
    return redirect(url_for('events'))


@app.route('/preregister')
def preregister():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = RegFormStudent()
    return render_template('preregister.html', form=form)

@app.route('/registerstudent', methods=['GET', 'POST'])
def student_register():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = RegFormStudent()
    if form.validate_on_submit():
        student = Student(true="",username=form.username.data, school=form.school.data, email=form.email.data, password=form.password.data)
        db.session.add(student)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('student_register.html', title='Student Register', form=form)

@app.route('/registerteacher', methods=['GET', 'POST'])
def teacher_register():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = RegFormTeacher()
    if form.validate_on_submit():
        teacher = Teacher(faculty=form.faculty.data, true="", email=form.email.data, password=form.password.data, age=form.age.data, firstname=form.firstname.data, lastname=form.lastname.data, awards=form.awards.data, school=form.school.data)
        db.session.add(teacher)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('teacher_register.html', title='Teacher Register', form=form)

@app.route('/registeralumni', methods=['GET', 'POST'])
def alumni_register():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = RegFormAlumni()
    if form.validate_on_submit():
        alumni = Alumni(true="",username=form.username.data, email=form.email.data, password=form.password.data, school=form.school.data)
        db.session.add(alumni)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('alumni_register.html', title='Alumni Register', form=form)

@app.route('/registeradmin', methods=['GET', 'POST'])
def admin_register():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = RegFormAdmin()
    if form.validate_on_submit():
        if form.admincode.data != "admin4life":
            flash('Wrong Code', 'danger')
        else:
            admin = Admin(true="",username=form.username.data, email=form.email.data, password=form.password.data)
            db.session.add(admin)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
    return render_template('admin_register.html', title='Admin Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    #if current_user.is_authenticated:
        #return redirect(url_for('homepage'))
    form = LoginForm()
    if form.validate_on_submit():
        if Student.query.filter_by(email=form.email.data).first():
            if Student.query.filter_by(password=form.password.data).first() == None:
                flash('Invalid Password', 'danger')
                return redirect(url_for('login'))
            else:
                user = Student.query.filter_by(email=form.email.data).first()
                if not user.true=="":
                    flash('Reset Password/Verify email','Account Locked')
                    return redirect(url_for('login'))
                else:
                    login_user(user, remember=form.remember.data)
                    #causes a bug that leaves the user using non logged in UI
                    #next_page = request.args.get('next')
                    #return redirect(next_page) if next_page else
                    return redirect(url_for('studenthome'))
        elif Teacher.query.filter_by(email=form.email.data).first():
            if Teacher.query.filter_by(password=form.password.data).first() == None:
                flash('Invalid Password', 'danger')
                return redirect(url_for('login'))
            else:
                user = Teacher.query.filter_by(email=form.email.data).first()
                if not user.true=="":
                    flash('Reset Password/Verify email','Account Locked')
                    return redirect(url_for('login'))
                else:
                    login_user(user, remember=form.remember.data)
                    #next_page = request.args.get('next')
                    #return redirect(next_page) if next_page else
                    return redirect(url_for('teacherhome'))
        elif Alumni.query.filter_by(email=form.email.data).first():
            if Alumni.query.filter_by(password=form.password.data).first() == None:
                flash('Invalid Password', 'danger')
                return redirect(url_for('login'))
            else:
                user = Alumni.query.filter_by(email=form.email.data).first()
                if not user.true=="":
                    flash('Reset Password/Verify email','Account Locked')
                    return redirect(url_for('login'))
                else:
                    login_user(user, remember=form.remember.data)
                    #next_page = request.args.get('next')
                    #return redirect(next_page) if next_page else
                    return redirect(url_for('alumnihome'))
        elif Admin.query.filter_by(email=form.email.data).first():
            if Admin.query.filter_by(password=form.password.data).first() == None:
                flash('Invalid Password', 'danger')
                return redirect(url_for('login'))
            else:
                user = Admin.query.filter_by(email=form.email.data).first()
                if not user.true=="":
                    flash('Reset Password/Verify email','Account Locked')
                    return redirect(url_for('login'))
                else:
                    login_user(user, remember=form.remember.data)
                    #next_page = request.args.get('next')
                    #return redirect(next_page) if next_page else \
                    return redirect(url_for('adminhome'))
        else:
            flash('Invalid Email', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', title='login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('homepage'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img/profile_pics', picture_fn)
    output_size = (250, 400)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/studentaccount", methods=['GET', 'POST'])
@login_required
def student_acc():
    form = UpdateStudentAcc()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.school = form.school.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('student_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.school.data = current_user.school
    image_file = url_for('static', filename='img/profile_pics/' + current_user.image_file)
    return render_template('student_acc.html', title='Account', image_file=image_file, form=form)

@app.route("/teacheraccount", methods=['GET', 'POST'])
@login_required
def teacher_acc():
    form = UpdateTeacherAcc()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.faculty = form.faculty.data
        current_user.email = form.email.data
        current_user.age = form.age.data
        current_user.awards = form.awards.data
        current_user.school = form.school.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('teacher_profile'))
    elif request.method == 'GET':
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.email.data = current_user.email
        form.age.data = current_user.age
        form.awards.data = current_user.awards
        form.school.data = current_user.school
        form.faculty.data = current_user.faculty
    image_file = url_for('static', filename='img/profile_pics/' + current_user.image_file)
    return render_template('teacher_acc.html', title='Account', image_file=image_file, form=form)

@app.route("/alumniaccount", methods=['GET', 'POST'])
@login_required
def alumni_acc():
    form = UpdateAlumniAcc()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.school = form.school.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('alumni_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.school.data = current_user.school
    image_file = url_for('static', filename='img/profile_pics/' + current_user.image_file)
    return render_template('alumni_acc.html', title='Account', image_file=image_file, form=form)

@app.route("/adminaccount", methods=['GET', 'POST'])
@login_required
def admin_acc():
    form = UpdateAdminAcc()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('admin_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='img/profile_pics/' + current_user.image_file)
    return render_template('admin_acc.html', title='Account', image_file=image_file, form=form)

@app.route("/studentprofile", methods=['GET', 'POST'])
@login_required
def student_profile():
    form = UpdateStudentAcc()
    image_file = url_for('static', filename='img/profile_pics/' + current_user.image_file)
    return render_template('student_profile.html', title='Account', image_file=image_file, form=form)

@app.route("/teacherprofile", methods=['GET', 'POST'])
@login_required
def teacher_profile():
    form = UpdateTeacherAcc()
    image_file = url_for('static', filename='img/profile_pics/' + current_user.image_file)
    return render_template('teacher_profile.html', title='Account', image_file=image_file, form=form)

@app.route("/alumniprofile", methods=['GET', 'POST'])
@login_required
def alumni_profile():
    form = UpdateAlumniAcc()
    image_file = url_for('static', filename='img/profile_pics/' + current_user.image_file)
    return render_template('alumni_profile.html', title='Account', image_file=image_file, form=form)

@app.route("/adminprofile", methods=['GET', 'POST'])
@login_required
def admin_profile():
    form = UpdateAdminAcc()
    image_file = url_for('static', filename='img/profile_pics/' + current_user.image_file)
    return render_template('admin_profile.html', title='Account', image_file=image_file, form=form)

@app.route("/Forgot",methods=['GET','POST'])
def forgot():
    message=None
    form= EmailForm()
    if form.validate_on_submit():
        user=None
        email=request.form['email']
        category=request.form['category']
        if category=="student":
            user = Student.query.filter_by(email=email).first()
        elif category=="teacher":
            user=Teacher.query.filter_by(email=email).first()
        elif category=="alumni":
            user=Alumni.query.filter_by(email=email).first()
        if user!=None:
            token = timer.dumps(email, salt='email-confirm')
            msg = Message('Password reset', sender='damienchew2001@gmail.com', recipients=[form.email.data])
            link = url_for('Change_Password',category=category,token=token, external=True)
            msg.body = "your link is 127.0.0.1:5000{}".format(link)
            mail.send(msg)
            # Should send an alert for feedback
            user.true=token
            db.session.commit()
            message='The email you entered is {}.'.format(email)
        else:
            message="Email does not match with any known user."
    return render_template('Forgot_Password.html', message=message, form=form)

@app.route('/Forgot/Change/<category>/<token>',methods=['GET','POST'])
def Change_Password(token,category):
    message = None
    check = 0
    form1 = passwordForm(prefix="form1")
    form2 = EmailForm(prefix="form2")
    try:
        email = timer.loads(token, salt='email-confirm', max_age=100)
    except SignatureExpired:
        check = 1
    finally:
        if request.method=='POST':
            user=None
            if check==0:
                if request.form['form'] == 'password':
                    if form1.validate_on_submit():
                        if category=="student":
                            user=Student.query.filter_by(true=token).first()
                        elif category=="teacher":
                            user=Teacher.query.filter_by(true=token).first()
                        elif category=="alumni":
                            user=Alumni.query.filter_by(true=token).first()
                        user.true = ""
                        user.password = form1.password.data
                        db.session.commit()
                        return redirect(url_for('login'))
            elif check==1:
                if request.form['form'] == 'email':
                    if not form2.email.data=="":
                        email = form2.email.data
                        if category=="student":
                            user=Student.query.filter_by(email=email).first()
                        elif category=="teacher":
                            user=Teacher.query.filter_by(email=email).first()
                        elif category=="alumni":
                            user=Alumni.query.filter_by(email=email).first()
                        if user != None:
                            token = timer.dumps(email, salt='email-confirm')
                            msg = Message('Password reset', sender='damienchew2001@gmail.com', recipients=[form2.email.data])
                            link = url_for('Change_Password',category=category ,token=token, external=True)
                            msg.body = "your link is 127.0.0.1:5000{}".format(link)
                            mail.send(msg)
                            user.true = token
                            db.session.commit()
                            message = 'The email you entered is {}.'.format(email)
                        else:
                            message = "Email does not match with any known user"
    return render_template("Change_Password.html", expired=int(check), message=message, form1=form1, form2=form2)

@app.route('/directory')
@login_required
def directory():
    schools = ConfirmedSchool.query.all()
    waits = School.query.all()
    return render_template('poly.html', schools=schools, waits=waits)


@app.route('/directory/new', methods=['GET', 'POST'])
@login_required
def new_directory():
    form = Name()
    if form.validate_on_submit():
        if  db.session.query(ConfirmedSchool).filter(ConfirmedSchool.name==form.name.data).first()==None:
            directory_1 = School(name=form.name.data, address=form.address.data, contact=form.contact.data,
                             year=form.year.data, website=form.website.data, achievement=form.achievement.data,
                             achievement_1=form.achievement_1.data, niche=form.niche.data, motto=form.motto.data,
                             zone=form.zone.data,type=form.type.data)
            if form.type.data=="PSLE":
                directory_1.PSLE=form.Adscore.data
            elif form.type.data=="L1R4":
                directory_1.L1R4=form.Adscore.data
            elif form.type.data=="L1R5":
                directory_1.L1R5=form.Adscore.data
            db.session.add(directory_1)
            db.session.commit()
            flash(f'{form.name.data} has been added, wait for admin to accept!', 'success')
            return redirect(url_for('directory'))
        else:
            flash(f'{form.name.data} has already been created.')
            return redirect(url_for('directory'))
    return render_template('create_new.html', title='new directory', form=form, legend='Add Your School')


@app.route('/directory/<int:school_id>')
def directory_school_name(school_id):
    posts = Post.query.all()
    schools = {}
    Selectedschool = db.session.query(ConfirmedSchool).filter(ConfirmedSchool.id == school_id).first()
    schools[0] = Selectedschool
    return render_template("review.html", posts=posts, schools=schools, schoolvalue=0)


@app.route('/directoryadmin/<int:school_id>', methods=["GET", "POST"])
@login_required
def admin_school(school_id):
    form = Choice()
    Adscore=None
    school = School.query.get_or_404(school_id)
    if school.type=="L1R4":
        Adscore=school.L1R4
    elif school.type=="PSLE":
        Adscore=school.PSLE
    elif school.type=="L1R5":
        Adscore=school.L1R5
    if form.validate_on_submit():
        return redirect(url_for(add))
    return render_template('admin_school_website.html', school=school, form=form,school_Adscore=Adscore)


@app.route('/directoryadmin/')
@login_required
def admin():
    schools = School.query.all()
    return render_template('admin.html', schools=schools)


@app.route('/directoryadmin/<int:school_id>/add', methods=["GET", "POST"])
@login_required
def add(school_id):
    school = School.query.get_or_404(school_id)
    form = Name()
    form.name.data = school.name
    form.address.data = school.address
    form.contact.data = school.contact
    form.type.data=school.type
    if form.type.data=="PSLE":
        form.Adscore.data=school.PSLE
    elif form.type.data=="L1R5":
        form.Adscore.data=school.L1R5
    elif form.type.data=="L1R4":
        form.Adscore.data=school.L1R4
    form.zone.data=school.zone
    form.website.data = school.website
    form.achievement.data = school.achievement
    form.achievement_1.data = school.achievement_1
    form.niche.data = school.niche
    form.motto.data = school.motto
    form.year.data = school.year
    if form.validate_on_submit():
        result = ConfirmedSchool(name=form.name.data, address=form.address.data, contact=form.contact.data
                           , year=form.year.data, website=form.website.data, achievement=form.achievement.data
                           , achievement_1=form.achievement_1.data, niche=form.niche.data, motto=form.motto.data,
                                 zone=form.zone.data)
        if form.type.data=="PSLE":
            result.PSLE=form.Adscore.data
        elif form.type.data=="L1R4":
            result.L1R4=form.Adscore.data
        elif form.type.data=="L1R5":
            result.L1R5=form.Adscore.data
        db.session.add(result)
        db.session.commit()
        db.session.delete(school)
        db.session.commit()
        flash(f'{form.name.data} has been added', 'success')
        return redirect(url_for('admin'))
    return render_template('add.html', title='add directory', form=form, school=school, legend='accept school')


@app.route('/directoryadmin/delete', methods=["POST"])
@login_required
def delete(school_id):
    school = School.query.get_or_404(school_id)
    db.session.delete(school)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/directoryadmin/<int:school_id>/reject', methods=["POST"])
@login_required
def reject(school_id):
    school = School.query.get_or_404(school_id)
    db.session.delete(school)
    db.session.commit()
    flash(f'{school.name} has been Rejected', 'success')
    return redirect(url_for('admin'))


@app.route("/review")
def review():
    posts = Post.query.all()
    schools = ConfirmedSchool.query.all()
    return render_template('review.html', posts=posts, schools=schools, schoolvalue=0)

@app.route("/review/<school>")
def reviewSchool(school):
    posts=Post.query.all()
    schools={}
    Selectedschool=db.session.query(ConfirmedSchool).filter(ConfirmedSchool.id==school).first()
    schools[0]=Selectedschool
    return render_template("review.html",posts=posts,schools=schools,schoolvalue=0)

@app.route("/review_nofilter")
def review_nofilter():
    posts = Post.query.all()
    flash('showing all reviews', 'info')  # same as normal home + 1 alert
    schools = ConfirmedSchool.query.all()
    return render_template('review.html', posts=posts, schools=schools, schoolvalue=0)

@app.route("/review_nofilter/<school>")
def reviewSchool_nofilter(school):
    posts = Post.query.all()
    flash('showing all reviews', 'info')  # same as normal home + 1 alert
    schools=[]
    Selectedschool = db.session.query(ConfirmedSchool).filter(ConfirmedSchool.id == school).first()
    schools.append(Selectedschool)
    return render_template('review.html', posts=posts, schools=schools, schoolvalue=0)

@app.route("/review_filter1")
def review_filter1():  # for filtering out review w/o staff
    posts = Post.query.all()
    flash('filtered out review without staff', 'info')
    schools = ConfirmedSchool.query.all()
    return render_template('review.html', posts=posts, schools=schools, schoolvalue=0, filter='1')

@app.route("/review_filter1/<school>")
def reviewSchool_filter1(school):  # for filtering out review w/o staff
    posts = Post.query.all()
    flash('filtered out review without staff', 'info')
    schools = []
    Selectedschool = db.session.query(ConfirmedSchool).filter(ConfirmedSchool.id == school).first()
    schools.append(Selectedschool)
    return render_template('review.html', posts=posts, schools=schools, schoolvalue=0, filter='1')

@app.route("/review_filter2")
def review_filter2():  # for filtering out review w/o facilities
    posts = Post.query.all()
    flash('filtered out review without facilities filled', 'info')
    schools = ConfirmedSchool.query.all()
    return render_template('review.html', posts=posts, schools=schools, schoolvalue=0, filter='2')

@app.route("/review_filter2/<school>")
def reviewSchool_filter2(school):  # for filtering out review w/o facilities
    posts = Post.query.all()
    flash('filtered out review without facilities filled', 'info')
    schools = []
    Selectedschool = db.session.query(ConfirmedSchool).filter(ConfirmedSchool.id == school).first()
    schools.append(Selectedschool)
    return render_template('review.html', posts=posts, schools=schools, schoolvalue=0, filter='2')

@app.route("/review_filter3")
def review_filter3():  # for filtering out review w/o advice
    posts = Post.query.all()
    flash('filtered out review without school management advice filled', 'info')
    schools = ConfirmedSchool.query.all()
    return render_template('review.html', posts=posts, schools=schools, schoolvalue=0, filter='3')

@app.route("/review_filter3/<school>")
def reviewSchool_filter3(school):  # for filtering out review w/o advice
    posts = Post.query.all()
    flash('filtered out review without school management advice filled', 'info')
    schools = []
    Selectedschool = db.session.query(ConfirmedSchool).filter(ConfirmedSchool.id == school).first()
    schools.append(Selectedschool)
    return render_template('review.html', posts=posts, schools=schools, schoolvalue=0, filter='3')


@app.route("/review_filter4")
def review_filter4():  # for filtering out review w/o staff, facilities, advice
    posts = Post.query.all()
    flash('filtered out review without staff and facilities filled', 'info')
    schools = ConfirmedSchool.query.all()
    return render_template('review.html', posts=posts, schools=schools, schoolvalue=0, filter='4')

@app.route("/review_filter4/<school>")
def reviewSchool_filter4(school):  # for filtering out review w/o staff, facilities, advice
    posts = Post.query.all()
    flash('filtered out review without staff and facilities filled', 'info')
    schools = []
    Selectedschool = db.session.query(ConfirmedSchool).filter(ConfirmedSchool.id == school).first()
    schools.append(Selectedschool)
    return render_template('review.html', posts=posts, schools=schools, schoolvalue=0, filter='4')

@app.route("/review/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user.email, content2=form.content2.data, content3=form.content3.data, content4=form.content4.data, rating=form.rating.data)
        db.session.add(post)
        db.session.commit()
        flash('Your review has been created!', 'success')
        return redirect(url_for('review'))

    return render_template('create_post.html', title='New Review',
                           form=form, legend='New Review')


@app.route("/review/<int:post_id>")
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    author=None
    if not db.session.query(Teacher).filter(Teacher.email==post.author).first()==None:
        author=db.session.query(Teacher).filter(Teacher.email==post.author).first()
    elif not db.session.query(Alumni).filter(Alumni.email==post.author).first()==None:
        author=db.session.query(Teacher).filter(Teacher.email==post.author).first()
    elif not db.session.query(Admin).filter(Admin.email==post.author).first()==None:
        author=db.session.query(Admin).filter(Admin.email==post.author).first()
    elif not db.session.query(Student).filter(Student.email==post.author).first()==None:
        author=db.session.query(Student).filter(Student.email==post.author).first()
    return render_template('post.html', title=post.title, post=post,author=author)


@app.route("/review/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    #if post.author != current_user:
        #abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.content2 = form.content2.data
        post.content3 = form.content3.data
        post.content4 = form.content4.data
        post.rating = form.rating.data
        db.session.commit()
        flash('Your review has been updated!', 'success')
        return redirect(url_for('review'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.content2.data = post.content2
        form.content3.data = post.content3
        form.content4.data = post.content4
        form.rating.data = post.rating
    return render_template('update_post.html', title='Update Review',
                           form=form, legend='Update Review')


@app.route("/review/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your review has been deleted!', 'success')
    return redirect(url_for('review'))

@app.route("/AdvancedSearch/Teachers/<teacher>")
def show_teacher(teacher):
    teacher=db.session.query(Teacher).filter(Teacher.username==teacher).first()
    if not teacher==None:
        stuff=[]
        image_file = url_for('static', filename='img/profile_pics/' + teacher.image_file)
        return render_template("teacher_account_shown.html",teacher=teacher,image_file=image_file)
    else:
        return "No Match"

if __name__ == '__main__':
    app.run(debug=True)
