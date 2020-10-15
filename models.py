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

    def get_show_info(self, artist=None, venue=None):
        self.artist = artist if artist else Artist.query.get(self.artist_id)
        data = {
            "artist_id": self.artist.id,
            "artist_name": self.artist.name,
            "artist_image_link": self.artist.image_link,
            "start_time": str(self.start_time),
        }
        if not venue:
            venue = venue if venue else Venue.query.get(self.venue_id)
            data["venue_image_link"] = venue.image_link

        return data


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

    def num_upcoming_shows(self):
        return (
            self.query.join(Show)
            .filter_by(venue_id=self.id)
            .filter(Show.start_time > datetime.now())
            .count()
        )

    def get_upcoming_shows(self):
        return Show.query.filter_by(venue_id=self.id).filter(
            Show.start_time > datetime.now()
        )

    def num_past_shows(self):
        return (
            self.query.join(Show)
            .filter_by(venue_id=self.id)
            .filter(Show.start_time < datetime.now())
            .count()
        )

    def get_past_shows(self):
        return Show.query.filter_by(venue_id=self.id).filter(
            Show.start_time < datetime.now()
        )

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

    def num_upcoming_shows(self):
        return (
            self.query.join(Show)
            .filter_by(artist_id=self.id)
            .filter(Show.start_time > datetime.now())
            .count()
        )

    def get_upcoming_shows(self):
        return Show.query.filter_by(artist_id=self.id).filter(
            Show.start_time > datetime.now()
        )

    def num_past_shows(self):
        return (
            self.query.join(Show)
            .filter_by(artist_id=self.id)
            .filter(Show.start_time < datetime.now())
            .count()
        )

    def get_past_shows(self):
        return Show.query.filter_by(artist_id=self.id).filter(
            Show.start_time < datetime.now()
        )

    def get_shows(self):
        return Show.query.filter_by(artist_id=self.id).all()


# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
