from flask import Flask, request, render_template, redirect, url_for, request, Blueprint, flash, current_app, jsonify, \
    session
from mysql.connector import connect, Error
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
import re
from application import db_info
import datetime
import pgeocode

views = Blueprint('views', __name__)

host = db_info.host
user = db_info.user
password = db_info.password
database = db_info.database


# Home Page | Work on redirecting to different pages
@views.route('/')
def home():
    try:
        if session['loggedin']:
            return render_template('HomePage.html', name=session['username'])
    except:
        return render_template("HomePage.html")


@views.route('/NewCustomerForm', methods=["GET", "POST"])
def NewCustomerForm():
    if request.method == "POST":
        first_name = request.form.get("f_name")
        last_name = request.form.get("l_name")
        email = request.form.get("email")
        passW = request.form.get("newpasswd")
        phone = request.form.get("phoneNum")
        address = request.form.get("Address")
        city = request.form.get("City")
        state = request.form.get("state")
        zipcode = request.form.get("zipcode")
        passHash = generate_password_hash(passW, method='sha256')

        # if user already exists, redirect back to signup form
        try:
            with connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database
            ) as connection:
                print(connection)
                cursor = connection.cursor(buffered=True)
                cursor.execute(f"SELECT * FROM users WHERE email = '{email}';")
                userExists = cursor.fetchone()
                print(userExists)
                if userExists:
                    flash('Email address already exists')
                    return redirect(url_for('views.NewCustomerForm'))
                elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    flash('Invalid email address !')
                    return redirect(url_for('views.NewCustomerForm'))
                elif not email or not passW:
                    flash('Please fill out the form completely!')
                    return redirect(url_for('views.NewCustomerForm'))
                else:
                    insert_customer = "INSERT INTO users (first_name, last_name, email, password, phone, address, city, state, zip) " \
                                      "VALUES " \
                                      "('" + first_name + "','" + last_name + "','" + email + "','" + passHash + "','" + phone + "'," \
                                                                                                                                 "'" + address + "','" + city + "','" + state + "','" + zipcode + "');"

                    with connection.cursor(buffered=True) as cursor:
                        print("Successfully inputted data into DB")

                        cursor.execute(insert_customer)
                        connection.commit()
                        flash('You have successfully registered !')
                        return redirect(url_for('views.home'))

        except Error as e:
            print(e)
    return render_template("NewCustomerForm.html")


@views.route('/EditProfile', methods=["GET", "POST"])
def EditProfile():
    try:
        if session['loggedin']:
            with connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database
            ) as connection:
                cursor = connection.cursor(buffered=True)
                query = f"SELECT first_name, last_name, email, phone, user_id, address, city, zip, state FROM users WHERE email = '{session['username']}'"
                cursor.execute(query)
                result = cursor.fetchone()
                if result is None:
                    flash('Error finding profile details in database. Please contact database administrator.')
                    return redirect(url_for('views.home'))
                data = {
                    "firstname": result[0],
                    "lastname": result[1],
                    "email": result[2],
                    "phone": result[3],
                    "id": result[4],
                    "address": result[5],
                    "city": result[6],
                    "zip": result[7],
                    "state": result[8]
                }

                if request.method == "POST":
                    # Retrieve form data
                    firstname = request.form.get('fname')
                    lastname = request.form.get('lname')
                    phone = request.form.get('phoneNum')
                    address = request.form.get('Address')
                    city = request.form.get('City')
                    state = request.form.get('state')
                    zipcode = request.form.get('zipcode')
                    email = request.form.get('email')

                    emailquery = f"SELECT first_name FROM users WHERE email='{email}'"  # checking for email in mysql DELETE!!!!!!!
                    cursor.execute(emailquery)
                    emailcheck = cursor.fetchone()

                    if (emailcheck and (
                            session[
                                'username'] != email)):  # if a user is found, we want to redirect back to edit page so user can try again
                        flash('Email address belongs to another user. Please enter an email that belongs to you.')
                        return redirect(url_for('views.EditProfile'))

                    edit_profile = f"UPDATE users SET first_name = '{firstname}', last_name = '{lastname}', email = '{email}', " \
                                   f"phone = '{phone}' , address = '{address}', city ='{city}', state = '{state}', zip='{zipcode}' " \
                                   f"WHERE user_id = '{data['id']}';"

                    # mysql changes
                    cursor.execute(edit_profile)
                    connection.commit()

                    flash('Profile successfully updated.')
                    return redirect(url_for('views.home'))

                else:  # method = GET
                    return render_template("EditProfile.html", data=data)

    except Error as e:
        print(e)
        return render_template("EditProfile.html", data=0)
    except KeyError:
        return render_template("HomePage.html")


