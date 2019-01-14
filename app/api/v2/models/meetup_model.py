from datetime import datetime

from .... db_con import init_db
from flask import current_app

from .base_model import BaseModels
from .user_model import UserModels
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized, NotFound, Conflict


class MeetupModels(BaseModels):
    """ 
    This class MeetupModels contain all the methods that
    interact with meetup details and records
    """

    def __init__(self, details={}):
        self.meetup_details = details
        self.db = init_db()

    def create_meetup(self):
        """ Creates a meetup record given data """
        images = []

        try:
            images = self.meetup_details["images"]
        except:
            pass

        try:
            user_id = UserModels().get_user_by_username(
                self.meetup_details["username"])

            meetup = self.fetch_id_if_text_exists(
                "topic", self.meetup_details["topic"], "meetups")

            tags, location, happeningOn = self.meetup_details["tags"], self.meetup_details[
                "location"], self.meetup_details["happeningOn"]
        except KeyError as errkey:
            raise BadRequest("{} is a required key".format(errkey))

        if isinstance(user_id, str):
            # user doesn't exist
            raise Forbidden("This user doesn't exist. Please register first")

        if isinstance(meetup, int):
            # Meetup already exists
            raise Conflict("This meetup already exists")

        try:
            payload = {
                "location": location,
                "images": images,
                "topic": self.meetup_details["topic"],
                "happeningOn": happeningOn,
                "Tags": tags,
                "createdBy": user_id[0]
            }

        except KeyError as missing:
            return self.makeresp("{} can not be empty".format(missing), 400)

        database = self.db
        cur = database.cursor()
        query = """ INSERT INTO meetups (user_id, topic, location, images, tags) VALUES (%(createdBy)s, %(topic)s, %(location)s, %(images)s, %(Tags)s) RETURNING meetup_id; """
        cur.execute(query, payload)

        meetup_id = cur.fetchone()[0]
        database.commit()
        cur.close()

        resp = {
            "topic": payload["topic"],
            "location": payload["location"],
            "happeningOn": self.meetup_details["happeningOn"],
            "id": meetup_id,
            "tags": payload["Tags"],
            "createdBy": self.meetup_details["username"]
        }

        return self.makeresp(resp, 201)

    def fetch_specific_meetup(self, meetup_id):
        """ Fetches a specific meetup record """

        #required = ["id", "topic", "location", "happeningOn", "tags"]

        data = self.fetch_details_by_id("meetup_id", meetup_id, "meetups")

        if not data:
            raise NotFound("This Meetup does not exist")

        username = UserModels().get_username_by_id(data[1])

        resp = {
            "createdBy": username,
            "topic": data[2],
            "location": data[4],
            "happeningOn": "{:%B %d, %Y %I:%M%p}".format(data[3]),
            "tags": data[6]
        }

        return self.makeresp(resp, 200)

    def fetch_upcoming_meetups(self):
        """ Fetches all upcoming meetups """
        dbconn = self.db
        cur = dbconn.cursor()
        cur.execute(""" SELECT * FROM meetups; """)
        data = cur.fetchall()
        resp = []

        for items in data:
            meetup_id, user_id, topic, happening_on, location, images, tags, created_on = items

            user = UserModels().get_username_by_id(user_id)[0]

            meetup = {
                "id": meetup_id,
                "topic": topic,
                "location": location,
                "happeningOn": happening_on,
                "tags": tags,
                "createdBy": user
            }
            resp.append(meetup)

        return self.makeresp(resp, 200)
