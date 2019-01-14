from datetime import datetime, timedelta
from flask import current_app
from .... db_con import init_db
from werkzeug.security import generate_password_hash, check_password_hash
from .base_model import BaseModels
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized, Conflict
import re
import jwt


def validator(user):
    for key, value in user.items():

        if not value:
            raise BadRequest("{} is a required field.".format(key))
        elif (key == 'firstname' or key == 'lastname' or key == 'username' or key == "othername") and (len(value) < 4 or len(value) > 15):
            raise BadRequest(
                "{} should be 4-15 characters long".format(key))

    if not re.search(r'\w+[.|\w]\w+@\w+[.]\w+[.|\w+]\w+', user["email"]):
        raise BadRequest("Please enter a valid {}.".format(key))

    if not (len(re.findall(r'[A-Z]', user["password"])) > 0 and len(re.findall(
            r'[a-z]', user["password"])) > 0 and len(re.findall(r'[0-9]', user["password"])) > 0 and len(re.findall(r'[@#$]', user["password"])) > 0):
        raise BadRequest(
            "Password should contain atleast one number, uppercase, lowercase and special character")


class UserModels(BaseModels):
    """
    This class UserModels contains the methods used when
    interacting with user user
    """

    def __init__(self, details={}):
        self.user_details = details
        self.db = init_db()

    def get_user_by_username(self, username):
        """ Fetches a user's details from the database given a username """

        database = self.db

        cur = database.cursor()
        cur.execute(
            """ SELECT user_id ,firstname, lastname, password, registered_on FROM users WHERE username = '{}'; """.format(username))

        data = cur.fetchone()

        cur.close()

        if not data:
            return "User not Found"

        return data

    def get_username_by_id(self, user_id):
        """ returns a username given the id """

        try:
            cur = self.db.cursor()
            cur.execute(
                """ SELECT username FROM users WHERE user_id = {};""".format(user_id))
            data = cur.fetchone()
            cur.close()

            return data

        except Exception:
            return "Not Found"

    def check_exists(self, username):
        """ Checks if the record exists """
        cur = self.db.cursor()

        cur.execute(
            """ SELECT username FROM users WHERE username = '%s';""" % (username))

        return cur.fetchone() is not None

    def register_user(self):
        """ Validates user user before adding them """

        try:

            validator(self.user_details)

            user = {
                "firstname": self.user_details["firstname"],
                "lastname": self.user_details["lastname"],
                "othername": self.user_details["othername"],
                "email": self.user_details["email"],
                "phoneNumber": self.user_details["phoneNumber"],
                "username": self.user_details["username"],
                "registered": datetime.now(),
                "password": generate_password_hash(self.user_details["password"]),
                "isAdmin": False
            }

        except KeyError as keymiss:
            raise BadRequest(
                "{} should be present in the provided data".format(keymiss))

        if self.check_exists(self.user_details["username"]):
            raise Conflict("This username already exists")

        database = self.db
        cur = database.cursor()
        query = """INSERT INTO users (firstname, lastname, othername, email, phone_number, username, password) \
            VALUES ( %(firstname)s, %(lastname)s,\
            %(othername)s, %(email)s, %(phoneNumber)s, %(username)s, %(password)s) RETURNING user_id;
            """

        cur.execute(query, user)
        user_id = cur.fetchone()[0]
        database.commit()
        cur.close()

        resp = {
            "id": user_id,
            "name": "{} {}".format(user["lastname"], user["firstname"])
        }

        return self.makeresp(resp, 201)

    def fetch_users(self):
        """ Returns all the users """
        database = self.db

        cur = database.cursor()
        cur.execute(
            """SELECT user_id, firstname, lastname FROM users;""")

        data = cur.fetchall()

        cur.close()

        resp = []

        for user in data:
            try:
                user_id, first_name, last_name = user
                final = {
                    "userId": user_id,
                    "user": "%s %s" % (last_name, first_name)
                }
                resp.append(final)
            except:
                pass

        return self.makeresp({
            "users": resp
        }, 200)

    def login_user(self):
        """ Logins in a user given correct user credentials """

        user = self.get_user_by_username(self.user_details[0])

        if isinstance(user, str):

            raise NotFound("Please check your username")

        user_id, firstname, lastname, password, registered = user

        if not check_password_hash(password, self.user_details[1]):

            raise Unauthorized("Please check your password")

        resp = {

            "name": "{} {}".format(lastname, firstname),
            "memberSince": registered,
            "message": "You have been logged in successfully"
        }

        return self.makeresp(resp, 200)
