import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = "postgresql://postgres:Hari987@localhost:5432/trivia_test_db"
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            self.new_question = {
            'question': 'What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?',
            'answer': 'Tom Cruise',
            'difficulty': 4,
            'category': '5'
        }
    def tearDown(self):
        """Executed after reach test"""
        pass
    #success test case for get_questions_by_category
    def test_get_questions_by_category(self):
        res=self.client().get('/categories/5/questions')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'],'Entertainment')

    #failure test case for get_questions_by_category(400)
    def test_400_questions_by_category(self):
        res=self.client().get('/categories/100/questions')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'bad request')

    #success test for adding a question
    def test_addQuestions(self):
        previous_questions = Question.query.all()
        res=self.client().post('/questions', json=self.new_question)
        data=json.loads(res.data)
        new_question = Question.query.all()
        self.assertTrue(len(new_question) - len(previous_questions) == 1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
       
    #failure test case for not adding a question(422)
    def test_addQuestions_failure(self):
        previous_questions = Question.query.all()
        res=self.client().post('/questions', json={})
        data=json.loads(res.data)
        new_question = Question.query.all()
        self.assertTrue(len(new_question) == len(previous_questions))
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    #success test case for deleting a question
    def test_deleteQuestions(self):
        question = Question(question=self.new_question['question'], answer=self.new_question['answer'],
                            category=self.new_question['category'], difficulty=self.new_question['difficulty'])
        question.insert()
        question_id=question.id
        previous_questions = Question.query.all()
        res=self.client().delete('/questions/{}'.format(question_id))
        data=json.loads(res.data)
        new_question = Question.query.all()
        testQuestion= Question.query.filter(Question.id == 1).one_or_none()
        self.assertTrue(len(previous_questions) - len(new_question) == 1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)
        self.assertEqual(testQuestion, None)
       
    #Success Test Case for search_questions
    def test_search_questions(self):
        self.search_term={'searchTerm':'Who'}
        res=self.client().post('/questions/search', json= self.search_term)
        data=json.loads(res.data)
        print("Printing Data: " + data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['searchTerm'])

    #Failure Test Case for search_questions(404)
    def test_search_questions_failure(self):
        self.search_term={'searchTerm':'dfgfhfghghgjhgj'}
        res=self.client().post('/questions/search', json= self.search_term)
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        

    #Success Test Case for play quiz
    def test_play_quiz(self):
        res=self.client().post('/quizzes', json= {})
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)