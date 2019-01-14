from datetime import datetime
from .base_model import BaseModels
from .user_model import UserModels
from .meetup_model import MeetupModels
from .... db_con import init_db
from flask import current_app
from werkzeug.exceptions import BadRequest, NotFound, Conflict, Forbidden


class QuestionModels(BaseModels):
    """ 
    This class QuestionModels contain all the 
    methods that interact with question details and
    record
    """

    def __init__(self, details={}):
        self.db = init_db()
        self.question_details = details

    def create_question(self):
        """ Creates a question to a meetup record """

        try:
            user = self.fetch_details_by_id(
                "user_id", self.question_details["user"], "users")

            meetup = self.fetch_details_by_id(
                "meetup_id", self.question_details["meetup"], "meetups")

            existing = self.fetch_id_if_text_exists(
                "title", self.question_details["title"], "questions")

            body = self.question_details["body"]

        except KeyError as keyerror:
            raise BadRequest("{} is a required field".format(keyerror))

        if not user:
            raise NotFound("User does not exist. Please register first")

        if not meetup:
            raise NotFound("This Meetup does not exist")

        if not self.check_is_error(existing):
            raise Conflict("This question already exists")

        if self.check_is_error(self.check_missing_details(self.question_details)):
            raise BadRequest(self.check_missing_details(self.question_details))

        question = {
            "createdBy": self.question_details["user"],
            "meetup": self.question_details["meetup"],
            "title": self.question_details["title"],
            "body": body,
            "votes": 0
        }

        database = self.db
        cur = database.cursor()
        query = """ INSERT INTO questions (meetup_id, user_id, title, body) VALUES (%(createdBy)s, %(meetup)s, %(title)s, %(body)s) RETURNING question_id; """
        cur.execute(query, question)

        question_id = cur.fetchone()[0]
        database.commit()
        cur.close()

        return self.makeresp(
            {
                "id": question_id,
                "user": question["createdBy"],
                "meetup": question["meetup"],
                "title": question["title"],
                "body": question["body"]
            }, 201)

    def upvote_question(self, question_id):
        """ 
        Increases the number of votes of a specific 
        question by 1 
        """

        data = self.fetch_details_by_id(
            "question_id", question_id, "questions")

        if not data:
            raise NotFound("Question does not exist")

        try:
            username = self.fetch_details_by_id(
                "user_id", self.question_details["user"], "users")

        except KeyError as keyerr:
            raise BadRequest("{} is a required field".format(keyerr))

        if not username:
            raise NotFound("User does not exist. Please register first")

        if self.check_is_error(self.check_missing_details(self.question_details)):
            raise BadRequest(self.check_missing_details(self.question_details))

        database = self.db
        cur = database.cursor()
        query = """ UPDATE questions SET votes = votes + 1 WHERE question_id = {} RETURNING meetup_id, title, body, votes; """.format(
            question_id)
        cur.execute(query)

        data = cur.fetchone()
        database.commit()
        cur.close()

        return self.makequestionresponse(data)

    def downvote_question(self, question_id):
        """ 
        Decreases the number of votes of a specific 
        question by 1 
        """

        data = self.fetch_details_by_id(
            "question_id", question_id, "questions")

        if not data:
            raise NotFound("Question does not exist")

        try:
            username = self.fetch_details_by_id(
                "user_id", self.question_details["user"], "users")

        except KeyError as keyerr:
            raise BadRequest("{} is a required field".format(keyerr))

        if not username:
            raise NotFound("User does not exist. Please register first")

        if self.check_is_error(self.check_missing_details(self.question_details)):
            raise BadRequest(self.check_missing_details(self.question_details))

        database = self.db
        cur = database.cursor()
        query = """ UPDATE questions SET votes = votes - 1 WHERE question_id = {} RETURNING meetup_id, title, body, votes; """.format(
            question_id)
        cur.execute(query)

        data = cur.fetchone()
        database.commit()
        cur.close()

        return self.makequestionresponse(data)

    def makequestionresponse(self, data):
        """
        This method takes in data and selects what part of 
        data to make response with and responds
        """

        resp = {
            "meetup": data[0],
            "title": data[1],
            "body": data[2],
            "votes": data[3]
        }

        return self.makeresp(resp, 200)
