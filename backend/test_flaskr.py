import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import *


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(db_user,db_pass,db_server, self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
                'question': 'Who is the best artist in the world today?',
                'answer': 'Rihanna',
                'category': 5,
                'difficulty': 3,
            }

        self.bad_question = {
                'question': 'Who is the best artist in the world today?',
                'answer': 'Rihanna',
                'category': [5],
                'difficulty': 3,
            }
        
        self.quiz = {'previous_questions': [],'quiz_category': {'category': "Art", 'id': 2}}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        response = self.client().get('/categories')
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(result['categories']))
    
    def test_405_get_categories(self):
        response = self.client().post('/categories')
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(result['success'], False)
        self.assertEqual(result['error'], 405)
        self.assertEqual(result['message'], 'Method not allowed')

    def test_get_questions(self):
        response = self.client().get('/questions')
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['currentCategory'])
        self.assertTrue(result['questions'])
    
    def test_404_get_questions(self):
        response = self.client().get('/questions?page=7')
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result['success'], False)
        self.assertEqual(result['error'], 404)
        self.assertEqual(result['message'], 'Resource Not Found')
    
    def test_get_questions_by_category(self):
        response = self.client().get('categories/1/questions')
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['totalQuestions'], 3)
        self.assertTrue(result['questions'])
    
    def test_404_get_questions_by_category(self):
        response = self.client().get('categories/10/questions')
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result['success'], False)
        self.assertEqual(result['error'], 404)
        self.assertEqual(result['message'], 'Resource Not Found')

    def test_insert_question(self):
        response = self.client().post('/questions', json=self.new_question)

        result = json.loads(response.data)

        self.assertTrue(response.status_code, 200)
        self.assertTrue(result['success'], True)
        self.assertTrue(result['created'], 24)
        self.assertTrue(result['questions'])
        self.assertTrue(result['total_questions'], 20)
    
    def test_422_insert_question(self):
        response = self.client().post('/questions', json=self.bad_question)
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(result['success'], False)
        self.assertEqual(result['error'], 422)
        self.assertEqual(result['message'], 'Not Processable')

    def test_delete_question(self):
        response = self.client().delete('/questions/23')
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['success'], True)
        self.assertEqual(result['question_id'], 23)

    def test_422_delete_question(self):
        response = self.client().delete('/questions/40')
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(result['success'], False)
        self.assertEqual(result['error'], 422)
        self.assertEqual(result['message'], 'Not Processable')

    def test_get_quiz(self):
        response = self.client().post('/quizzes', json=self.quiz)
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['question'])
    
    def test_404_get_quiz(self):
        response = self.client().post('/quizzes',json={"previous_questions": [4,2,6], "quiz_category": {'category': "Entertainment", 'id': 5}})
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result['success'], False)
        self.assertEqual(result['error'], 404)
        self.assertEqual(result['message'], 'Resource Not Found')
    
    def test_search_question(self):
        response = self.client().post('/questions', json={'searchTerm': 'title'})
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['questions'])
        self.assertEqual(result['totalQuestions'], 2)

    def test_404_search_question(self):
        response = self.client().post('/questions', json={'searchTerm': [2]})
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result['success'], False)
        self.assertEqual(result['error'], 404)
        self.assertEqual(result['message'], 'Resource Not Found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()