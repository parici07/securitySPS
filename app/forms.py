from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, \
    DateField, FileField, TimeField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, optional
from app.models import User
from flask import request
from werkzeug.utils import secure_filename

GENRE_CHOICES = [('Any Genre', 'Any Genre'), ('Role-playing (RPG)', 'Role-playing (RPG)'),
                 ('Simulator', 'Simulator'), ('Sport', 'Sport'), ('Strategy', 'Strategy'),
                 ('Turn-based strategy (TBS)', 'Turn-based strategy (TBS)'), ('Tactical', 'Tactical'),
                 ('Hack and slash/Beat \'em up', 'Hack and slash/Beat \'em up'),
                 ('Quiz/Trivia', 'Quiz/Trivia'), ('Pinball', 'Pinball'), ('Adventure', 'Adventure'),
                 ('Indie', 'Indie'), ('Arcade', 'Arcade'), ('Visual Novel', 'Visual Novel'),
                 ('Card & Board Game', 'Card & Board Game'), ('MOBA', 'MOBA'),
                 ('Point-and-click', 'Point-and-click'), ('Fighting', 'Fighting'), ('Shooter', 'Shooter'),
                 ('Music', 'Music'), ('Platform', 'Platform'), ('Puzzle', 'Puzzle'), ('Racing', 'Racing'),
                 ('Real Time Strategy (RTS)', 'Real Time Strategy (RTS)'), ('Business', 'Business'),
                 ('Drama', 'Drama'), ('Non-fiction', 'Non-fiction'), ('Sandbox', 'Sandbox'),
                 ('Educational', 'Educational'), ('Kids', 'Kids'), ('Open world', 'Open world'),
                 ('Warfare', 'Warfare'), ('Party', 'Party'),
                 ('4X (explore, expand, exploit, exterminate)', '4X (explore, expand, exploit, exterminate)'),
                 ('Mystery', 'Mystery'), ('Romance', 'Romance'), ('Action', 'Action'), ('Fantasy', 'Fantasy'),
                 ('Science fiction', 'Science fiction'), ('Horror', 'Horror'), ('Thriller', 'Thriller'),
                 ('Survival', 'Survival'), ('Historical', 'Historical'), ('Stealth', 'Stealth'),
                 ('Comedy', 'Comedy')]

PLATFORM_CHOICES = [('Any Platform', 'Any Platform'), ('PC (Microsoft Windows)', 'PC (Microsoft Windows)'),
                    ('Linux', 'Linux'), ('PlayStation 5', 'PlayStation 5'), ('Xbox Series X|S', 'Xbox Series X|S'),
                    ('PlayStation 4', 'PlayStation 4'), ('Xbox One', 'Xbox One'), ('Nintendo Switch', 'Nintendo Switch'),
                    ('Xbox 360', 'Xbox 360'), ('PlayStation 3', 'PlayStation 3'), ('Wii U', 'Wii U'), ('Wii', 'Wii'),
                    ('PlayStation 2', 'PlayStation 2'), ('PlayStation', 'PlayStation'), ('Xbox', 'Xbox'), ('GameCube', 'GameCube'),
                    ('Nintendo 64', 'Nintendo 64'), ('Super Nintendo Entertainment System (SNES)', 'Super Nintendo Entertainment System (SNES)')
                    , ('Nintendo Entertainment System (NES)', 'Nintendo Entertainment System (NES)') , ('Atari 2600', 'Atari 2600'),
                    ('Atari 5200', 'Atari 5200'), ('Atari 7800', 'Atari 7800'), ('Atari Lynx', 'Atari Lynx'), ('Atari Jaguar', 'Atari Jaguar'),
                    ('iOS', 'iOS'), ('Android', 'Android'), ('Mac', 'Mac')]

MODE_CHOICES = [('Any Mode', 'Any Mode'), ('Battle Royale', 'Battle Royale'),
                ('Co-operative', 'Co-operative'), ('Massively Multiplayer Online (MMO)', 'Massively Multiplayer Online (MMO)'),
                ('Multiplayer', 'Multiplayer'), ('Single player', 'Single player'), ('Split screen', 'Split screen')]

PERSPECTIVE_CHOICES = [('Any Perspective', 'Any Perspective'), ('Auditory', 'Auditory'),
                       ('Bird view / Isometric', 'Bird view / Isometric'), ('First person', 'First person'),
                       ('Side view', 'Side view'), ('Text', 'Text'), ('Third person', 'Third person'),
                       ('Virtual Reality', 'Virtual Reality')]

