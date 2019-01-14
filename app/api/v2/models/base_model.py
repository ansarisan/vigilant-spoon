from .... db_con import init_db
from flask import current_app

users, meetups, questions, rsvps = [], [], [], []


class BaseModels(object):
    """ 
    This class contains methods that are common to all other
    models
    """

    def makeresp(self, payload, status_code):
        """ Returns user details if found and message if not """

        if isinstance(payload, str):
            return {
                "status": status_code,
                "error": payload
            }
        if not isinstance(payload, list):
            return {
                "status": status_code,
                "data": [payload]
            }

        return {
            "status": status_code,
            "data": payload
        }

    def fetch_id_if_text_exists(self, item_name, text, table):
        # select meetup_id from meetups where topic = 'This is topic';
        singular = table[:-1] + '_id'

        cur = init_db().cursor()
        cur.execute(""" SELECT {} FROM {} WHERE lower({}) = '{}'; """.format(
            singular, table, item_name, text.lower()))
        data = cur.fetchone()

        if not data:
            # no meetup or question found with that text
            return " Text not found"

        return data[0]

    def fetch_details_by_id(self, item_name, item_id, table):
        """ returns a username given the id """

        try:
            cur = init_db().cursor()
            cur.execute(
                """ SELECT * FROM {} WHERE {} = {}; """.format(table, item_name, int(item_id)))
            data = cur.fetchone()
            cur.close()

            #response = [item for item in data if item in required]

            return data

        except Exception:
            return "Not Found"

    def check_missing_details(self, details):
        """ 
        Checks if required data exists in the provided details
        and returns missing values or [] if none
        """

        for key, value in details.items():
            if not value:
                return "{} is a required field".format(key)

    def check_is_error(self, data):
        """ Checks if data passed to it is of type string """

        return isinstance(data, str)
