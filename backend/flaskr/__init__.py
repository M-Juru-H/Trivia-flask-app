import os
from threading import currentThread
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/v1.0/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def categories():

        categories = Category.query.all()

        return jsonify(
            {
                "categories": dict((category.id, category.type) for category in categories) ,
            }
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions', methods=['GET'])
    def questions():

        categories = Category.query.all()
        questions = Question.query.order_by(Question.id).all()

        paginated_questions = paginate_questions(request, questions)
        if not paginated_questions:
            abort(404)

        rand_categories = random.randint(1, int(len(categories)))
        current_category = [category.type for category in categories if category.id == rand_categories][0]

        return jsonify(
            {
                "questions": paginated_questions,
                "totalQuestions": len(questions),
                "categories": dict((category.id, category.type) for category in categories),
                "currentCategory": current_category
                }
        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_questions(question_id):


        try:
            question = Question.query.get(question_id)

            if question is None:
                abort(404)

            question.delete()

            return jsonify(
                {
                    "success": True,
                    "question_id": question_id,
                }
            )
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=['POST'])
    def add_questions():
        body = request.get_json()

        if body.get('searchTerm'):
               
            searchTerm = body.get("searchTerm", None)
            search = Question.query.filter(Question.question.ilike(f"%{searchTerm}%")).all()

            if not search:
                abort(404)

            categories = Category.query.all()
            questions = Question.query.order_by(Question.id).all()
            rand_categories = random.randint(1, int(len(categories)))
            current_category = [category.type for category in categories if category.id == rand_categories][0]

            return jsonify(
                {
                    "questions": [question.format() for question in search],
                    "totalQuestions": len(search),
                    "currentCategory": current_category
                    }
            )

        else:

            question = body.get("question", None)
            answer = body.get("answer", None)
            category = body.get("category", None)
            difficulty = body.get("difficulty", None)

            try:
                new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
                new_question.insert()

                questions = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, questions)

                return jsonify(
                    {
                        "success": True,
                        "created": new_question.id,
                        "questions": current_questions,
                        "total_questions": len(Question.query.all()),
                    }
                )

            except:
                abort(422)


    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def specified_category(id):        
        
        questions = Question.query.filter(Question.category == id).order_by(Question.id).all()
        
        if not questions:
            abort(404)

        categories = Category.query.all()
        rand_categories = random.randint(1, int(len(categories)))
        current_category = [category.type for category in categories if category.id == rand_categories][0]

        return jsonify(
            {
                "questions": paginate_questions(request, questions),
                "totalQuestions": len(questions),
                "currentCategory": current_category
                }
        )

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():

        body = request.get_json()
        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)

        
        if quiz_category['type'] == 'click':
            questions = Question.query.filter(
            Question.id.notin_(previous_questions)).all()
        else:
            questions = Question.query.filter(
            Question.id.notin_(previous_questions),
            Question.category == quiz_category['id']).all()
            
        if not questions:
            abort(404)
        
        question = random.choice(questions)

        return jsonify({
            'question': question.format()
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Not Processable"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Server error"
        }), 500

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed"
        }), 405

    return app

