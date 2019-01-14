from .base_model import BaseModels
from .user_model import UserModels
from .meetup_model import MeetupModels
from .... db_con import init_db
from flask import current_app
from werkzeug.exceptions import BadRequest, NotFound


class RsvpModels(BaseModels):
    """
    This class RsvpModels contains all the methods that
    are used to manipulated rsvps of a specific meetup
    """

    def __init__(self, details={}):
        self.db = init_db()
        self.rsvp_details = details

    def respond_meetup(self, meetup_id):
        """ Responds to a meetup RSVP """

        error = self.check_missing_details(self.rsvp_details)

        if self.check_is_error(error):
            raise BadRequest(error)

        try:

            user = self.fetch_details_by_id(
                "user_id", self.rsvp_details["user"], "users")

            meetup = self.fetch_details_by_id(
                "meetup_id", meetup_id, "meetups")

            status = self.rsvp_details["response"]

        except KeyError as error:
            raise BadRequest("{} is a required data field".format(error))

        if not user:
            raise NotFound("User does not exist. Please register first")

        if not meetup:
            raise NotFound("This Meetup does not exist")

        rsvp = {
            "meetup": meetup_id,
            "user": self.rsvp_details["user"],
            "response": self.rsvp_details["response"]
        }

        database = self.db
        cur = database.cursor()
        query = """ INSERT INTO rsvps (user_id, meetup_id, response) VALUES (%(user)s, %(meetup)s, %(response)s) RETURNING rsvp_id; """
        cur.execute(query, rsvp)

        rsvp_id = cur.fetchone()[0]
        database.commit()
        cur.close()

        resp = {
            "id": rsvp_id,
            "meetup": rsvp["meetup"],
            "topic": meetup[2],
            "status": status
        }

        return self.makeresp(resp, 201)
