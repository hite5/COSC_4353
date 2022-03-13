from flask import Flask, request, render_template, redirect, url_for, request, Blueprint, flash, current_app, jsonify
from mysql.connector import connect, Error
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from . import db
from .models import User
import datetime
import pgeocode


views = Blueprint('views', __name__)

host = "localhost"
user = "root"
password = "coogshouse"
database = "group_5_db"

# Home Page | Work on redirecting to different pages
@views.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('KEEPhomePage.html', name=current_user.name.capitalize())
    return render_template("KEEPhomePage.html")


@views.route('/employee', methods=["GET", "POST"])
@login_required
def loggedIn():
    return render_template("KEEPhomePage.html", name=current_user.name.capitalize(),
                           type=current_user.type.capitalize())


@views.route('/NewCustomerForm', methods=["GET", "POST"])
def NewCustomerForm():
    if request.method == "POST":
        fname = request.form.get("f_name")
        lname = request.form.get("l_name")
        email = request.form.get("email")
        passW = request.form.get("newpasswd")
        phone = request.form.get("phoneNum")
        address = request.form.get("Address")
        city = request.form.get("City")
        state = request.form.get("state")
        zip = request.form.get("zipcode")

        #if user already exists, redirect back to signup form
        user1 = User.query.filter_by(email=email).first()
        if user1:
            flash('Email address already exists')
            return redirect(url_for('views.NewCustomerForm'))

         # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(email = email, name = fname,
                        password = generate_password_hash(passW, method='sha256'))

        try:
            with connect(
                host = host,
                user = user,
                password = password,
                database = database
            ) as connection:
                print(connection)

                insert_customer = "INSERT INTO users (first_name, last_name, email, password, phone, address, city, state, zip) " \
                                  "VALUES " \
                                  "('" + fname + "','" + lname + "','" + email + "','" + passW + "','" + phone + "'," \
                                    "'" + address + "','" + city + "','" + state + "','" + zip + "');"

                with connection.cursor(buffered=True) as cursor:

                    print("Successfully inputted data into DB")

                    cursor.execute(insert_customer)
                    connection.commit()

                    db.session.add(new_user)
                    db.session.commit()

        except Error as e:
            print(e)
    return render_template("NewCustomerForm.html")



@views.route('/EditProfile', methods=["GET", "POST"])
@login_required
def EditProfile():
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=database
        ) as connection:
            cursor = connection.cursor(buffered=True)
            query = f"SELECT first_name, last_name, email, phone, user_id FROM users WHERE email = '{current_user.email}'"
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
            }

            if request.method == "POST":
                # Retrieve form data
                firstname = request.form.get('fname')
                lastname = request.form.get('lname')
                phone = request.form.get('phoneNum')
                address = request.form.get('Address')
                city = request.form.get('City')
                state = request.form.get('state')
                zip = request.form.get('zipcode')
                email = request.form.get('email')

                user1 = User.query.filter_by(email=email).first() # checking for email in sqlite

                emailquery = f"SELECT first_name FROM users WHERE email='{email}'" # checking for email in mysql
                cursor.execute(emailquery)
                emailcheck = cursor.fetchone()
                
                emailexists = user1 or emailcheck

                if (emailexists and (
                        current_user.email != email)):  # if a user is found, we want to redirect back to edit page so user can try again
                    flash('Email address belongs to another user. Please enter an email that belongs to you.')
                    return redirect(url_for('views.EditProfile'))

                phone = request.form.get('phoneNum')

                edit_profile = f"UPDATE users SET first_name = '{firstname}', last_name = '{lastname}', email = '{email}', phone = '{phone}' , address = '{address}', city ='{city}', state = '{state}', zip='{zip}' WHERE user_id = '{data['id']}';"
                
                # mysql changes
                cursor.execute(edit_profile)
                connection.commit()

                # sqlite changes
                current_user.name = firstname
                current_user.email = email
                db.session.commit()
                flash('Profile successfully updated.')
                return redirect(url_for('views.EditProfile'))

            else:  # GET
                return render_template("EditProfile.html", data=data)

    except Error as e:
        print(e)
        return render_template("EditProfile.html", data=0)


@views.route('/NewOrder', methods=["GET", "POST"]) # pragma: no cover
@login_required
def packDelivery():
  return render_template("KEEPfuelQuoteForm.html")


