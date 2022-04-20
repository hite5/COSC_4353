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
        response = tester.get("/login")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    # def test_index3(self): #signup page
    #     tester = app.test_client(self)
    #     response = tester.post('/signup', data=dict(email='data1', name='data2name', password='data2pass'))
    #     statuscode = response.status_code
    #     self.assertEqual(statuscode, 302) #redirect

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
                                                             newpasswd = 'password',
                                                             phoneNum = '1234567891',
                                                             Address = 'swagstreet',
                                                             City = 'swagcity',
                                                             state = 'TX',
                                                             zipcode = '12345'))
        statuscode = response.status_code
        self.assertEqual(statuscode, 302)

    def test_index7(self): #test login
        tester = app.test_client(self)
        response = tester.post('/login', data=dict(username='mj@mail.com', password='password'))
        statuscode = response.status_code
        tester.get('/logout')
        self.assertEqual(statuscode, 302)

    def test_index8(self):  # test report
        with app.test_client(self) as tester:
            tester.get('/auto_login')
            response = tester.post('/report', data=dict(start='2021-01-01', end='2022-03-31'))
            statuscode = response.status_code
            self.assertEqual(statuscode, 200)

    def test_index9(self):  # test editprofile
        with app.test_client(self) as tester:
            # tester = app.test_client(self)
            tester.get('/auto_login')
            response = tester.post('/EditProfile', data=dict(
                fname='mike',
                lname='jones',
                phoneNum='7879247896',
                Address='101 Main St',
                City='Houston',
                state='TX',
                zipcode='77009',
                email='mj@mail.com'))

            statuscode = response.status_code
            self.assertEqual(statuscode, 302)

    def test_index10(self):  # test change password
        with app.test_client(self) as tester:
            # tester = app.test_client(self)
            tester.get('/auto_login')
            response = tester.post('/changePassword', data=dict(
                oldpasswd='password',
                newpasswd='password1',
                confirmpasswd='password1'))
            statuscode = response.status_code
            self.assertEqual(statuscode, 302)

    def test_index101(self):  # test change password
        with app.test_client(self) as tester:
            # tester = app.test_client(self)
            tester.get('/auto_login')
            response = tester.post('/changePassword', data=dict(
                oldpasswd='password1',
                newpasswd='password',
                confirmpasswd='password'))
            statuscode = response.status_code
            self.assertEqual(statuscode, 302)

    def test_index11(self): #load report page
        tester = app.test_client(self)
        response = tester.get("/report")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_index12(self): #load new order
        tester = app.test_client(self)
        response = tester.get("/NewOrder")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
