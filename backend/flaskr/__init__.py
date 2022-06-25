import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS')
        return response

    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """

    def paginate_helper(request, requested_data):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        formatted_data = [data.format() for data in requested_data]
        current_data = formatted_data[start:end]
        return current_data

    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        categories = [category.format() for category in categories]
        categories = [data['type'] for data in categories]
        return jsonify({'success': True,
                        'categories': categories})

    """
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions')
    def get_questions():
        questions = Question.query.all()
        questions_paginated = paginate_helper(request, questions)
        if len(questions_paginated) == 0:
            abort(404)
        categories = [category.format() for category in Category.query.all()]
        categories_list = [data['type'] for data in categories]
        current_category = categories_list
        return jsonify({'questions': questions_paginated,
                        'total_questions': len(questions),
                        'current_category': current_category,
                        'categories': categories_list})

    """
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter_by(id=question_id).one_or_none()
        if question is None:
            abort(404)
        try:
            question.delete()
            return jsonify({'success': True, 'question_id': question.id}, 200)
        except BaseException:
            abort(422)

    """
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=['POST'])
    def post_or_search_question():
        body = request.get_json()
        if not body:
            abort(400)
        search_term = request.get_json().get('searchTerm', None)
        if search_term:
            questions = Question.query.filter(
                Question.question.ilike(
                    '%' + search_term + '%')).all()
            if questions:
                formatted_questions = [question.format()
                                       for question in questions]
                return jsonify({'question': formatted_questions,
                                'total_question': len(formatted_questions),
                                'current_category': questions[0].category,
                                'success': True})
            else:
                abort(404)

        question = body.get('question')
        answer = body.get('answer')
        difficulty = body.get('difficulty')
        category = body.get('category')
        if not question or not answer or not difficulty or not category:
            abort(400)
        try:
            new_question = Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty)
            new_question.insert()
            return jsonify(
                {'success': True, 'question_id': new_question.id}, 201)
        except BaseException:
            abort(422)

    """
    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:category_id>/questions',methods=["GET"])
    def get_category_questions(category_id):
        
        category_questions =[question.format() for question in Question.query.filter(Question.category==category_id).all()]

        if not category_questions:
            abort(404)

        return jsonify({
            "questions": category_questions,
            "total_questions":len(category_questions),
            "current_category": Category.query.filter(Category.id==category_id).first().type
        }),200

    """
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    
    def play_quiz():
        previous_questions = request.get_json().get('previous_questions')
        quiz_category =request.get_json().get('quiz_category')



        if  previous_questions is None or quiz_category is None:
            abort(400)
        if quiz_category["id"] == 0:            
            category_questions =[question.format() for question in Question.query.all()]
        else:
          category_questions =[question.format() for question in Question.query.filter(Question.category==quiz_category['id']).all()]

        

        while True:
            random_question = random.choice(category_questions)
            if random_question['id'] not in previous_questions:
                break
            else:
                 return jsonify({
            "question":None
        })
        
        return jsonify({
            "question":random_question
        }),200
     
    """
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Requested resource can not be found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed for requested url"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": 'Request can not be processed'
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app


app = create_app()
