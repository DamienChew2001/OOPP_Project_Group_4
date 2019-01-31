from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField, HiddenField,RadioField,DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange,InputRequired,length
from flask_login import current_user


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