@views.route('/NewOrder', methods=["GET", "POST"])
def packDelivery():
    try:
        if session['loggedin']:
            return render_template("FuelQuoteForm.html")
    except KeyError:
        return render_template("HomePage.html")


@views.route('/submitFormToDB', methods=['POST'])
def SubmitQuoteForm():
    dest = request.form['dest']
    zipcode = request.form['zipcode']
    gallons = request.form['gallons']
    state = request.form['state']
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=database
        ) as connection:
            print(connection)
            if dest is None:
                print("is none")
            # doing something
            if zipcode and gallons and state != "text" and dest:

                with connection.cursor(buffered=True) as cursor:

                    if zipcode != '00000':
                        print(session['username'])
                        trackQ = "SELECT count(*) FROM quotes WHERE email = '" + session['username'] + "';"
                    else:
                        trackQ = "SELECT count(*) FROM quotes WHERE email = 'homie@mail.com';"

                    # numOfRow = cursor.execute(trackQ)
                    cursor.execute(trackQ)
                    number_of_rows = cursor.fetchone()
                    number_of_rows = number_of_rows[0]

                    print(f"Submit number_of_rows  = {number_of_rows}")

                    # numOfRow = cursor.execute(trackQ)

                    # check
                    currentPrice = 1.5

                    if state == "TX":
                        locationFactor = 0.02
                    else:
                        locationFactor = 0.04

                    if number_of_rows is None or number_of_rows == 0:
                        print("hasnotdonebizzbefore")
                        rateHistoryFactor = 0.0
                    else:
                        print("hasdonebizzbefore")
                        rateHistoryFactor = 0.01

                    if int(gallons) > 1000:
                        gallonsReqFactor = 0.02
                    else:
                        gallonsReqFactor = 0.03

                    companyProfitFactor = 0.1

                    margin = currentPrice * (locationFactor
                                             - rateHistoryFactor
                                             + gallonsReqFactor
                                             + companyProfitFactor)
                    suggestedPrice = currentPrice + margin
                    totalPrice = float(gallons) * suggestedPrice
                    totalPrice = float("%.2f" % totalPrice)

                    # cost = "$" + str(suggestedPrice)
                    totalcost = str(totalPrice)

                    # Margin => (.02 - .01 + .02 + .1) * 1.50 = .195
                    # Suggested Price/gallon => 1.50 + .195 = $1.695
                    # Total Amount Due => 1500 * 1.695 = $2542.50

                    if zipcode != '00000':
                        trackQ = "INSERT INTO quotes(email, dest, quantity, total, date, zip, state) VALUES('" \
                                 + str(session['username']) + "', '" \
                                 + str(dest) + "', '" \
                                 + str(gallons) + "','" \
                                 + str(totalcost) + "', " + "NOW() ,'" \
                                 + str(zipcode) + "', '" \
                                 + str(state) + "');"
                    else:
                        trackQ = "INSERT INTO quotes(email, dest, quantity, total, date, zip, state) VALUES('homie@mail.com', '" \
                                 + str(dest) + "', '" \
                                 + str(gallons) + "','" \
                                 + str(totalcost) + "', " + "NOW() ,'" \
                                 + str(zipcode) + "', '" \
                                 + str(state) + "');"
                    cursor.execute(trackQ)

                    connection.commit()
                    return jsonify({'success': 'didit!'})

            return jsonify({'error': 'Missing data!'})
    except Error as e:
        print(e)


@views.route('/quoteCalc', methods=['POST'])
def CalcProcess():
    zipcode = request.form['zipcode']
    gallons = request.form['gallons']
    state = request.form['state']

    if state == "text":
        return jsonify({'error': 'Missing data!'})

    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=database
        ) as connection:
            print(connection)
            # query
            with connection.cursor(buffered=True) as cursor:
                # SELECT count(*) FROM quotes WHERE email = 'homie@mail.com';
                if zipcode != '00000':
                    print(session['username'])
                    trackQ = "SELECT count(*) FROM quotes WHERE email = '" + session['username'] + "';"
                else:
                    trackQ = "SELECT count(*) FROM quotes WHERE email = 'homie@mail.com';"
                # numOfRow = cursor.execute(trackQ)
                cursor.execute(trackQ)
                number_of_rows = cursor.fetchone()

                number_of_rows = number_of_rows[0]
                # check
                currentPrice = 1.5

                if state == "TX":
                    locationFactor = 0.02
                else:
                    locationFactor = 0.04

                if number_of_rows is None or number_of_rows == 0:
                    print("hasnotdonebizzbefore")
                    rateHistoryFactor = 0.0
                else:
                    print("hasdonebizzbefore")
                    rateHistoryFactor = 0.01

                if int(gallons) > 1000:
                    gallonsReqFactor = 0.02
                else:
                    gallonsReqFactor = 0.03

                companyProfitFactor = 0.1

                margin = currentPrice * (locationFactor
                                         - rateHistoryFactor
                                         + gallonsReqFactor
                                         + companyProfitFactor)
                suggestedPrice = currentPrice + margin
                totalPrice = float(gallons) * suggestedPrice
                totalPrice = format(totalPrice, '.2f')

                # Margin => (.02 - .01 + .02 + .1) * 1.50 = .195
                # Suggested Price/gallon => 1.50 + .195 = $1.695
                # Total Amount Due => 1500 * 1.695 = $2542.50
                if zipcode and gallons:
                    cost = "$" + str(suggestedPrice)
                    totalcost = "$" + str(totalPrice)

                    return jsonify({"cost": cost, "totalcost": totalcost})

            return jsonify({'error': 'Missing data!'})

    except Error as e:
        print(e)