CATEGORY_CHOICES = [('General', 'General'), ('Recruitment', 'Recruitment'), ('Discussion', 'Discussion'),
                    ('Looking for Group', 'Looking for Group'), ('Games', 'Games'), ('Events', 'Events')]
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


    def validate_password(self, password):
        user = User.query.filter_by(username=self.username.data).first()
        if user is not None:
            if not user.check_password(password.data):
                raise ValidationError('Your username or password is incorrect')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    admin = StringField('Admin Code')
    terms = BooleanField('I agree to the terms and conditions', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

        organisation = email.data.split('@')[1]
        if str(organisation) != 'stpauls.qld.edu.au':
            raise ValidationError('Please use a valid school email address.')

    def validate_password(self, password):
        if len(password.data) < 8:
            raise ValidationError('Password must be at least 8 characters long.')

        if password.data == password.data.lower():
            raise ValidationError('Password must contain at least one uppercase letter.')

        if password.data == password.data.upper():
            raise ValidationError('Password must contain at least one lowercase letter.')

        if password.data.isalpha():
            raise ValidationError('Password must contain at least one number.')

        if password.data.isnumeric():
            raise ValidationError('Password must contain at least one letter.')
        # if in file
        if password.data in open('app/static/text/common.txt').read():
            raise ValidationError('Password is too common.')

class SearchGamesForm(FlaskForm):
    game = StringField('Game', validators=[DataRequired()])
    genre = SelectField('Genre', choices=GENRE_CHOICES, validators=[optional()])
    platform = SelectField('Platform', choices=PLATFORM_CHOICES, validators=[optional()])
    year = IntegerField('Year', validators=[optional()])
    mode = SelectField('Mode', choices=MODE_CHOICES, validators=[optional()])
    perspective = SelectField('Perspective', choices=PERSPECTIVE_CHOICES, validators=[optional()])
    submit = SubmitField('Search')

class CreateTeamForm(FlaskForm):
    team_name = StringField('Team Name', validators=[DataRequired()])
    team_description = StringField('Team Description', validators=[DataRequired()])
    submit = SubmitField('Create Team')

class TeamSearchForm(FlaskForm):
    team_name = StringField('Team Name', validators=[DataRequired()])
    submit = SubmitField('Search')


class CreatePostForm(FlaskForm):
    post_content = TextAreaField('Post Content', validators=[DataRequired()])
    category = SelectField('Category', choices=CATEGORY_CHOICES)
    submit = SubmitField('Create Post')

class SearchPostsForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class CreateCommentForm(FlaskForm):
    c_content = TextAreaField('Comment Content', validators=[DataRequired()])
    submit = SubmitField('Create Comment')

class EditProfileForm(FlaskForm):
    bio = TextAreaField('Bio', validators=[optional()])
    pfp = FileField('Profile Picture', validators=[optional(), FileAllowed(['jpg', 'png', 'jpeg'])])
    pronouns = StringField('Pronouns', validators=[optional()])
    submit = SubmitField('Save')

    def validate_pronouns(self, pronouns):
        if pronouns.data in open('app/static/text/pblacklist.txt').read():
            raise ValidationError('Get a better joke.')

class CreateTournamentForm(FlaskForm):
    tournament_name = StringField('Tournament Name', validators=[DataRequired()])
    tournament_description = StringField('Tournament Description', validators=[DataRequired()])
    participants = IntegerField('Participants', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    submit = SubmitField('Create Tournament')

class SearchTournamentsForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class AddMatchForm(FlaskForm):
    player1 = SelectField('Player 1', validators=[DataRequired()])
    player2 = SelectField('Player 2', validators=[DataRequired()])
    match_date = DateField('Match Date', format='%Y-%m-%d', validators=[DataRequired()])
    match_time = TimeField('Match Time', format='%H:%M', validators=[DataRequired()])
    submit = SubmitField('Add Match')

class SearchUsersForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class SearchMentorsForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class CreatePractiseForm(FlaskForm):
    practise_name = StringField('Practise Name', validators=[DataRequired()])
    practise_description = StringField('Practise Description', validators=[DataRequired()])
    practise_date = DateField('Practise Date', format='%Y-%m-%d', validators=[DataRequired()])
    practise_time = TimeField('Practise Time', format='%H:%M', validators=[DataRequired()])
    submit = SubmitField('Create Practise')

class CreateNoteForm(FlaskForm):
    note = TextAreaField('Note', validators=[DataRequired()])
    submit = SubmitField('Add Note')




