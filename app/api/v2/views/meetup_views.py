from flask import Flask, request, jsonify
from .. import version2
from .. models.meetup_model import MeetupModels


@version2.route("/meetups", methods=["POST"])
def post_new_meetup():
    """ Creates a new meetup record if details provided"""

    resp = MeetupModels(request.get_json()).create_meetup()

    return jsonify(resp), resp["status"]

@version2.route("/meetups/<int:meetup_id>", methods=["GET"])
def fetch_specific_meetup(meetup_id):
    """ Fetches a specific meetup record """
        
    return jsonify(MeetupModels().fetch_specific_meetup(meetup_id)), MeetupModels().fetch_specific_meetup(meetup_id)["status"]


@version2.route("/meetups/upcoming", methods=["GET"])
def fetch_upcoming_meetup():
    """ Fetches all upcoming meetup records """
   
    return jsonify(MeetupModels().fetch_upcoming_meetups()), MeetupModels().fetch_upcoming_meetups()["status"]