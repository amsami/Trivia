import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json

from models import db, setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
#Pagination function as it will be used a lot at different end points
def paginate_questions(request, all_questions):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in all_questions]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @AK TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resource={r"/api/*": {"origins": "*"}})
  '''
  @AK TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,PUT,DELETE,OPTIONS')
        return response
  '''
  @AK TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  #Categories endpoint, where we load all categories and I have to change the format to meet the Json format
  @app.route('/categories')
  def all_categories():
   category_all = Category.query.all()
   category_all = Category.query.order_by(Category.type).all()

   categories = [category.format() for category in category_all]

   if len(categories) == 0:
      abort(404)

  #Change the format to dictionary to pass Json format
   formatted_categories = {k:v for category in categories for k,v in category.items()}
   return jsonify({
          'success': True,
          'categories': formatted_categories         
   })
  '''
  @AK TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  #Questions end point, passing all questions and all categories
  @app.route('/questions')
  def get_questions():
    questions = Question.query.all()
    formatted_questions = paginate_questions(request, questions)
    category_all = Category.query.all()
    categories = [category.format() for category in category_all]

    if len(formatted_questions) == 0:
      abort(404)

    formatted_categories = {k:v for category in categories for k,v in category.items()}
    return jsonify({
          'success': True,
          'questions': formatted_questions,
          'total_questions': len(questions),
          'category': "",
          'categories': formatted_categories
    })
  '''
  @AK TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  #Delete end point
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.filter(Question.id == question_id).one_or_none()
    if question is None:
      abort(404)
    #based on the question id, delete the question, and update the db
    try:
      Question.query.filter(Question.id == question_id).delete()
      questions = Question.query.all()
      #return new questions after deleting the question
      formatted_questions = paginate_questions(request, questions)
      if len(formatted_questions) == 0:
        abort(404)
      
      category_all = Category.query.all()
      categories = [category.format() for category in category_all]

      if len(categories) == 0:
        abort(404)
       
      formatted_categories = {k:v for category in categories for k,v in category.items()}
      
      db.session.commit()

      return jsonify({
        'success': True,
        'questions': formatted_questions,
        'total_questions': len(questions),
        'categories': formatted_categories
      })

    except:
      abort(422)  
      db.session.rollback()

 
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''          
  @app.route('/questions', methods=['POST'])
  def add_question():
    try:
      #get the new question data from json
      question = Question(
                          question = request.get_json()['question'],
                          answer = request.get_json()['answer'],
                          category = request.get_json()['category'],
                          difficulty = request.get_json()['difficulty']
                          )
      question.insert()
      #add question and commit to db
      db.session.commit()

      return jsonify({
        'success': True,
      })
    except:
      abort(422)
      db.session.rollback()


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    #get Search term from Json, and then search based on the search term
    #Return data to the format to json
    searchTerm = request.get_json()['searchTerm']
    data_searched=Question.query.filter(Question.question.ilike('%{}%'.format(searchTerm))).all()
    formatted_questions = paginate_questions(request, data_searched)   
    category_all = Category.query.all()
    categories = [category.format() for category in category_all]
    formatted_categories = {k:v for category in categories for k,v in category.items()} 
    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions_found': len(data_searched),
      'current_category': "",
      'categories': formatted_categories
    })   

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  #Get the set of questions based on a category
  @app.route('/categories/<int:category_id>/questions')
  def get_specific_question(category_id):
    questions_per_category = Question.query.filter(Question.category == category_id).all()
    if len(questions_per_category) == 0:
      abort(404)

    formatted_questions = paginate_questions(request, questions_per_category)

    category_all = Category.query.all()
    categories = [category.format() for category in category_all]
    formatted_categories = {k:v for category in categories for k,v in category.items()} 

    print(category_id, questions_per_category, formatted_questions, len(questions_per_category))

    try:

      return jsonify({
          'success': True,
          'questions': formatted_questions,
          'total_questions': len(questions_per_category),
          'category': category_id,
          'categories': formatted_categories
      })
    except:
      abort(404)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''  
  #Quiz end point, get data from Json about category, and previous questions
  # If category all is selected, category is set to 0, and check if it's the first question, then pass all questions
  # If there was a previous question, then pass all questions not part of the previous questions set
  # Otherwise, if thre is a category id, get questions from that category, and check for previous questions like the case 
  # of all categories 
  @app.route('/quizzes', methods=['POST'])
  def quiz():
    response_quiz = request.get_json()
    previous_questions = response_quiz['previous_questions']
    category_id = response_quiz["quiz_category"]["id"]
    if category_id == 0:
      if previous_questions is None:
        questions = Question.query.all()        
      else:
        questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
        
    else:
      if previous_questions is None:
        questions = Question.query.filter(Question.category == category_id).all()
      else:
        questions = Question.query.filter(Question.id.notin_(previous_questions),
        Question.category == category_id).all()
    #I got an error, because random.choice function would error out if there was an empty array
    #Needed to add a check here to avoid getting an error with the random.choice function.
    if len(questions) == 0:
        return jsonify({'question': None})

    next_question = random.choice(questions).format()
    print(next_question)
    if next_question is None:
      next_question = False

    return jsonify({
      'success': True,
      'question': next_question
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  #Setting up error handlers for all the different error messages
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "Bad request"
      }), 400

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "Not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "Unprocessable"
      }), 422

  @app.errorhandler(405)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 405,
          "message": "Method not allowed"
      }), 405

  return app

    