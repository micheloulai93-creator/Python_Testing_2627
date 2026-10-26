import json
from datetime import datetime

from flask import (Flask, flash, redirect, render_template, request,
                   session, url_for)


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


def saveData():
    """Sauvegarde les données modifiées dans les fichiers JSON."""
    with open('clubs.json', 'w') as c:
        json.dump({'clubs': clubs}, c, indent=4)
    with open('competitions.json', 'w') as comps:
        json.dump({'competitions': competitions}, comps, indent=4)


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

MAX_PLACES_PER_CLUB = 12

bookings = {}


def get_club_by_email(email):
    return next((c for c in clubs if c['email'] == email), None)


def get_club_by_name(name):
    return next((c for c in clubs if c['name'] == name), None)


def get_competition_by_name(name):
    return next((c for c in competitions if c['name'] == name), None)


def is_competition_over(competition, now=None):
    now = now or datetime.now()
    try:
        date = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    except (KeyError, ValueError):
        return True
    return date < now


@app.context_processor
def inject_helpers():
    return {'is_over': is_competition_over}


def parse_places(raw_value):
    try:
        value = int(str(raw_value).strip())
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def validate_booking(club, competition, places_required, already_booked=0):
    if is_competition_over(competition):
        return "This competition is already over."
    if already_booked + places_required > MAX_PLACES_PER_CLUB:
        return "You cannot book more than 12 places in a competition."
    if int(competition['numberOfPlaces']) <= 0:
        return "This competition is full."
    if places_required > int(competition['numberOfPlaces']):
        return "Not enough places available in this competition."
    if places_required > int(club['points']):
        return "Not enough points to book that many places."
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['GET', 'POST'])
def showSummary():
    if request.method == 'POST':
        club = get_club_by_email(request.form.get('email', ''))
        if club is None:
            flash("Sorry, that email was not found.", "error")
            return redirect(url_for('index'))
        session['email'] = club['email']
        return render_template('welcome.html', club=club, competitions=competitions)
    else:
        if 'email' in session:
            club = get_club_by_email(session['email'])
            if club:
                return render_template('welcome.html', club=club, competitions=competitions)
        return redirect(url_for('index'))


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = get_club_by_name(club)
    foundCompetition = get_competition_by_name(competition)
    if foundClub is None:
        flash("Something went wrong-please try again", "error")
        return redirect(url_for('index'))
    if foundCompetition is None:
        flash("Something went wrong-please try again", "error")
        return render_template('welcome.html', club=foundClub, competitions=competitions)
    if is_competition_over(foundCompetition):
        flash("This competition is already over.", "error")
        return render_template('welcome.html', club=foundClub, competitions=competitions)
    return render_template('booking.html', club=foundClub, competition=foundCompetition)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = get_competition_by_name(request.form.get('competition'))
    club = get_club_by_name(request.form.get('club'))
    if club is None:
        flash("Something went wrong-please try again", "error")
        return redirect(url_for('index'))
    if competition is None:
        flash("Something went wrong-please try again", "error")
        return render_template('welcome.html', club=club, competitions=competitions)

    placesRequired = parse_places(request.form.get('places'))
    if placesRequired is None:
        flash("Please enter a valid number of places (at least 1).", "error")
        return render_template('welcome.html', club=club, competitions=competitions)

    key = (competition['name'], club['name'])
    error = validate_booking(club, competition, placesRequired, bookings.get(key, 0))
    if error:
        flash(error, "error")
        return render_template('welcome.html', club=club, competitions=competitions)

    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
    club['points'] = int(club['points']) - placesRequired
    bookings[key] = bookings.get(key, 0) + placesRequired

    saveData()

    flash('Great-booking complete!', "success")
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/points')
def points():
    ranking = sorted(clubs, key=lambda c: int(c['points']), reverse=True)
    return render_template('points.html', clubs=ranking)


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))
