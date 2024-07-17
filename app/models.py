from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from passlib.hash import argon2




class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    bio = db.Column(db.String(500))
    pfp = db.Column(db.String(500))
    pronouns = db.Column(db.String(50))
    admin = db.Column(db.Boolean, default=False)

    team_admin = db.relationship('Teams', back_populates='team_admin')
    team_users = db.relationship('TeamUsers', back_populates='user')
    posts = db.relationship('Posts', back_populates='user')
    likes = db.relationship('Likes', back_populates='user')
    comments = db.relationship('Comments', back_populates='user')
    tournament_users = db.relationship('TournamentUsers', back_populates='user')
    match_users = db.relationship('MatchUsers', back_populates='user')
    ment_applications = db.relationship('MentApplications', back_populates='user')

    # match winner
    matches_won = db.relationship('Matches', back_populates='match_winner', foreign_keys='Matches.winner_id')

    # many to one relationships
    tournament_admin = db.relationship('Tournaments', backref='user', foreign_keys='Tournaments.admin_id')
    tournament_winner = db.relationship('Tournaments', foreign_keys='Tournaments.winner_id')

    following = db.relationship('Following', backref='user', foreign_keys='Following.user_id')
    followed = db.relationship('Following', foreign_keys='Following.following_id')

    mentor = db.relationship('Mentor', backref='mentor', foreign_keys='Mentor.mentor_id')
    mentee = db.relationship('Mentor', foreign_keys='Mentor.mentee_id')



    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f'<User {self.username}>'
    #pkdf2_sha256
    '''def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)'''

    #bcrypt
    '''def set_password(self, password):
        salt = bc.gensalt()
        # convert password to bytes
        password = password.encode('utf-8')
        self.password_hash = bc.hashpw(password=password, salt=salt)

    def check_password(self, password):
        password = password.encode('utf-8')
        return bc.checkpw(password=password, hashed_password=self.password_hash)'''

    #argon2

    def set_password(self, password):
        self.password_hash = argon2.hash(password)

    def check_password(self, password):
        return argon2.verify(password, self.password_hash)


class Following(db.Model):
    follow_id = db.Column(db.Integer, primary_key=True, index=True, unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), name='follow_user_id', nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), name='follow_following_id', nullable=False)

    def __repr__(self):
        return '<Following {}>'.format(self.follow_id)

    def get_id(self):
        return str(self.follow_id)

class FavouriteGames(db.Model):
    favourite_game_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    game_id = db.Column(db.Integer, index=True, nullable=False)

    def get_id(self):
        return str(self.favourite_game_id)

    def __repr__(self):
        return f'<FavouriteGames {self.favourite_game_id}>'

class Teams(db.Model):
    team_id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(64), index=True, unique=True)
    team_description = db.Column(db.String(500))
    admin_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    official = db.Column(db.Boolean, default=False)

    team_admin = db.relationship('User', back_populates='team_admin')
    team_users = db.relationship('TeamUsers', back_populates='team')

    practises = db.relationship('Practises', back_populates='team')


    def get_id(self):
        return str(self.team_id)

    def __repr__(self):
        return f'<Teams {self.team_name}>'

class TeamUsers(db.Model):
    team_user_id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    team = db.relationship('Teams', back_populates='team_users')
    user = db.relationship('User', back_populates='team_users')
    def get_id(self):
        return str(self.team_user_id)

    def __repr__(self):
        return f'<TeamUsers {self.team_user_id}>'

class Posts(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    post_content = db.Column(db.String(500))
    post_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    category = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    user = db.relationship('User', back_populates='posts')
    likes = db.relationship('Likes', back_populates='post')
    comments = db.relationship('Comments', back_populates='post')

    def get_id(self):
        return str(self.post_id)

    def __repr__(self):
        return f'<Posts {self.post_id}>'

class Likes(db.Model):
    like_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    post = db.relationship('Posts', back_populates='likes')
    user = db.relationship('User', back_populates='likes')

    def get_id(self):
        return str(self.like_id)

    def __repr__(self):
        return f'<Likes {self.like_id}>'

class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    c_content = db.Column(db.String(500))
    c_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    user = db.relationship('User', back_populates='comments')
    post = db.relationship('Posts', back_populates='comments')

    def get_id(self):
        return str(self.comment_id)

    def __repr__(self):
        return f'<Comments {self.comment_id}>'

class Tournaments(db.Model):
    tournament_id = db.Column(db.Integer, primary_key=True)
    tournament_name = db.Column(db.String(64), index=True, unique=True)
    tournament_description = db.Column(db.String(500))
    start_date = db.Column(db.Date, index=True)
    end_date = db.Column(db.Date, index=True)
    participants = db.Column(db.Integer)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    winner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    tournament_users = db.relationship('TournamentUsers', back_populates='tournament')
    matches = db.relationship('Matches', back_populates='tournament')

    def get_id(self):
        return str(self.tournament_id)

    def __repr__(self):
        return f'<Tournaments {self.tournament_name}>'

class TournamentUsers(db.Model):
    tournament_user_id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.tournament_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    tournament = db.relationship('Tournaments', back_populates='tournament_users')
    user = db.relationship('User', back_populates='tournament_users')

    def get_id(self):
        return str(self.tournament_user_id)

    def __repr__(self):
        return f'<TournamentUsers {self.tournament_user_id}>'

class Matches(db.Model):
    match_id = db.Column(db.Integer, primary_key=True)
    match_number = db.Column(db.Integer)
    match_datetime = db.Column(db.DateTime, index=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.tournament_id'))
    winner_id = db.Column(db.Integer, db.ForeignKey('user.user_id', name='winner_id'))

    tournament = db.relationship('Tournaments', back_populates='matches')
    match_users = db.relationship('MatchUsers', back_populates='match')
    match_winner = db.relationship('User', foreign_keys=[winner_id], back_populates='matches_won')

    def get_id(self):
        return str(self.match_id)

    def __repr__(self):
        return f'<Matches {self.match_id}>'

class MatchUsers(db.Model):
    match_user_id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.match_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    match = db.relationship('Matches', back_populates='match_users')
    user = db.relationship('User', back_populates='match_users')

    def get_id(self):
        return str(self.match_user_id)

    def __repr__(self):
        return f'<MatchUsers {self.match_user_id}>'

class Mentor(db.Model):
    ment_id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), name='mentor_id', nullable=False)
    mentee_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), name='mentee_id', nullable=False)

    def get_id(self):
        return str(self.ment_id)

    def __repr__(self):
        return f'<Mentor {self.ment_id}>'

class MentApplications(db.Model):
    ment_appl_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    user = db.relationship('User', back_populates='ment_applications')

    def get_id(self):
        return str(self.ment_appl_id)

    def __repr__(self):
        return f'<MentApplications {self.ment_appl_id}>'

class Practises(db.Model):
    practise_id = db.Column(db.Integer, primary_key=True)
    practise_name = db.Column(db.String(64), index=True, unique=True)
    practise_description = db.Column(db.String(500))
    practise_datetime = db.Column(db.DateTime, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'))

    team = db.relationship('Teams', back_populates='practises')

    def get_id(self):
        return str(self.practise_id)

    def __repr__(self):
        return f'<Practises {self.practise_name}>'

class Stats(db.Model):
    stat_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    game_id = db.Column(db.Integer, index=True, nullable=False)
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)
    draws = db.Column(db.Integer)
    notes = db.Column(db.String(500))

    def get_id(self):
        return str(self.stat_id)

    def __repr__(self):
        return f'<Stats {self.stat_id}>'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))