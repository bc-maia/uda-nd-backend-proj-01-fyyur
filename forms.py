from datetime import datetime
from flask_wtf import FlaskForm
from sqlalchemy.sql.sqltypes import Boolean
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField
from wtforms.fields.core import BooleanField
from wtforms.validators import DataRequired, AnyOf, URL
from enums import Genres, States


class ShowForm(FlaskForm):
    artist_id = StringField("artist_id")
    venue_id = StringField("venue_id")
    start_time = DateTimeField(
        "start_time", validators=[DataRequired()], default=datetime.today()
    )


class VenueForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    city = StringField("city", validators=[DataRequired()])
    state = SelectField(
        "state",
        validators=[DataRequired()],
        choices=States.options(),
    )
    address = StringField("address", validators=[DataRequired()])
    seeking_talent = BooleanField("seeking_talent")
    seeking_description = StringField(
        "seeking_description", validators=[DataRequired()]
    )
    phone = StringField("phone")
    genres = SelectMultipleField(
        # TODO implement enum restriction
        "genres",
        validators=[DataRequired()],
        choices=Genres.options(),
    )
    image_link = StringField("image_link")
    facebook_link = StringField("facebook_link", validators=[URL()])
    website_link = StringField("website_link", validators=[URL()])


class ArtistForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    city = StringField("city", validators=[DataRequired()])
    state = SelectField(
        "state",
        validators=[DataRequired()],
        choices=States.options(),
    )
    phone = StringField(
        # TODO implement validation logic for state
        "phone"
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        "genres",
        validators=[DataRequired()],
        choices=Genres.options(),
    )
    website_link = StringField("website_link", validators=[URL()])
    facebook_link = StringField("facebook_link", validators=[URL()])
    image_link = StringField("image_link")
    seeking_venue = BooleanField("seeking_venue")
    seeking_description = StringField(
        "seeking_description", validators=[DataRequired()]
    )


# TODO IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM
