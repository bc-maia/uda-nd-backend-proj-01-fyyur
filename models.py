# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime


db = SQLAlchemy()


class Show(db.Model):
    __tablename__ = "show"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)


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
    # DONE: implement any missing fields, as a database migration using Flask-Migrate

    def get_upcoming_shows(self) -> list:
        shows = (
            db.session.query(Artist, Show)
            .join(Show)
            .join(Venue)
            .filter(
                Show.venue_id == self.id,
                Show.artist_id == Artist.id,
                Show.start_time > datetime.now(),
            )
            .all()
        )
        return formatted_shows(shows)

    def get_past_shows(self) -> list:
        shows = (
            db.session.query(Artist, Show)
            .join(Show)
            .join(Venue)
            .filter(
                Show.venue_id == self.id,
                Show.artist_id == Artist.id,
                Show.start_time < datetime.now(),
            )
            .all()
        )
        return formatted_shows(shows)

    def get_shows(self):
        return Show.query.filter_by(venue_id=self.id).all()


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
    # DONE: implement any missing fields, as a database migration using Flask-Migrate

    def get_upcoming_shows(self) -> list:
        shows = (
            db.session.query(Artist, Show)
            .join(Show)
            .join(Venue)
            .filter(
                Show.venue_id == Venue.id,
                Show.artist_id == self.id,
                Show.start_time > datetime.now(),
            )
            .all()
        )
        return formatted_shows(shows, venue_img=True)

    def get_past_shows(self) -> list:
        shows = (
            db.session.query(Artist, Show)
            .join(Show)
            .join(Venue)
            .filter(
                Show.venue_id == Venue.id,
                Show.artist_id == self.id,
                Show.start_time < datetime.now(),
            )
            .all()
        )
        return formatted_shows(shows, venue_img=True)

    def get_shows(self):
        return Show.query.filter_by(artist_id=self.id).all()


def formatted_shows(shows: list, venue_img=False) -> list:
    data = []
    for artist, show in shows:
        event = {
            "artist_id": artist.id,
            "artist_name": artist.name,
            "start_time": str(show.start_time),
        }
        if venue_img:
            event["venue_image_link"] = show.venue.image_link
        else:
            event["artist_image_link"] = artist.image_link

        data.append(event)

    return data


# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
