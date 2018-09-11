
from os import environ
from datetime import date, datetime
from flask import Flask
from flask_restful import reqparse, Resource, Api
from sqlalchemy import create_engine

# set configuration parameters from envronment variables or use the default values
if 'DATABASE_HOST' in environ:
    db_host = environ['DATABASE_HOST']
else:
    db_host = 'localhost'
if 'DATABASE_NAME' in environ:
    db_name = environ['DATABASE_NAME']
else:
    db_name = 'myapi'
if 'DATABASE_USER' in environ:
    db_user = environ['DATABASE_USER']
else:
    db_user = 'myapi'
if 'DATABASE_PASS' in environ:
    db_pass = environ['DATABASE_PASS']
else:
    db_pass = 'myapi'

# a database engine settings
db_engine = create_engine('postgres://' + db_user + ':' + db_pass + '@' + db_host + '/' + db_name)

# create and setup a parser for parsing incoming data in json format
parser = reqparse.RequestParser()
parser.add_argument('dateOfBirth', location='json')

# a class for serving API requests
class serve_api(Resource):
    # actions for the method GET
    def get(self, user_name):
        # select the user's data from the database
        db_conn = db_engine.connect()
        db_query = db_conn.execute("SELECT user_bd FROM users where user_name = '%s'" % user_name)
        data = db_query.fetchone()
        # check if a user exists in the database
        if data is not None:
            # get the current date
            today = date.today()
            # compose the user's birthday with the current year
            user_bd = data.user_bd.replace(year=today.year)
            # if the user already celebrated his birthday this year
            if user_bd < today:
                # compose the user's birthday with the next year
                user_bd = user_bd.replace(year=today.year + 1)
            # calculate an amount of days till the user's birthday
            time_to_user_bd = abs(user_bd - today)
            if time_to_user_bd.days == 0:
                # congratulation if the user's birthday is today
                result = { 'message': 'Hello, %s! Happy birthday!' % user_name }
                code = 200
            else:
                # greeting with an amount of days till the user's birthday
                result = { 'message': 'Hello, %s! Your birthday is in %s days' % (user_name, str(time_to_user_bd.days)) }
                code = 200
        else:
            # the user doesn't exist in the database
            result = { 'message': 'User %s not found' % user_name }
            code = 404
        return result, code
    # actions for the method PUT
    def put(self, user_name):
        # parse received data
        parsed_args = parser.parse_args()
        # extract the user's birthday date
        user_bd = parsed_args['dateOfBirth']
        if user_bd is not None:
            # proceed if we have a birthday date
            try:
                # validate a format of the birthday date
                datetime.strptime(user_bd, "%Y-%m-%d")
                # select the user's data from the database
                db_conn = db_engine.connect()
                db_query = db_conn.execute("SELECT user_id FROM users where user_name = '%s'" % user_name)
                data = db_query.fetchone()
                # check if a user exists in the database
                if data is not None:
                    # update the user's data if the user exists in the database
                    db_query = db_conn.execute("UPDATE users SET user_bd = '%s' WHERE user_name = '%s'" % (user_bd, user_name))
                    result = {}
                    code = 204
                else:
                    # store the user's data if the user doesn't exist in the database
                    db_query = db_conn.execute("INSERT INTO users (user_bd, user_name) VALUES ('%s','%s')" % (user_bd, user_name))
                    result = {}
                    code = 201
            except ValueError:
                # a birthday date validation error
                result = { 'message': 'An incorrect format of a birthday date, should be YYYY-MM-DD' }
                code = 400
        else:
            # the request doesn't contain a birthday date
            result = { 'message': 'An update request should contain a birthday date in a format YYYY-MM-DD' }
            code = 400
        return result, code

# create a Flask application with API
app = Flask(__name__)
api = Api(app)

# create an API endpoint
api.add_resource(serve_api, '/hello/<user_name>')

# run the Flask application
if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')