@views.route('/report')
def report():
    try:
        if session['loggedin']:
            return render_template("ReportRequestPage.html")
    except KeyError:
        return render_template("HomePage.html")


@views.route('/report', methods=["POST"])
def outputReport():
    try:
        if session['loggedin']:
            startDate = request.form.get('start')
            endDate = request.form.get('end')
            startDate = startDate + " 00:00:00"
            endDate = endDate + " 23:59:59"
            netRevenue = 0
            print(f"startDate = {startDate}, endDate = {endDate}")
            headers = ['Quote ID', 'Client', 'Address', 'Quantity', 'Total Price', 'Date']
            sqlQuery = f"SELECT * FROM group_5_db.quotes WHERE date BETWEEN '{startDate}' AND '{endDate}' AND email = '{session['username']}';"

            if startDate > endDate:
                flash("Start date cannot be greater than End date.")
                return redirect(url_for('views.outputReport'))

            with connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database
            ) as connection:
                cursor = connection.cursor(buffered=True)
                cursor.execute(sqlQuery)
                result = cursor.fetchall()
                if len(result) == 0:
                    flash("No items in the database")
                    return redirect(url_for('views.outputReport'))
                data = []
                for row in result:
                    data_row = list(row)
                    date = row[2] + ", " + row[7] + ", " + str(row[6])
                    data_row[4] = "$" + data_row[4]
                    del (data_row[7])
                    del (data_row[6])
                    del (data_row[2])
                    data_row.insert(2, date)
                    data.append(data_row)
                    netRevenue += float(row[4])
                netRevenue = format(netRevenue, '.2f')
                return render_template("ReportOutput.html", heading=headers, data=data,
                                       date_start=startDate,
                                       date_end=endDate, search_type="Customer ID", revenue=netRevenue,
                                       num_items=len(result))
    except KeyError:
        return render_template("HomePage.html")


@views.route('/')
def index():
    return render_template('HomePage.html')


# Change Password
@views.route('/changePassword', methods=['GET', 'POST'])
def changePassword():
    if request.method == 'POST':
        try:
            if session['loggedin']:
                with connect(
                        host=host,
                        user=user,
                        password=password,
                        database=database
                ) as connection:
                    print(connection)
                    cursor = connection.cursor(buffered=True)

                    oldPass = request.form.get('oldpasswd')
                    newPass = request.form.get('newpasswd')

                    cursor.execute(f"SELECT * FROM users WHERE email = '{session['username']}';")
                    account = cursor.fetchone()
                    authenticate = check_password_hash(account[9], oldPass)
                    if not authenticate:  # If user enters wrong current password
                        flash('Current password is incorrect. Please enter your current password to change password.')
                        return redirect(url_for('views.changePassword'))

                    confirmPass = request.form.get('confirmpasswd')
                    if newPass != confirmPass:  # If password and confirmation do not match
                        flash('Passwords do not match. Enter desired new password and then confirm desired new password.')
                        return redirect(url_for('views.changePassword'))

                    if oldPass == newPass:  # If old password and new password are the same
                        flash('Current password is the same as desired new password.')
                        return redirect(url_for('views.changePassword'))

                    passHash = generate_password_hash(newPass, method='sha256')
                    update_password = f"UPDATE users SET password = '{passHash}' WHERE email = '{session['username']}';"

                    cursor.execute(update_password)
                    connection.commit()

                    flash('Password successfully changed.')
                    return redirect(url_for('views.home'))
        except Error as e:
            print(e)
        except KeyError:
            return render_template("HomePage.html")

    return render_template('ChangePassword.html')
