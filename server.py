import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

MAX_PLACES_PER_CLUB = 12


def get_club_by_email(email):
    """Retourne le club correspondant à l'email, ou None s'il n'existe pas."""
    return next((c for c in clubs if c['email'] == email), None)


def get_club_by_name(name):
    """Retourne le club portant ce nom, ou None."""
    return next((c for c in clubs if c['name'] == name), None)


def get_competition_by_name(name):
    """Retourne la compétition portant ce nom, ou None."""
    return next((c for c in competitions if c['name'] == name), None)


def parse_places(raw_value):
    """Convertit la saisie en entier strictement positif, ou retourne None si invalide."""
    try:
        value = int(str(raw_value).strip())
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def validate_booking(club, competition, places_required):
    """Vérifie qu'une réservation est autorisée.

    Retourne un message d'erreur (str) si elle est refusée, sinon None.
    """
    if places_required > MAX_PLACES_PER_CLUB:
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

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = get_club_by_email(request.form.get('email', ''))
    if club is None:
        flash("Sorry, that email was not found.")
        return redirect(url_for('index'))
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = get_club_by_name(club)
    foundCompetition = get_competition_by_name(competition)
    if foundClub is None:
        flash("Something went wrong-please try again")
        return redirect(url_for('index'))
    if foundCompetition is None:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=foundClub, competitions=competitions)
    return render_template('booking.html',club=foundClub,competition=foundCompetition)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = get_competition_by_name(request.form.get('competition'))
    club = get_club_by_name(request.form.get('club'))
    if club is None:
        flash("Something went wrong-please try again")
        return redirect(url_for('index'))
    if competition is None:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)
    placesRequired = parse_places(request.form.get('places'))
    if placesRequired is None:
        flash("Please enter a valid number of places (at least 1).")
        return render_template('welcome.html', club=club, competitions=competitions)
    error = validate_booking(club, competition, placesRequired)
    if error:
        flash(error)
        return render_template('welcome.html', club=club, competitions=competitions)
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    club['points'] = int(club['points'])-placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))