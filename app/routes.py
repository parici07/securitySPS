import os
from app import app, db
from app.forms import (SearchGamesForm, LoginForm, RegistrationForm, CreateTeamForm,
                       TeamSearchForm, CreatePostForm, SearchPostsForm, CreateCommentForm,
                       EditProfileForm, CreateTournamentForm, SearchTournamentsForm, AddMatchForm,
                       SearchUsersForm, SearchMentorsForm, CreatePractiseForm)
from app.models import (User, FavouriteGames, Teams, TeamUsers, Posts, Likes, Comments,
                        Tournaments, TournamentUsers, Matches, MatchUsers, Following, Mentor,
                        MentApplications, Practises)
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
import requests
import datetime
from datetime import date
from werkzeug.utils import secure_filename

CLIENT_ID = '85v6iy5ufik67v1ya6v7gqovuo7pur'
ACCESS_TOKEN = ('jupv9nrc72mzidmshdplmuct50xigy')
HEADERS = {
    'Client-ID': CLIENT_ID,
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}


def game_info(game_id):
    url = 'https://api.igdb.com/v4/games'
    query = f'''
    fields name, cover.url, age_ratings.content_descriptions.description, release_dates.human, genres.name, rating, summary, url, themes.name;
    where id = {game_id};
        limit 10;
    '''

    response = requests.post(url, headers=HEADERS, data=query, verify=False)
    if response.status_code == 200:
        games = response.json()
        print(f"Number of games retrieved: {len(games)}")  # Debugging line
        return games
    else:
        print(f"Error fetching games: {response.status_code}, {response.text}")  # Debugging line
        return []

def game_search(game, genre, platform, year, mode, perspective):
    url = 'https://api.igdb.com/v4/games'
    query = f'''
        fields name, release_dates.human, cover.url, id, platforms.name;
        search "{game}";
        limit 500;
    '''

    filters = []

    if genre != 'Any Genre':
        filters.append(f'(genres.name = "{genre}" | themes.name = "{genre}")')

    if platform != 'Any Platform':
        filters.append(f'platforms.name = "{platform}"')

    if year:
        start_date_timestamp = int(datetime.datetime(year, 1, 1).timestamp())
        end_date_timestamp = int(datetime.datetime(year, 12, 31).timestamp())

        filters.append(f'first_release_date >= {start_date_timestamp} & first_release_date <= {end_date_timestamp}')

    if mode != 'Any Mode':
        filters.append(f'game_modes.name = "{mode}"')

    if perspective != 'Any Perspective':
        filters.append(f'player_perspectives.name = "{perspective}"')


    if len(filters) > 0:
        where = 'where ' + ' & '.join(filters) + ';'
        print(where)
        query = query.replace('limit 500;', where + '\n limit 500;')

    print(query)
    response = requests.post(url, headers=HEADERS, data=query, verify=False)

    if response.status_code == 200:
        games = response.json()
        print(f"Number of games retrieved: {len(games)}")
        return games
    else:
        print(f"Error fetching games: {response.status_code}, {response.text}")
        return []

