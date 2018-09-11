
from datetime import date, datetime
from os import environ
import json
import string
import random
import unittest

# local import
import myapi

# get the current date
today = date.today()

# generate a random name for a user
user = ''.join([random.choice(string.ascii_letters) for n in xrange(10)])

# generate a random user's birtday
year = random.randint(1970, 2000)
month = random.randint(1, 12)
day = random.randint(1, 28)
user_bd1 = date(year, month, day)

# calculate an amount of days till the user's birthday
user_bd_tmp = user_bd1.replace(year=today.year)
if user_bd_tmp < today:
    user_bd_tmp = user_bd_tmp.replace(year=today.year + 1)
time_to_user_bd = abs(user_bd_tmp - today)

# set a second instance of the user's birtday
user_bd2 = date(2010, today.month, today.day)

# make a sample message expected than the user's birthday isn't today
sample_message1 = "Hello, %s! Your birthday is in %s days" % (user, str(time_to_user_bd.days))

# make a sample message expected than the user has a birthday today
sample_message2 = "Hello, %s! Happy birthday!" % user

# get an api address from the envronment variable or use the default value
if 'API_HOST' in environ:
    api_host = environ['API_HOST']
else:
    api_host = 'localhost'

# set full url for api requests
API_URL = 'http://' + api_host + '/hello/' + user

class TestMyApi(unittest.TestCase):

    def setUp(self):
        self.app = myapi.app.test_client()
        self.app.testing = True

    def test_put(self):

    # user doesn't exist in the database
        response = self.app.get(API_URL)
        self.assertEqual(response.status_code, 404)

    # missing the key dateOfBirth
        data = {"some_key": "some_value"}
        response = self.app.put(API_URL,
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    # the key dateOfBirth with the wrong value
        data = {"dateOfBirth": "some_value"}
        response = self.app.put(API_URL,
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    # a put request with right data
        data = {"dateOfBirth": "2000-01-01"}
        response = self.app.put(API_URL,
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)

    # a put request with the same name, but with other data
        data = {"dateOfBirth": "%s" % user_bd1.strftime('%Y-%m-%d') } 
        response = self.app.put(API_URL,
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 204)

    # the user exists in the database and his birthday isn't today
        response = self.app.get(API_URL)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data())
        self.assertEqual(data['message'], sample_message1)

    # set the second instance of the user's birthday
        data = {"dateOfBirth": "%s" % user_bd2.strftime('%Y-%m-%d') } 
        response = self.app.put(API_URL,
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 204)

    # the user exists in the database and has a birthday today
        response = self.app.get(API_URL)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data())
        self.assertEqual(data['message'], sample_message2)

# run tests
if __name__ == "__main__":
    unittest.main()
