#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Venue, Artist, Show
from seed import seed as seeder
from pprint import pprint
from sqlalchemy.orm import load_only
from datetime import date
import sys
from flask_wtf.csrf import CSRFProtect

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
csrf = CSRFProtect()

def create_app(db):  
  app = Flask(__name__)
  moment = Moment(app)
  app.config.from_object('config')
  db.init_app(app)
  migrate = Migrate(app, db)
  csrf.init_app(app)

  return app

app = create_app(db)

@app.cli.command()
def seed():
  seeder(db)

def with_context():
  app.app_context().push()
  return app 

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# DTOS
#----------------------------------------------------------------------------#

def sortShows(shows):
  data = {
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  for show in shows:
    print(show.venue)
    if (show.start_time).strftime("%Y/%M/%D, %H:%M:%S") > (datetime.now()).strftime("%Y/%M/%D, %H:%M:%S"):
      data["upcoming_shows"].append(create_show_dto(show))
      data["upcoming_shows_count"] = len(data["upcoming_shows"])
    else:
      data["past_shows"].append(create_show_dto(show))
      data["past_shows_count"] = len(data["past_shows"])
  return data

def create_show_dto(show):
  return {
    "venue_id": show.venue.id,
    "venue_name": show.venue.name,
    "artist_id": show.artist.id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "venue_image_link": show.venue.image_link,
    "start_time": str(show.start_time)
  }

def create_artist_dto(artist):
  data = {
    "id": artist.id,
    "genres": artist.genres, 
    "name": artist.name, 
    "city": artist.city, 
    "state": artist.state, 
    "phone": artist.phone, 
    "genres": artist.genres, 
    "image_link": artist.image_link, 
    "website": artist.website, 
    "facebook_link": artist.facebook_link, 
    "seeking_venue": artist.seeking_venue, 
    "seeking_description": artist.seeking_description, 
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }

  shows = sortShows(artist.shows)
  
  return {
    **data,
    **shows
  }

def create_venue_dto(venue):
  data = {
    "id": venue.id,
    "genres": venue.genres,
    "name": venue.name,
    "city": venue.city,
    "state": venue.state,
    "address": venue.address,
    "phone": venue.phone,
    "image_link": venue.image_link,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }

  shows = sortShows(venue.shows)
  
  return {
    **data,
    **shows
  }

#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = {}
  venues = Venue.query.all()
  for venue in venues:
    if not venue.city in data:
      data[venue.city] = {
        "city": venue.city,
        "state": venue.state,
        "venues": []
      }

    data[venue.city]['venues'].append(venue)

  data=[*data.values()]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['GET'])
def search_venues():
  search_term = request.args.get('search_term')
  data = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  response={
    "count": len(data),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  data = create_venue_dto(venue)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  error = False
  if (form.validate()):
    data = {
      "genres": form.genres.data,
      "name": form.name.data,
      "city": form.city.data,
      "state": form.state.data,
      "address": form.address.data,
      "phone": form.phone.data,
      "image_link": form.image_link.data,
      "website": form.website_link.data,
      "facebook_link": form.facebook_link.data,
      "seeking_talent": 'seeking_venue' in form if True else False,
      "seeking_description": form.seeking_description.data
    }
    try:
      venue = Venue(**data)
      db.session.add(venue)
      db.session.commit()
    except Exception as e:
      error = True
      print(e)
      print(sys.exc_info())
      db.session.rollback()
    finally:
      db.session.close()
  else:
    error = True

  if error:
   
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    return render_template('forms/new_venue.html', form=form)

  flash('Venue ' + form.name.data + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    db.session.delete(venue)
    db.session.commit()
  except: 
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist).options(load_only(Artist.id, Artist.name))
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['GET'])
def search_artists():
  search_term = request.args.get('search_term')
  data = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  
  response={
    "count": len(data),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  dto = create_artist_dto(artist)
  return render_template('pages/show_artist.html', artist=dto)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  form = ArtistForm(state=artist.state, genres=artist.genres, seeking_venue=artist.seeking_venue)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  form = ArtistForm(request.form)
  error = False
  if (form.validate()):
    try:
      artist = Artist.query.filter_by(id=artist_id).one()
      artist.name = form.name.data,
      artist.city = form.city.data,
      artist.state = form.state.data,
      artist.genres = [str(genre) for genre in form.genres.data]
      artist.phone = form.phone.data,
      artist.facebook_link = form.facebook_link.data,
      artist.image_link = form.image_link.data,
      db.session.add(artist)
      db.session.commit()
    except Exception as e:
      error = True
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
      print(sys.exc_info())
    finally:
      db.session.close()
  else:
    error = True

  if (error):
    return redirect(url_for('edit_artist', artist_id=artist_id))
  
  flash('Edited artist ' + request.form['name'] + ' successfuly')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  form = VenueForm(**create_venue_dto(venue), website_link=venue.website)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  error = False
  if (form.validate()):
    try:
      venue = Venue.query.filter_by(id=venue_id).first_or_404()
      venue.name = form.name.data
      venue.genres = form.genres.data
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.image_link = form.image_link.data
      venue.website = form.website_link.data
      venue.facebook_link = form.facebook_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      db.session.add(venue)
      db.session.commit()
    except:
      db.session.rollback()
      error=True
    finally:
      db.session.close()
  else:
    error=True

  if (error):
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
    redirect(url_for('edit_venue', venue_id=venue_id))
  flash('Artist ' + request.form['name'] + ' updated.')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  error = False

  if (form.validate()):
    try:
      data = {
        "name": form.name.data,
        "city": form.city.data,
        "facebook_link": form.facebook_link.data,
        "image_link": form.image_link.data,
        "website": form.website_link.data,
        "genres": form.genres.data,
        "name": form.name.data,
        "phone": form.phone.data,
        "state": form.state.data,
        "seeking_venue": 'seeking_venue' in form if True else False,
        "seeking_description": form['seeking_description'].data
      }

      artist = Artist(**data)
      db.session.add(artist)
      db.session.commit()
    except:
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
  else:
    error = True

  if (error):
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.', 'danger')
    #flash(form.errors.items(), 'danger')
    return render_template('forms/new_artist.html', form=form)
  else:
    flash('Created artist ' + form['name'].data + ' successfully')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows: 
    data.append(create_show_dto(show))
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  artist_id = request.form['artist_id']
  start_time = request.form['start_time']
  venue_id = request.form['venue_id']

  try:
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)