@app.route('/')
@app.route('/index')
@login_required
def index():
    # GET ALL EVENTS USER IS IN
    today = date.today()
    matchuser_inst = MatchUsers.query.filter_by(user_id=current_user.user_id).all()
    matches = []
    for match in matchuser_inst:
        match = Matches.query.filter_by(match_id=match.match_id).first()
        if match.match_datetime.date() >= today:
            matches.append(match)


    tournamentuser_inst = TournamentUsers.query.filter_by(user_id=current_user.user_id).all()
    tournaments = []
    for tournament in tournamentuser_inst:
        tournament = Tournaments.query.filter_by(tournament_id=tournament.tournament_id).first()
        if tournament.end_date >= today:
            tournaments.append(tournament)

    # get all teams
    teamuser_inst = TeamUsers.query.filter_by(team_user_id=current_user.user_id).all()
    teams = []
    for team in teamuser_inst:
        team = Teams.query.filter_by(team_id=team.team_id).first()
        teams.append(team)

    # get all team practises
    practises = []
    for team in teams:
        practise_inst = Practises.query.filter_by(team_id=team.team_id).all()
        for practise in practise_inst:
            if practise.practise_datetime.date() >= today:
                practises.append(practise)



    events = []
    for match in matches:
        event = {}
        event['type'] = 'Match'
        event['name'] = f'Match {match.match_number}'
        match_date = match.match_datetime
        #convert datetime to date
        match_date = match_date.date()
        event['date'] = match_date
        event['id'] = match.match_id
        events.append(event)

    for tournament in tournaments:
        event = {}
        event['type'] = 'Tournament Start'
        event['name'] = tournament.tournament_name
        event['date'] = tournament.start_date
        event['id'] = tournament.tournament_id
        events.append(event)

        event = {}
        event['type'] = 'Tournament End'
        event['name'] = tournament.tournament_name
        event['date'] = tournament.end_date
        event['id'] = tournament.tournament_id
        events.append(event)

    for practise in practises:
        event = {}
        event['type'] = 'Practise'
        event['name'] = practise.practise_name
        event['date'] = practise.practise_datetime.date()
        event['id'] = practise.practise_id
        events.append(event)

    events = sorted(events, key=lambda x: x['date'])
    print(events)

    # GET ALL POSTS
    posts = []




    return render_template('index.html', title='Home', events=events, posts=posts)

## LOGIN AND REGISTER ROUTES ##

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    else:
        print(form.errors)
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.admin.data == 'ADMIN2024':
            user = User(username=form.username.data, email=form.email.data, admin=True)
        else:
            user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account registered. Please login.')
        return redirect(url_for('login'))
    else:
        print(form.errors)
    return render_template('register.html', title='Register', form=form)

## USER ROUTES ##
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    following = Following.query.filter_by(user_id=current_user.user_id, following_id=user.user_id).first()

    # get favourite games
    favourite_games = FavouriteGames.query.filter_by(user_id=user.user_id).all()
    games = []
    for game in favourite_games:
        games.append(game_info(game.game_id)[0])
    print(games)

    # get posts
    posts = Posts.query.filter_by(user_id=user.user_id).all()

    # mentor status
    is_ment = MentApplications.query.filter_by(user_id=user.user_id).first()

    return render_template('user.html', title='Profile', user=user, games=games, posts=posts, following=following, is_ment=is_ment)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        if form.bio.data:
            current_user.bio = form.bio.data

        if form.pfp.data:
            if current_user.pfp:
                os.remove('app/static/pfps/' + current_user.pfp)
            file_name = current_user.username + secure_filename(form.pfp.data.filename)
            form.pfp.data.save('app/static/pfps/' + file_name)
            current_user.pfp = file_name

        if form.pronouns.data:
            current_user.pronouns = form.pronouns.data

        db.session.commit()
        flash('Profile updated')
        return redirect(url_for('user', username=current_user.username))
    else:
        print(form.errors)
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/search_users', methods=['GET', 'POST'])
@login_required
def search_users():
    form = SearchUsersForm()
    users = ''
    if form.validate_on_submit():
        users = User.query.filter_by(username=form.search.data).all()
        return render_template('search_users.html', title="Search Users", form=form, users=users)
    else:
        print(form.errors)

    return render_template('search_users.html', title="Search Users", form=form, users=users)

