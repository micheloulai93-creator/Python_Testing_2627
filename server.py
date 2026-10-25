import json
from datetime import datetime
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

# Places deja reservees : {(nom_competition, nom_club): nombre}
bookings = {}


def get_club_by_email(email):
    """Retourne le club correspondant à l'email, ou None s'il n'existe pas."""
    return next((c for c in clubs if c['email'] == email), None)


def get_club_by_name(name):
    """Retourne le club portant ce nom, ou None."""
    return next((c for c in clubs if c['name'] == name), None)


def get_competition_by_name(name):
    """Retourne la compétition portant ce nom, ou None."""
    return next((c for c in competitions if c['name'] == name), None)


def is_competition_over(competition, now=None):
    """True si la date de la compétition est passée (date illisible = considérée passée)."""
    now = now or datetime.now()
    try:
        date = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    except (KeyError, ValueError):
        return True
    return date < now


@app.context_processor
def inject_helpers():
    """Rend is_competition_over() utilisable dans les templates (is_over)."""
    return {'is_over': is_competition_over}


def parse_places(raw_value):
    """Convertit la saisie en entier strictement positif, ou retourne None si invalide."""
    try:
        value = int(str(raw_value).strip())
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def validate_booking(club, competition, places_required, already_booked=0):
    """Vérifie qu'une réservation est autorisée.

    already_booked : places déjà réservées par ce club dans cette compétition.
    Retourne un message d'erreur (str) si elle est refusée, sinon None.
    """
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

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = get_club_by_email(request.form.get('email', ''))
    if club is None:
        flash("Sorry, that email was not found.", "error")
        return redirect(url_for('index'))
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
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
    return render_template('booking.html',club=foundClub,competition=foundCompetition)


@app.route('/purchasePlaces',methods=['POST'])
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
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    club['points'] = int(club['points'])-placesRequired
    bookings[key] = bookings.get(key, 0) + placesRequired
    flash('Great-booking complete!', "success")
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))