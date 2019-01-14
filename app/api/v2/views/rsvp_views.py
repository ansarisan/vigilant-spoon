from flask import Flask, request, jsonify
from .. import version2
from .. models.rsvp_model import RsvpModels



@version2.route("/meetups/<int:meetup_id>/rsvps", methods=["POST"])
def respond_meetup(meetup_id):
    """ Responds to meetup RSVP """

    details = request.get_json()

    resp = RsvpModels(details).respond_meetup(meetup_id)

    return jsonify(resp), resp["status"]
