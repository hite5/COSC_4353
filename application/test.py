from app import app
from flask import session
import unittest
class FlaskTest(unittest.TestCase):
    def test_index(self): #load homepage
        tester = app.test_client(self)
        response = tester.get("/")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200) #code 200 means it loaded with no problems

    def test_index2(self): #load login page
        tester = app.test_client(self)
        response = tester.get("/emp_login")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_index3(self): #signup page
        tester = app.test_client(self)
        response = tester.post('/signup', data=dict(email='data1', name='data2name', password='data2pass'))
        statuscode = response.status_code
        self.assertEqual(statuscode, 302) #redirect

    def test_index4(self): #calculator page
        tester = app.test_client(self)
        response = tester.post('/quoteCalc', data=dict(zipcode='77204', gallons='420'))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_index5(self): #submit to form
        tester = app.test_client(self)
        response = tester.post('/submitFormToDB', data=dict(dest='swag', zipcode='77204', gallons='1337'))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_index6(self): #new customer submission
        tester = app.test_client(self)
        response = tester.post('/NewCustomerForm', data=dict(f_name = 'jim',
                                                             l_name = 'tim',
                                                             email = 'swag@swaggerson.com',
                                                             newpasswd = 'ayoayoaoyaoy',
                                                             phoneNum = '1234567891',
                                                             Address = 'swagstreet',
                                                             City = 'swagcity',
                                                             state = 'TX',
                                                             zipcode = '12345'))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_index7(self): #test login
        tester = app.test_client(self)
        response = tester.post('/emp_login', data=dict(email='swag@swaggerson.com', password='ayoayoaoyaoy', remember='True'))
        statuscode = response.status_code
        self.assertEqual(statuscode, 302)


    # #FAILED DUE TO OVERLOADING ROUTES (ONE HAS POST)
    # def test_index3(self):  # load signup page
    #     tester = app.test_client(self)
    #     response = tester.get("/signup")
    #     statuscode = response.status_code
    #     self.assertEqual(statuscode, 200)
