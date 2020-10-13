# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import ARRAY
import logging
from logging import Formatter, FileHandler
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = "venue"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(ARRAY(db.String))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    shows = db.relationship("Show", backref="venue", lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = "artist"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String)
    genres = db.Column(ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    shows = db.relationship("Show", backref="artist", lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = "show"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    try:
        if venues := Venue.query.all():
            locations = sorted(set((v.city, v.state) for v in venues))
            for city, state in locations:
                group_data = {"city": city, "state": state, "venues": []}
                for venue in venues:
                    if venue.city == city and venue.state == state:
                        group_data["venues"].append(
                            {"id": venue.id, "name": venue.name}
                        )
                data.append(group_data)
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search = request.form.get("search_term", "")
    response = {}
    try:
        if venues := Venue.query.filter(Venue.name.ilike(f"%{search}%")).all():
            response["count"] = len(venues)
            response["data"] = []
            for v in venues:
                response["data"].append(
                    {
                        "id": v.id,
                        "name": v.name,
                        "num_upcoming_shows": 0,
                    }
                )
        else:
            response["count"] = 0
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=search,
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data = {}
    error = False
    try:
        venue = Venue.query.get(venue_id)
        if venue:
            data["id"] = venue.id
            data["name"] = venue.name
            data["genres"] = venue.genres
            data["city"] = venue.city
            data["state"] = venue.state
            data["phone"] = venue.phone
            data["website"] = venue.website
            data["facebook_link"] = venue.facebook_link
            data["seeking_talent"] = venue.seeking_talent
            data["seeking_description"] = venue.seeking_description
            data["image_link"] = venue.image_link
    except:
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # on successful db insert, flash success
    if error or not data:
        flash(f"An error occurred. Venue could not be listed.")
        return render_template("pages/home.html")

    return render_template("pages/show_venue.html", venue=data)


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    data = request.form.to_dict()
    genres = request.form.to_dict(flat=False)["genres"]
    seeking = True if data.get("seeking_talent") else False
    try:
        venue = Venue(
            name=data["name"],
            address=data["address"],
            city=data["city"],
            state=data["state"],
            phone=data["phone"],
            website=data["website_link"],
            facebook_link=data["facebook_link"],
            image_link=data["image_link"],
            genres=genres,
            seeking_talent=seeking,
            seeking_description=data["seeking_description"],
        )
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # on successful db insert, flash success
    if error:
        flash(f"An error occurred. Venue '{data['name']}' could not be listed.")
    else:
        flash(f"Venue '{data['name']}' was successfully listed!")
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g.,
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = None
    data = None
    try:
        if venue := Venue.query.get(venue_id):
            form = VenueForm(obj=venue)
            data = {
                "id": venue.id,
                "name": venue.name,
                "genres": venue.genres,
                "address": venue.address,
                "city": venue.city,
                "state": venue.state,
                "phone": venue.phone,
                "website": venue.website,
                "facebook_link": venue.facebook_link,
                "seeking_talent": venue.seeking_talent,
                "seeking_description": venue.seeking_description,
                "image_link": venue.image_link,
            }
    except:
        print(sys.exc_info())
    finally:
        db.session.close()

    # TODO: populate form with values from venue with ID <venue_id>
    if data:
        return render_template("forms/edit_venue.html", form=form, venue=data)
    else:
        return redirect(url_for("index"))


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    data = request.form.to_dict()
    data["genres"] = request.form.to_dict(flat=False)["genres"]
    seeking = True if data.get("seeking_talent") else False
    try:
        if venue := Venue.query.get(venue_id):
            venue.name = data["name"]
            venue.genres = data["genres"]
            venue.address = data["address"]
            venue.city = data["city"]
            venue.state = data["state"]
            venue.phone = data["phone"]
            venue.website = data["website_link"]
            venue.facebook_link = data["facebook_link"]
            venue.image_link = data["image_link"]
            venue.seeking_talent = seeking
            venue.seeking_description = data["seeking_description"]
            db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # on successful db update, flash success
    if error:
        flash(f"An error occurred. Venue '{data['name']}' could not be updated.")
    else:
        flash(f"Venue '{data['name']}' was successfully updated!")

    return redirect(url_for("show_venue", venue_id=venue_id))


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # TODO: BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    error = False
    venue_name = ""
    try:
        venue = Venue.query.get(venue_id)
        if venue:
            venue_name = venue.name
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # on successful db insert, flash success
    if error:
        flash(f"An error occurred. Venue could not be listed.")
    else:
        flash(f"Venue '{venue_name}' was successfully removed!")
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g.,
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return redirect(url_for("index"))


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # TODO: replace with real data returned from querying the database
    data = []
    try:
        artists = Artist.query.all()
        if artists:
            for a in artists:
                data.append(
                    {
                        "id": a.id,
                        "name": a.name,
                        "num_upcoming_shows": 0,
                    }
                )
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search = request.form.get("search_term", "")
    response = {}
    try:
        if artists := Artist.query.filter(Artist.name.ilike(f"%{search}%")).all():
            response["count"] = len(artists)
            response["data"] = []
            for a in artists:
                response["data"].append(
                    {
                        "id": a.id,
                        "name": a.name,
                        "num_upcoming_shows": 0,
                    }
                )
        else:
            response["count"] = 0
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=search,
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data = {}
    error = False
    try:
        artist = Artist.query.get(artist_id)
        if artist:
            data["id"] = artist.id
            data["name"] = artist.name
            data["genres"] = artist.genres
            data["city"] = artist.city
            data["state"] = artist.state
            data["phone"] = artist.phone
            data["website"] = artist.website
            data["facebook_link"] = artist.facebook_link
            data["seeking_venue"] = artist.seeking_venue
            data["seeking_description"] = artist.seeking_description
            data["image_link"] = artist.image_link
    except:
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # on successful db insert, flash success
    if error or not data:
        flash(f"An error occurred. Artist could not be listed.")
        return render_template("pages/home.html")

    return render_template("pages/show_artist.html", artist=data)


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Artist record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    data = request.form.to_dict()
    genres = request.form.to_dict(flat=False)["genres"]
    seeking = True if data.get("seeking_venue") else False
    try:
        artist = Artist(
            name=data["name"],
            genres=genres,
            city=data["city"],
            state=data["state"],
            phone=data["phone"],
            website=data["website_link"],
            facebook_link=data["facebook_link"],
            image_link=data["image_link"],
            seeking_venue=seeking,
            seeking_description=data["seeking_description"],
        )
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # on successful db insert, flash success
    if error:
        flash(f"An error occurred. Artist '{data['name']}' could not be listed.")
    else:
        flash(f"Artist '{data['name']}' was successfully listed!")
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g.,
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = None
    data = None
    try:
        if artist := Artist.query.get(artist_id):
            form = ArtistForm(obj=artist)
            data = {
                "id": artist.id,
                "name": artist.name,
                "genres": artist.genres,
                "city": artist.city,
                "state": artist.state,
                "phone": artist.phone,
                "website": artist.website,
                "facebook_link": artist.facebook_link,
                "seeking_venue": artist.seeking_venue,
                "seeking_description": artist.seeking_description,
                "image_link": artist.image_link,
            }
    except:
        print(sys.exc_info())
    finally:
        db.session.close()

    # TODO: populate form with fields from artist with ID <artist_id>
    if data:
        return render_template("forms/edit_artist.html", form=form, artist=data)
    else:
        return redirect(url_for("index"))


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    data = request.form.to_dict()
    data["genres"] = request.form.to_dict(flat=False)["genres"]
    seeking = True if data.get("seeking_venue") else False
    try:
        if artist := Artist.query.get(artist_id):
            artist.name = data["name"]
            artist.genres = data["genres"]
            artist.city = data["city"]
            artist.state = data["state"]
            artist.phone = data["phone"]
            artist.website = data["website_link"]
            artist.facebook_link = data["facebook_link"]
            artist.image_link = data["image_link"]
            artist.seeking_venue = seeking
            artist.seeking_description = data["seeking_description"]
            db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # on successful db update, flash success
    if error:
        flash(f"An error occurred. Artist '{data['name']}' could not be updated.")
    else:
        flash(f"Artist '{data['name']}' was successfully updated!")

    return redirect(url_for("show_artist", artist_id=artist_id))
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g.,
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route("/artists/<artist_id>", methods=["DELETE"])
def delete_artist(artist_id):
    # TODO: Complete this endpoint for taking a artist_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # TODO: BONUS CHALLENGE: Implement a button to delete a Artist on an Artist Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    error = False
    artist_name = ""
    try:
        artist = Artist.query.get(artist_id)
        if artist:
            artist_name = artist.name
        db.session.delete(artist)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # on successful db insert, flash success
    if error:
        flash(f"An error occurred. Artist could not be listed.")
    else:
        flash(f"Artist '{artist_name}' was successfully removed!")
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g.,
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return redirect(url_for("index"))


#  Shows
#  ----------------------------------------------------------------
@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = [
        {
            "venue_id": 1,
            "venue_name": "The Musical Hop",
            "artist_id": 4,
            "artist_name": "Guns N Petals",
            "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
            "start_time": "2019-05-21T21:30:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 5,
            "artist_name": "Matt Quevedo",
            "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
            "start_time": "2019-06-15T23:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-01T20:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-08T20:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-15T20:00:00.000Z",
        },
    ]
    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash("Show was successfully listed!")
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.route("/shows/<show_id>", methods=["DELETE"])
def delete_show(show_id):
    # TODO: Complete this endpoint for taking a show_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # TODO: BONUS CHALLENGE: Implement a button to delete a Show on a Show Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Utils
#  ----------------------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
