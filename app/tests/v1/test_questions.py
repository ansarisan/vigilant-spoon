import unittest
import json
from ... import create_app


class TestQuestions(unittest.TestCase):
    """
    Contains testcases for questions 
    for a meetup record
    """

    def setUp(self):
        """ Sets up what the test will need before it runs """

        self.app = create_app()

        self.client = self.app.test_client()

        self.data = {
            "firstname": "Mohammed",
            "lastname": "Mohali",
            "othername": "Mrali",
            "email": "ali@moh.com",
            "phoneNumber": "0707070707",
            "username": "Mohali",
            "password": "P@5sword"
        }

        self.meetup = {
            "location": "House of Leather, Nairobi",
            "images": ["img1.jgp", "img2.jpg"],
            "topic": "All the Leather you can get",
            "happeningOn": "Mar 8 2019 11:30AM",
            "tags": ["Creative", "Leather"],
            "username": "Leewel"
        }

        self.user = self.client.post(
            "/api/v1/auth/signup", data=json.dumps(self.data), content_type="application/json")
        self.assertEqual(self.user.status_code, 201)

        self.meetup = self.client.post(
            "/api/v1/meetups", data=json.dumps(self.meetup), content_type="application/json")
        self.assertEqual(self.meetup.status_code, 201)

        self.question = {
            "user": self.user.json["data"][0]["id"],
            "meetup": self.meetup.json["data"][0]["id"],
            "title": "Leather bag price",
            "body": "How much would a good leather bag cost ?"

        }

        

    def post_question(self, path="/api/v1/questions", data={}):
        """ Creates a question for a specific meetup """

        if not data:
            data = self.question

        response = self.client.post(path, data=json.dumps(
            data), content_type="application/json")

        return response

    def upvote_question(self, path="/api/v1/questions/<int:question_id>/upvote", data={}):
        """ Increases votes of a specific question by 1 """
        
        response = self.client.patch(path)

        return response

    def downvote_question(self, path="/api/v1/questions/<int:question_id>/downvote", data={}):
        """ Downvotes a question to a specific meetup """

        response = self.client.patch(path)

        return response

    def test_post_new_question(self):
        """ Tests whether new question is created with data provided """

        new_question = self.post_question()

        self.assertEqual(new_question.status_code, 201)
        self.assertTrue(new_question.json["data"])

    def test_upvote_question(self):
        """ Tests for upvoting a question """

        new_vote = self.post_question()
        self.assertEqual(new_vote.status_code, 201)

        self.assertEqual(self.upvote_question(path="/api/v1/questions/{}/upvote".format(new_vote.json["data"][0]["user"])).status_code, 200)
        self.assertTrue(self.upvote_question(path="/api/v1/questions/{}/upvote".format(new_vote.json["data"][0]["user"])).json["data"][0]["votes"])
        self.assertEqual(self.upvote_question(path="/api/v1/questions/{}/upvote".format(new_vote.json["data"][0]["user"])).json["data"][0]["votes"], 3)


    def test_downvote_question(self):
        """ Tests for downvoting a question """

        downvote = self.post_question()
        self.assertEqual(downvote.status_code, 201)

        self.assertEqual(self.downvote_question(path="/api/v1/questions/{}/downvote".format(downvote.json["data"][0]["user"])).status_code, 200)
        
        


if __name__ == "__main__":
    unittest.main()
