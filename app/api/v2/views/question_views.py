from flask import Flask, request, jsonify
from .. import version2
from .. models.question_model import QuestionModels


@version2.route("/questions", methods=["POST"])
def create_question():
    """ Creates a question for a specific meetup """

    details = request.get_json()

    resp = QuestionModels(details).create_question()

    return jsonify(resp), resp["status"]


@version2.route("/questions/<int:question_id>/upvote", methods=["PATCH"])
def upvote_question(question_id):
    """ 
    This method upvotes a specific question 
    """
    details = request.get_json()

    return jsonify(QuestionModels(details).upvote_question(question_id)), 200


@version2.route("/questions/<int:question_id>/downvote", methods=["PATCH"])
def downvote_question(question_id):
    """ Downvotes a question to a specific meetup """

    resp = QuestionModels(request.get_json()).downvote_question(question_id)

    return jsonify(resp), resp["status"]
