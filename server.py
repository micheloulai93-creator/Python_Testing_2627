import json
import csv
import io
from datetime import datetime

from flask import (Flask, flash, redirect, render_template, request,
                   session, url_for, Response)


def loadClubs():
    with open('clubs.json') as c:
        return json.load(c)['clubs']


def loadCompetitions():
    with open('competitions.json') as comps:
        return json.load(comps)['competitions']


def loadBookings():
    try:
        with open('bookings.json') as b:
            return json.load(b)
    except FileNotFoundError:
        return {}


def saveData():
    with open('clubs.json', 'w') as c:
        json.dump({'clubs': clubs}, c, indent=4)
    with open('competitions.json', 'w') as comps:
        json.dump({'competitions': competitions}, comps, indent=4)
    with open('bookings.json', 'w') as b:
        json.dump(bookings, b, indent=4)


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()
bookings = loadBookings()

MAX_PLACES_PER_CLUB = 12


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
    else:
        if 'email' not in session:
            return redirect(url_for('index'))
        club = get_club_by_email(session['email'])
        if club is None:
            return redirect(url_for('index'))

    competitions_triees = sorted(competitions, key=lambda x: x['date'],
                                 reverse=True)
    a_venir = [c for c in competitions_triees if not is_competition_over(c)]
    passees = [c for c in competitions_triees if is_competition_over(c)]
    competitions_finales = a_venir + passees

    favoris = club.get('favorites', [])

    return render_template('welcome.html', club=club,
                           competitions=competitions_finales, favoris=favoris)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    if 'email' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('index'))

    foundClub = get_club_by_name(club)
    foundCompetition = get_competition_by_name(competition)

    if foundClub is None:
        flash("Something went wrong-please try again", "error")
        return redirect(url_for('showSummary'))

    if foundClub['email'] != session['email']:
        flash("You can only book for your own club.", "error")
        return redirect(url_for('showSummary'))

    if foundCompetition is None:
        flash("Something went wrong-please try again", "error")
        return redirect(url_for('showSummary'))

    if is_competition_over(foundCompetition):
        flash("This competition is already over.", "error")
        return redirect(url_for('showSummary'))

    return render_template('booking.html', club=foundClub,
                           competition=foundCompetition)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    if 'email' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('index'))

    club = get_club_by_email(session['email'])
    competition = get_competition_by_name(request.form.get('competition'))

    if club is None or competition is None:
        flash("Something went wrong-please try again", "error")
        return redirect(url_for('showSummary'))

    placesRequired = parse_places(request.form.get('places'))
    if placesRequired is None:
        flash("Please enter a valid number of places (at least 1).", "error")
        return redirect(url_for('showSummary'))

    key = "%s|%s" % (competition['name'], club['name'])
    error = validate_booking(club, competition, placesRequired,
                             bookings.get(key, 0))
    if error:
        flash(error, "error")
        return redirect(url_for('showSummary'))

    competition['numberOfPlaces'] = (int(competition['numberOfPlaces'])
                                     - placesRequired)
    club['points'] = int(club['points']) - placesRequired
    bookings[key] = bookings.get(key, 0) + placesRequired

    saveData()

    flash('Great-booking complete! %d places booked.' % placesRequired,
          "success")
    return redirect(url_for('showSummary'))


@app.route('/points')
def points():
    ranking = sorted(clubs, key=lambda c: int(c['points']), reverse=True)
    return render_template('points.html', clubs=ranking)


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))


@app.route('/history')
def history():
    if 'email' not in session:
        return redirect(url_for('index'))

    club = get_club_by_email(session['email'])
    historique = []

    for key, places in bookings.items():
        comp_name, club_name = key.split('|')
        if club_name == club['name']:
            comp = get_competition_by_name(comp_name)
            if comp:
                historique.append({
                    'competition': comp_name,
                    'date': comp['date'],
                    'places': places
                })

    historique = sorted(historique, key=lambda x: x['date'])
    return render_template('history.html', club=club, historique=historique)


@app.route('/export-csv')
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Club', 'Points'])

    ranking = sorted(clubs, key=lambda c: int(c['points']), reverse=True)
    for c in ranking:
        writer.writerow([c['name'], c['points']])

    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers["Content-Disposition"] = (
        "attachment; filename=points_clubs.csv"
    )
    return response


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'email' not in session:
        return redirect(url_for('index'))

    club = get_club_by_email(session['email'])

    if request.method == 'POST':
        new_email = request.form.get('email')
        if new_email and new_email != club['email']:
            if get_club_by_email(new_email) is not None:
                flash("This email is already used by another club.", "error")
            else:
                club['email'] = new_email
                session['email'] = new_email
                saveData()
                flash("Profile updated successfully.", "success")
                return redirect(url_for('profile'))

    return render_template('profile.html', club=club)


@app.route('/toggle-favorite/<competition_name>')
def toggle_favorite(competition_name):
    if 'email' not in session:
        return redirect(url_for('index'))

    club = get_club_by_email(session['email'])
    if 'favorites' not in club:
        club['favorites'] = []

    if competition_name in club['favorites']:
        club['favorites'].remove(competition_name)
    else:
        club['favorites'].append(competition_name)

    saveData()
    return redirect(url_for('showSummary'))