@app.route('/follow/<username>', methods=['GET', 'POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()

    if user:
        following = Following.query.filter_by(user_id=current_user.user_id, following_id=user.user_id).first()
        if following:
            db.session.delete(following)
            db.session.commit()
            flash(f'Unfollowed {username}')
        else:
            follow = Following(user_id=current_user.user_id, following_id=user.user_id)
            db.session.add(follow)
            db.session.commit()
            flash(f'Followed {username}')
    return redirect(url_for('user', username=username))




## GAME ROUTES ##
@app.route('/search_games', methods=['GET', 'POST'])
@login_required
def search_games():
    games = ''
    form = SearchGamesForm()
    if form.validate_on_submit():
        games = game_search(form.game.data, form.genre.data, form.platform.data, form.year.data,
                            form.mode.data, form.perspective.data)

        return render_template('search_games.html', title='Search Games', form=form, games=games)
    else:
        print(form.errors)
    return render_template('search_games.html', title='Search Games', form=form, games=games)

@app.route('/game/<game_id>')
@login_required
def game(game_id):
    games = game_info(game_id)
    is_favourite = FavouriteGames.query.filter_by(user_id=current_user.user_id, game_id=game_id).first()

    game = games[0]
    cover_url = game['cover']['url']
    cover_url = cover_url.replace('t_thumb', 't_cover_big')
    game['cover']['url'] = cover_url
    print(game)
    print(game['name'])
    print(game['release_dates'][0]['human'])
    print(game['age_ratings'][0])
    return render_template('game.html', title=game['name'], game=game, is_favourite=is_favourite)

@app.route('/favourite_game/<game_id>')
@login_required
def favourite_game(game_id):
    is_favourite = FavouriteGames.query.filter_by(user_id=current_user.user_id, game_id=game_id).first()
    if is_favourite:
        db.session.delete(is_favourite)
        db.session.commit()
        flash('Game removed from favourites')
    else:
        favourite_game = FavouriteGames(user_id=current_user.user_id, game_id=game_id)
        db.session.add(favourite_game)
        db.session.commit()
        flash('Game added to favourites')

    return redirect(url_for('game', game_id=game_id))

## TEAM ROUTES ##

@app.route('/search_teams', methods=['GET', 'POST'])
@login_required
def search_teams():
    form = TeamSearchForm()

    # get user teams
    userteam_inst = TeamUsers.query.filter_by(user_id=current_user.user_id).all()
    user_teams = []
    for team in userteam_inst:
        team = Teams.query.filter_by(team_id=team.team_id).first()
        user_teams.append(team)

    teams = ''
    if form.validate_on_submit():
        teams = Teams.query.filter_by(team_name=form.team_name.data).all()
        return render_template('search_teams.html', title='Search Teams', form=form, teams=teams)
    else:
        print(form.errors)
    return render_template('search_teams.html', title='Search Teams', form=form, teams=teams, user_teams=user_teams)

@app.route('/create_team', methods=['GET', 'POST'])
@login_required
def create_team():
    form = CreateTeamForm()

    if form.validate_on_submit():
        if current_user.admin == True:
            team = Teams(team_name=form.team_name.data, team_description=form.team_description.data, admin_id=current_user.user_id, official=True)
        else:
            team = Teams(team_name=form.team_name.data, team_description=form.team_description.data, admin_id=current_user.user_id)

        db.session.add(team)
        db.session.commit()
        flash('Team created')
        return redirect(url_for('index'))
    else:
        print(form.errors)
    return render_template('create_team.html', title='Create Team', form=form)

@app.route('/team/<team_id>', methods=['GET', 'POST'])
@login_required
def team(team_id):
    in_team = TeamUsers.query.filter_by(user_id=current_user.user_id, team_id=team_id).first()
    team = Teams.query.filter_by(team_id=team_id).first_or_404()
    team_users = TeamUsers.query.filter_by(team_id=team_id).all()
    users = []
    for user in team_users:
        users.append(User.query.filter_by(user_id=user.user_id).first())

    print(team.admin_id)
    print(current_user.user_id)

    if current_user.user_id == team.admin_id:
        admin = True
    else:
        admin = False
    return render_template('team.html', title=team.team_name, team=team, users=users, in_team=in_team, admin=admin)

@app.route('/join_team/<team_id>')
@login_required
def join_team(team_id):
    in_team = TeamUsers.query.filter_by(user_id=current_user.user_id, team_id=team_id).first()

    if in_team:
        db.session.delete(in_team)
        db.session.commit()
        flash('Left team')
    else:
        team_user = TeamUsers(user_id=current_user.user_id, team_id=team_id)
        db.session.add(team_user)
        db.session.commit()
        flash('Joined team')

    return redirect(url_for('team', team_id=team_id))

@app.route('/create_practise/<team_id>', methods=['GET', 'POST'])
@login_required
def create_practise(team_id):
    team = Teams.query.filter_by(team_id=team_id).first_or_404()

    if current_user.user_id != team.admin_id:
        return redirect(url_for('index'))

    form = CreatePractiseForm()

    if form.validate_on_submit():
        practise_datetime = datetime.datetime.combine(form.practise_date.data, form.practise_time.data)

        practise = Practises(practise_name=form.practise_name.data, practise_description=form.practise_description.data, practise_datetime=practise_datetime, team_id=team_id)
        db.session.add(practise)
        db.session.commit()
        flash('Practise created')
        return redirect(url_for('team', team_id=team_id))
    else:
        print(form.errors)
    return render_template('create_practise.html', title='Create Practise', form=form, team=team)

@app.route('/practise/<practise_id>', methods=['GET', 'POST'])
@login_required
def practise(practise_id):
    practise = Practises.query.filter_by(practise_id=practise_id).first()

    return render_template('practise.html', title=practise.practise_name, practise=practise)


## POST ROUTES ##

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        post = Posts(post_content=form.post_content.data, category=form.category.data, user_id=current_user.user_id)
        db.session.add(post)
        db.session.commit()
        flash('Post created')
        return redirect(url_for('index'))
    else:
        print(form.errors)

    return render_template('create_post.html', title='Create Post', form=form)

@app.route('/post/<post_id>')
@login_required
def post(post_id):
    post = Posts.query.filter_by(post_id=post_id).first_or_404()
    author = User.query.filter_by(user_id=post.user_id).first()
    likes = Likes.query.filter_by(post_id=post_id).count()
    comments = Comments.query.filter_by(post_id=post_id).all()
    for comment in comments:
        comment_author = User.query.filter_by(user_id=comment.user_id).first()
        comment.author = comment_author.username

    is_liked = Likes.query.filter_by(user_id=current_user.user_id, post_id=post_id).count()
    return render_template('post.html', title='Post', post=post, author=author, likes=likes, is_liked=is_liked, comments=comments)

@app.route('/search_posts', methods=['GET', 'POST'])
@login_required
def search_posts():
    posts = ''
    form = SearchPostsForm()
    if form.validate_on_submit():
        posts = Posts.query.filter_by(post_content=form.search.data).all()
        for post in posts:
            author = User.query.filter_by(user_id=post.user_id).first()
            post.author = author.username

        return render_template('search_posts.html', title='Search Posts', form=form, posts=posts)
    else:
        print(form.errors)
    return render_template('search_posts.html', title='Search Posts', form=form, posts=posts)

@app.route('/like_post/<post_id>', methods=['GET', 'POST'])
@login_required
def like_post(post_id):
    is_liked = Likes.query.filter_by(user_id=current_user.user_id, post_id=post_id).count()

    if is_liked > 0:
        like = Likes.query.filter_by(user_id=current_user.user_id, post_id=post_id).first()
        db.session.delete(like)
        db.session.commit()
        flash('Post unliked')
    else:
        like = Likes(user_id=current_user.user_id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        flash('Post liked')

    return redirect(url_for('post', post_id=post_id))

@app.route('/create_comment/<post_id>', methods=['GET', 'POST'])
@login_required
def create_comment(post_id):
    form = CreateCommentForm()
    post = Posts.query.filter_by(post_id=post_id).first_or_404()

    if form.validate_on_submit():
        comment = Comments(c_content=form.c_content.data, post_id=post_id, user_id=current_user.user_id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment created')
        return redirect(url_for('post', post_id=post_id))
    else:
        print(form.errors)


    return render_template('create_comment.html', title='Create Comment', form=form, post=post)

## TOURNAMENT HANDLING ##

@app.route('/create_tournament', methods=['GET', 'POST'])
@login_required
def create_tournament():
    if current_user.admin == False:
        return redirect(url_for('index'))

    form = CreateTournamentForm()

    if form.validate_on_submit():
        tournament = Tournaments(tournament_name=form.tournament_name.data, tournament_description=form.tournament_description.data,
                                 admin_id=current_user.user_id, start_date=form.start_date.data, end_date=form.end_date.data,
                                 participants=form.participants.data)
        db.session.add(tournament)
        db.session.commit()
        flash('Tournament created')
        return redirect(url_for('index'))
    else:
        print(form.errors)
    return render_template('create_tournament.html', title='Create Tournament', form=form)

@app.route('/tournament/<tournament_id>', methods=['GET', 'POST'])
@login_required
def tournament(tournament_id):
    tournament = Tournaments.query.filter_by(tournament_id=tournament_id).first_or_404()
    tournament_users = TournamentUsers.query.filter_by(tournament_id=tournament_id).all()
    users = []
    if current_user.user_id == tournament.admin_id:
        admin = True
    else:
        admin = False
    in_tournament = TournamentUsers.query.filter_by(user_id=current_user.user_id, tournament_id=tournament_id).first()
    if tournament.participants == len(tournament_users):
        full = True
    else:
        full = False

    for user in tournament_users:
        users.append(User.query.filter_by(user_id=user.user_id).first())

    matches = Matches.query.filter_by(tournament_id=tournament_id).all()




    return render_template('tournament.html', title=tournament.tournament_name,
                           tournament=tournament, users=users, in_tournament=in_tournament,
                           full=full, admin=admin, matches=matches)

@app.route('/join_tournament/<tournament_id>', methods=['GET', 'POST'])
@login_required
def join_tournament(tournament_id):
    if current_user.admin:
        flash('Admins cannot join tournaments.')
        return redirect(url_for('tournament', tournament_id=tournament_id))

    in_tournament = TournamentUsers.query.filter_by(user_id=current_user.user_id, tournament_id=tournament_id).first()
    total_participants = TournamentUsers.query.filter_by(tournament_id=tournament_id).count()
    tournament = Tournaments.query.filter_by(tournament_id=tournament_id).first()

    if in_tournament:
        db.session.delete(in_tournament)
        db.session.commit()
        flash('Left tournament')
    else:
        if tournament.participants <= total_participants:
            flash('Tournament is full')
            return redirect(url_for('tournament', tournament_id=tournament_id))

        tournament_user = TournamentUsers(user_id=current_user.user_id, tournament_id=tournament_id)
        db.session.add(tournament_user)
        db.session.commit()
        flash('Joined tournament')

    return redirect(url_for('tournament', tournament_id=tournament_id))

@app.route('/search_tournaments', methods=['GET', 'POST'])
@login_required
def search_tournaments():
    form = SearchTournamentsForm()
    tournaments = ''

    if form.validate_on_submit():
        tournaments = Tournaments.query.filter_by(tournament_name=form.search.data).all()
        return render_template('search_tournaments.html', title='Search Tournaments', form=form, tournaments=tournaments)
    else:
        print(form.errors)

    return render_template('search_tournaments.html', title='Search Tournaments', form=form, tournaments=tournaments)

## MATCH HANDLING ##

@app.route('/add_match/<tournament_id>', methods=['GET', 'POST'])
@login_required
def add_match(tournament_id):
    tournament = Tournaments.query.filter_by(tournament_id=tournament_id).first_or_404()
    admin = User.query.filter_by(user_id=tournament.admin_id).first()
    match_num = Matches.query.filter_by(tournament_id=tournament_id).count() + 1

    if current_user.user_id != admin.user_id:
        return redirect(url_for('index'))

    '''if tournament.participants != TournamentUsers.query.filter_by(tournament_id=tournament_id).count():
        flash('Not all participants have joined the tournament')
        return redirect(url_for('tournament', tournament_id=tournament_id))'''

    if tournament.end_date < date.today():
        flash('Tournament has ended')
        return redirect(url_for('tournament', tournament_id=tournament_id))

    form = AddMatchForm()

    tournament_users = TournamentUsers.query.filter_by(tournament_id=tournament_id).all()
    choices = []
    for user in tournament_users:
        user = User.query.filter_by(user_id=user.user_id).first()
        choices.append((user.user_id, user.username))
    print(choices)

    form.player1.choices = choices
    form.player2.choices = choices

    if form.validate_on_submit():
        player1_id = form.player1.data
        player2_id = form.player2.data
        match_date = datetime.datetime.combine(form.match_date.data, form.match_time.data)

        player1 = User.query.filter_by(user_id=player1_id).first()
        player2 = User.query.filter_by(user_id=player2_id).first()

        if player1_id == player2_id:
            flash('Players cannot be the same')
            flash('Players cannot be the same')
            return redirect(url_for('add_match', tournament_id=tournament_id))


        match = Matches(match_number=match_num, match_datetime=match_date, tournament_id=tournament_id)

        db.session.add(match)
        db.session.commit()

        # get match
        match = Matches.query.filter_by(match_number=match_num, tournament_id=tournament_id).first()
        matchplayer1 = MatchUsers(match_id=match.match_id, user_id=player1_id)
        matchplayer2 = MatchUsers(match_id=match.match_id, user_id=player2_id)

        db.session.add(matchplayer1)
        db.session.add(matchplayer2)
        db.session.commit()
        flash('Match created')
        return redirect(url_for('tournament', tournament_id=tournament_id))
    else:
        print(form.errors)
    return render_template('add_match.html', title='Add Match', form=form, choices=choices, tournament_id=tournament_id)

## MENTOR SYSTEM ##
@app.route('/mentor_application', methods=['GET', 'POST'])
@login_required
def mentor_application():
    is_mentor = MentApplications.query.filter_by(user_id=current_user.user_id).first()
    if is_mentor:
        flash('Withdrawn from mentor role.')
        db.session.delete(is_mentor)
        db.session.commit()
    else:
        mentor = MentApplications(user_id=current_user.user_id)
        db.session.add(mentor)
        db.session.commit()
        flash('Users can now select you as a mentor.')
    return redirect(url_for('user', username=current_user.username))

@app.route('/search_mentors', methods=['GET', 'POST'])
@login_required
def search_mentors():
    form = SearchMentorsForm()
    users = ''

    mentors = []

    if form.validate_on_submit():
        users = User.query.filter_by(username=form.search.data).all()
        for user in users:
            mentor = MentApplications.query.filter_by(user_id=user.user_id).first()
            if mentor:
                mentors.append(user)
        return render_template('search_mentors.html', title='Search Mentors', form=form, users=users, mentors=mentors)
    else:
        print(form.errors)
    return render_template('search_mentors.html', title='Search Mentors', users=users, form=form)

@app.route('/select_mentor/<mentor_id>')
@login_required
def select_mentor(mentor_id):
    # check if already mentoring someone
    is_mentoring = Mentor.query.filter_by(mentor_id=mentor_id).first()
    if is_mentoring:
        flash('Mentor is already mentoring someone.')
        return redirect(url_for('search_mentors'))

    # check if same as current user
    if int(mentor_id) == int(current_user.user_id):
        flash('Cannot mentor self.')
        return redirect(url_for('search_mentors'))

    mentor = Mentor(mentor_id=mentor_id, mentee_id=current_user.user_id)
    db.session.add(mentor)
    db.session.commit()
    flash('Mentor selected')
    return redirect(url_for('search_mentors'))

## MANAGEMENT DASHBOARD ##
@app.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    if current_user.admin == False:
        return redirect(url_for('index'))

    # get all admin teams
    teams = Teams.query.filter_by(admin_id=current_user.user_id).all()

    return render_template('manage.html', title='Management Dashboard', teams=teams)
















