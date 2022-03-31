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
        #response = tester.post('/emp_login', data=dict(email='swag@swaggerson.com', password='ayoayoaoyaoy', remember='True'))
        response = tester.post('/quoteCalc', data=dict(zipcode='00000', gallons='420', state='TX'))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_index5(self): #submit to form
        tester = app.test_client(self)
        response = tester.post('/submitFormToDB', data=dict(dest='swag', zipcode='00000', gallons='1337', state='TX'))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_index6(self): #new customer submission
        tester = app.test_client(self)
        response = tester.post('/NewCustomerForm', data=dict(f_name = 'tim',
                                                             l_name = 'jim',
                                                             email = 'swag3@swaggerson.com',
                                                             newpasswd = 'ayoayoaoyaoy2',
                                                             phoneNum = '1234567891',
                                                             Address = 'swagstreet',
                                                             City = 'swagcity',
                                                             state = 'TX',
                                                             zipcode = '12345'))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_index7(self): #test login
        tester = app.test_client(self)
        response = tester.post('/emp_login', data=dict(email='swag3@swaggerson.com', password='ayoayoaoyaoy', remember='True'))
        statuscode = response.status_code
        self.assertEqual(statuscode, 302)

    def test_index8(self):  # test report
        tester = app.test_client(self)
        response = tester.post('/report', data=dict(customer='Chevron', start='2021-01-01', end='2022-03-31'))
        statuscode = response.status_code
        self.assertEqual(statuscode, 302)


    # #FAILED DUE TO OVERLOADING ROUTES (ONE HAS POST)
    # def test_index3(self):  # load signup page
    #     tester = app.test_client(self)
    #     response = tester.get("/signup")
    #     statuscode = response.status_code
    #     self.assertEqual(statuscode, 200)