@views.route('/heelo') # pragma: no cover
def dosomething():
    return render_template("testingAjax.html")

# @views.route('/process', methods=['POST'])
# def process():
#     email = request.form['email']
#     name = request.form['name']
#
#     if name and email:
#         newName = name[::-1]
#
#         return jsonify({'name' : newName})
#
#     return jsonify({'error' : 'Missing data!'})

@views.route('/submitFormToDB', methods=['POST'])
def SubmitQuoteForm():
    dest = request.form['dest']
    zipcode = request.form['zipcode']
    gallons = request.form['gallons']
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=database
        ) as connection:
            print(connection)
            #doing something
            if zipcode and gallons:
                #dist = pgeocode.GeoDistance('US')
                #newdist = dist.query_postal_code("77204", zipcode)
                cost = 10 * int(gallons)
                totalcost = int(cost + (float(cost)*0.085))
                #cost = "$" + str(cost)
                totalcost = "$" + str(totalcost)

                with connection.cursor(buffered=True) as cursor:
                    trackQ = "INSERT INTO quotes(email, dest, quantity, shipping, tax, total, date, zip) VALUES('" + str(current_user.email) + "', '" + str(dest) + "', '" + str(gallons) + "', '1', '1', '" + str(totalcost) + "', " + "NOW() ,'" + str(zipcode) + "');"
                    cursor.execute(trackQ)


                    # query = f"SELECT quote_id FROM quotes WHERE email = '{current_user.email}'"
                    # cursor.execute(query)
                    # result = cursor.fetchone()
                    # data = {"quoteid" : result[0]}
                    # print(data)


                    connection.commit()
                    return jsonify({'success': 'didit!'})


            return jsonify({'error': 'Missing data!'})


    except Error as e:
        print(e)






@views.route('/quoteCalc', methods=['POST'])
def CalcProcess():
    zipcode = request.form['zipcode']
    gallons = request.form['gallons']

    if zipcode and gallons:
        #dist = pgeocode.GeoDistance('US')
        #newdist = dist.query_postal_code("77204", zipcode)
        cost = 10 * int(gallons)
        #totalcost = int(cost + (newdist * 7))
        totalcost = int(cost + (float(cost) * 0.085))
        cost = "$" + str(cost)
        totalcost = "$" + str(totalcost)


        return jsonify({"cost": cost, "totalcost": totalcost})

    return jsonify({'error' : 'Missing data!'})



# @views.route('/submitPkgUpdate', methods=["GET","POST"])
# def submitPkgUpdate()
#     return render_template("PakageUpdateConfirmation.html")


@views.route('/report')
@login_required
def report():
    return render_template("ReportRequestPage.html")


if __name__ == '_@views__':
    views.run()


@views.route('/')
def index():
    return render_template('KEEPhomePage.html')

# Change Password
@views.route('/changePassword', methods=['GET','POST'])
@login_required
def changePassword():
    if request.method == 'POST':
        oldPass = request.form.get('oldpasswd')
        if (not check_password_hash(current_user.password, oldPass)): # If user enters wrong current password
            flash('Current password is incorrect. Please enter your current password to change password.')
            return redirect(url_for('views.changePassword'))
        newPass = request.form.get('newpasswd')
        confirmPass = request.form.get('confirmpasswd')
        if (newPass != confirmPass): # If password and confirmation do not match
            flash('Passwords do not match. Enter desired new password and then confirm desired new password.')
            return redirect(url_for('views.changePassword'))
        if (oldPass == newPass): # If old password and new password are the same
            flash('Current password is the same as desired new password.')
            return redirect(url_for('views.changePassword'))

        try:
            with connect(
                host=host,
                user=user,
                password=password,
                database=database
            ) as connection:
                print(connection)

                update_password = f"UPDATE employee SET Emp_pwd = AES_ENCRYPT('{newPass}', '432A462D4A614E635266556A586E3272') WHERE email = '{current_user.email}';"

                with connection.cursor(buffered=True) as cursor:
                    cursor.execute(update_password)
                    connection.commit()
                
                current_user.password = generate_password_hash(newPass, method='sha256')
                db.session.commit()
                flash('Password successfully changed.')
                return redirect(url_for('views.changePassword'))
        except Error as e:
            print(e)

    return render_template('ChangePassword.html')