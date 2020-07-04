import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

#paginate questions: reusable function
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions
    
def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  

  #set up CORS
  CORS(app, resources={'/': {'origins': '*'}})

  #set up after_request decorator to set Access-Control-Allow
  @app.after_request
  def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
        return response
  

  #This route handles GET request for all available categories
  @app.route('/categories', methods=['GET'])
  def get_categories():

        categories = Category.query.order_by(Category.type).all()
        if (len(categories) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'categories': {
                category.id:category.type for category in categories
            }
        })


 # This route handles GET requests for questions including pagination
  @app.route('/questions', methods=['GET'])
  def get_questions():
        question_list = Question.query.all()
        total_questions = len(question_list)
        current_questions = paginate_questions(request, question_list)

        categories = {}
        for category in Category.query.all():
            categories[category.id] = category.type
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': categories
        })

  # This route handles delete question using Question ID
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_questions(id):
    
    question_data = Question.query.filter_by(id=id).one_or_none()
    if question_data is None:
        abort(404)
    question_data.delete()
    return jsonify({
                'success': True,
                'deleted': id
                    })

  #This route handles a new POST question request
  @app.route('/questions', methods=['POST'])
  def add_questions():
       body = request.get_json()
       searchTerm = body.get('searchTerm')
       try:
        if searchTerm: 
            selection = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).all()
        else: 
            new_question = body.get('question','')
            new_answer = body.get('answer','')
            new_difficulty = body.get('difficulty','')
            new_category = body.get('category','')
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            return jsonify({
                    'success': True,
                    'created': question.id,
                    'question_created': question.question,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })
       except Exception as error:
        abort(422)

  #This route handles the search request for Questions 
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', '')

        if search_term:
            result = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in result],
                'total_questions': len(result),
                'current_category': None
            })
        abort(404)

  #This route handles questions based on a category
  @app.route('/categories/<int:id>/questions', methods=['GET'])
  def get_questions_by_category(id):

        category = Category.query.filter_by(id=id).one_or_none()
        if (category is None):
            abort(400)

        matching_questions = Question.query.filter_by(category=category.id).all()
        paginated = paginate_questions(request, matching_questions)
        return jsonify({
            'success': True,
            'questions': paginated,
            'total_questions': len(Question.query.all()),
            'current_category': category.type
        })

  #This route handles the quiz play
  @app.route('/quizzes', methods=['POST'])
  def playQuiz():
    if request.data:
            search_key = request.get_json()
            if (('quiz_category' in search_key and 'id' in search_key['quiz_category']) and 'previous_questions' in search_key):
                questions_query = Question.query.filter_by(category=search_key['quiz_category']['id']).filter(
                      Question.id.notin_(search_key["previous_questions"])).all()
                length_of_available_question = len(questions_query)
                if length_of_available_question > 0:
                    result = {
                      
                          "success": True,
                          "question": Question.format(
                              questions_query[random.randrange(
                                  0,
                                  length_of_available_question
                              )]
                          )
                          
                    }
                else:
                    result = {
                          "success": True,
                          "question": None,
                          
                    }
                return jsonify(result)
            abort(404)
            abort(422)


  #Error Handlers
  @app.errorhandler(404)
  def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

  @app.errorhandler(422)
  def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

  @app.errorhandler(400)
  def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

  
  return app

    