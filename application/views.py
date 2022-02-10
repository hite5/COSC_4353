from flask import Flask, request, render_template, redirect, url_for, request, Blueprint, flash, current_app
from mysql.connector import connect, Error
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from . import db
from .models import User, login_required_test
import datetime

views = Blueprint('views', __name__)

host = "team-8.mysql.database.azure.com"
user = "team8@team-8"
password = "Coogshouse#1"
database = "group_8_postoffice"

# Edit Customer Search
@views.route('/editCustomerSearch', methods=["GET", "POST"])
@login_required
def editCustomerSearch():
    if request.method == "POST":
        customerid = request.form.get("cid")
        try:
            with connect(
                host=host,
                user=user,
                password=password,
                database=database
            ) as connection:
                cursor = connection.cursor(buffered=True)
                query = f"SELECT Fname FROM customer WHERE Cust_ID = '{customerid}'"
                cursor.execute(query)
                result = cursor.fetchone()
                if result is None:
                    flash('Customer with that ID does not exist. Please enter a valid Customer ID.')
                    return redirect(url_for('views.editCustomerSearch'))
            return redirect(url_for('views.editCustomer', customerid=customerid)) # ADD IN CHECKS
        except Error as e:
            print(e)
    return render_template("EditCustomerSearch.html")

# Edit Customer
@views.route('/editCustomer/<customerid>', methods=["GET", "POST"])
@login_required
def editCustomer(customerid):
    try:
        with connect(
            host=host,
            user=user,
            password=password,
            database=database
        ) as connection:
            cursor = connection.cursor(buffered=True)
            findcustomer = f"SELECT Fname, lname, email, phone_no, address FROM customer WHERE Cust_ID = '{customerid}'"
            cursor.execute(findcustomer)
            result = cursor.fetchone()
            data = {
                "firstname": result[0],
                "lastname": result[1],
                "email": result[2],
                "phone": result[3],
                "address": result[4]
            }

            if request.method == "POST":
                # retrieve form data and change data in database
                firstname = request.form.get('fname')
                lastname = request.form.get('lname')
                email = request.form.get('email')
                phone = request.form.get('phoneNum')
                address = request.form.get('address')
                
                editdetails = f"UPDATE customer SET Fname = '{firstname}', lname = '{lastname}', email = '{email}', phone_no = '{phone}', address = '{address}' WHERE Cust_ID = '{customerid}'"
                cursor.execute(editdetails)
                connection.commit()
                flash('Customer details successfully updated.')
                return redirect(url_for('views.editCustomer', customerid = customerid))
                
            return render_template("EditCustomer.html", data=data)
    except Error as e:
        print(e)


# Home Page | Work on redirecting to different pages
@views.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('homePage.html', name=current_user.name.capitalize(),
                               type=current_user.type.capitalize())
    return render_template("homePage.html")


@views.route('/employee', methods=["GET", "POST"])
@login_required
def loggedIn():
    return render_template("homePage.html", name=current_user.name.capitalize(),
                           type=current_user.type.capitalize())


@views.route('/packageTracker')
def packTracker():
    return render_template("packageTracker.html")


@views.route('/packageTracker', methods=['POST'])
def tracking():
    packageID = request.form.get("trackID")
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=database
        ) as connection:
            print(connection)
            cursor = connection.cursor(buffered=True)

            track = "SELECT current_office_num AS `Office Number`, departure, arrival FROM tracking WHERE " \
                    "Package_ID = " + packageID + " ORDER BY arrival DESC; "

            package = "SELECT P_type, isFragile, weight, insurance, status, delivered_time, Reciever, price, " \
                      "length, width, height FROM package WHERE ID = " + packageID + "; "

            branch = ["Houston", "Dallas", "Austin", "San Antonio", "El Paso"]

            cursor.execute(package)
            result = cursor.fetchone()
            if result is None:
                flash('Package does not exist.')
                return redirect(url_for('views.packTracker'))
            print(result)
            pack = {"priority": result[0],
                    "isFragile": result[1],
                    "weight": result[2],
                    "ins": result[3],
                    "status": result[4],
                    "delivered": result[5],
                    "sender": result[6],
                    "receiver": result[6],
                    "price": result[7],
                    "length": result[8],
                    "width": result[9],
                    "height": result[10]
                    }
            if pack["isFragile"] == 1:
                pack['isFragile'] = 'Yes'
            else:
                pack['isFragile'] = 'No'

            if pack["priority"] == 'p':
                pack['priority'] = 'Priority'
            elif pack["priority"] == 's':
                pack['priority'] = 'Standard'

            if pack["ins"] == 1:
                pack['ins'] = "Yes"
            else:
                pack['ins'] = "No"

            recID = "SELECT Fname, lname, email, phone_no, address FROM customer WHERE Cust_ID =" + str(
                pack["receiver"]) + ";"
            cursor.execute(recID)
            result = cursor.fetchone()

            recCustomer = {"Name": result[0] + " " + result[1],
                           "email": result[2],
                           "phone_no": result[3],
                           "address": result[4]
                           }

            trackHistory = []
            cursor.execute(track)
            result = cursor.fetchall()
            for i in range(len(result)):
                x = result[i][2]
                y = result[i][1]
                print(y)
                if y is None:
                    trackHistory.append("At " + x.strftime('%c') + " your package arrived at our " + branch[
                        result[i][0] - 1] + " branch.")
                else:
                    trackHistory.append("At " + x.strftime('%c') + " your package arrived at our " + branch[
                        result[i][0] - 1] + " branch. It left that facility at: " + y.strftime('%c'))

            deliveredTimeQ = f"SELECT delivered_time FROM package WHERE ID = {packageID}"


            if pack["status"] == "pending":
                pack["status"] = "Your package is in transit."
            elif pack["status"] == "returned":
                cursor.execute(deliveredTimeQ)
                result = cursor.fetchone()
                deliveredDate = result[0].strftime('%x')
                deliveredTime = result[0].strftime('%X')
                pack["status"] = "Your package was returned at: " + deliveredDate + " " + deliveredTime
            else:
                cursor.execute(deliveredTimeQ)
                result = cursor.fetchone()
                deliveredDate = result[0].strftime('%x')
                deliveredTime = result[0].strftime('%X')
                pack['status'] = 'Your package was delivered at: ' + deliveredDate + " " + deliveredTime

        return render_template("TrackingLandingPage.html", packID=packageID, trackpack=pack, customer=recCustomer,
                               history=trackHistory)

    except Error as e:
        print(e)


@views.route('/NewCustomerForm', methods=["GET", "POST"])
def NewCustomerForm():
    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        passW = request.form.get("passW")
        email = request.form.get("email")
        phoneNum = request.form.get("phoneNum")
        cust_address = request.form.get("cust_address")

        #if user already exists, redirect back to signup form
        user1 = User.query.filter_by(email=email).first()
        if user1:
            flash('Email address already exists')
            return redirect(url_for('views.NewCustomerForm'))

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

                # ADD SEQUEL SHIT
                insert_customer = "" #do dis

                with connection.cursor(buffered=True) as cursor:
                    #cursor.execute(insert_customer)
                    #connection.commit()
                    cursor.execute(query)
                    temp = cursor.fetchone()
                    print("Successfully inputted data into DB")

                    if temp is not None:
                        flash('Email already exists')
                        return redirect(url_for('views.NewCustomerForm'))
                    else:
                        cursor.execute(insert_customer)
                        connection.commit()
                        cursor.execute(query)
                        temp = cursor.fetchone()

                        db.session.add(new_user)
                        db.session.commit()

                        custInfo = {
                            "fname": fname,
                            "lname": lname,
                            "email": email,
                            "phoneNum": phoneNum,
                            "cust_address": cust_address
                        }
                        return render_template("CustomerConfirmation.html", info=custInfo)
        except Error as e:
            print(e)
    return render_template("NewCustomerForm.html")


@views.route('/EditEmployee', methods=["GET", "POST"])
@login_required
def editEmployee():
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=database
        ) as connection:
            cursor = connection.cursor(buffered=True)
            query = f"SELECT F_Name, L_Name, email, Ph_num, Emp_ID FROM employee WHERE email = '{current_user.email}'"
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
                "id": result[4]
            }

            if request.method == "POST":
                # Retrieve form data
                firstname = request.form.get('fname')
                lastname = request.form.get('lname')

                email = request.form.get('email')
                user1 = User.query.filter_by(email=email).first() # checking for email in sqlite

                emailquery = f"SELECT F_name FROM employee WHERE email='{email}'" # checking for email in mysql
                cursor.execute(emailquery)
                emailcheck = cursor.fetchone()
                
                emailexists = user1 or emailcheck

                if (emailexists and (
                        current_user.email != email)):  # if a user is found, we want to redirect back to edit page so user can try again
                    flash('Email address belongs to another employee. Please enter an email that belongs to you.')
                    return redirect(url_for('views.editEmployee'))

                phone = request.form.get('phoneNum')

                edit_employee = f"UPDATE employee SET F_Name = '{firstname}', L_Name = '{lastname}', email = '{email}', Ph_num = '{phone}' WHERE Emp_ID = '{data['id']}';"
                
                # mysql changes
                cursor.execute(edit_employee)
                connection.commit()

                # sqlite changes
                current_user.name = firstname
                current_user.email = email
                db.session.commit()
                flash('Profile successfully updated.')
                return redirect(url_for('views.editEmployee'))

            else:  # GET
                return render_template("EditProfile.html", data=data)

    except Error as e:
        print(e)
        return render_template("EditProfile.html", data=0)


@views.route('/NewPackage', methods=["GET", "POST"])
@login_required
def packDelivery():
    if request.method == "POST":
        send_fname = request.form.get("s_fname")
        send_lname = request.form.get("s_lname")
        rec_fname = request.form.get("r_fname")
        rec_lname = request.form.get("r_lname")
        send_email = request.form.get("s_email")
        send_phoneNum = request.form.get("s_phoneNum")
        rec_email = request.form.get("r_email")
        rec_phoneNum = request.form.get("r_phoneNum")
        return_add = request.form.get("custAdd")
        destAddress = request.form.get("destAdd")
        weight = int(request.form.get("weight"))
        width = int(request.form.get("width"))
        height = int(request.form.get("height"))
        length = int(request.form.get("length"))
        checkboxes = request.form.getlist("etc")
        delivery = int(request.form.get("delivery"))
        employeeID = request.form.get("employeeID")
        fragile = 0
        insurance = 1
        for checks in checkboxes:
            if checks == '20':
                fragile = 1
            elif checks == '30':
                insurance = 1.2

        price = ((width * height * length) * weight) * .01 * insurance * delivery
        price = ("%.2f" % price)
        print(price)
        # add a redirect to bring the user to a page where it shows that your package is being sent
        # and what the cost of the package is.
        # return redirect(url_for('packTracker'))

        try:
            with connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database
            ) as connection:
                print(connection)

                # Need to make a query to the DB and check to see if there is matching values
                # for the sending customer or the receiving customer
                # If there isn't a record of the receiving customer:
                # Create a new customer
                # If there isn't a record of the sending customer:
                # Create a new customer
                # If there isn't a record of both:
                # Create two new customers
                # Else skip creating customers

                # Take the customer information (in particular the customer ID) that was either created or queried,
                # and create a new package entry for the database.
                # Make sure that we have the receiving customer's customerID
                # and sender's customerID to add to the package entry.
                # insert_package = "INSERT INTO package VALUES (1001,'p',0,8,100,1,'pending',now(),007,1,00.00);"
                show_change = "select * from customer;"
                # show_package = "select * from package;"

                with connection.cursor(buffered=True) as cursor:
                    # query to get the branchID based off the employeeID inserting it.
                    branchQ = """SELECT office_num
                                                 FROM employee
                                                 WHERE Emp_ID = """ + employeeID + ';'
                    cursor.execute(branchQ)
                    branchResult = cursor.fetchone()
                    if branchResult is None:
                        flash("Employee ID is invalid")
                        return redirect(url_for('views.packDelivery'))
                    branchID = branchResult[0]
                    s_query = "SELECT Cust_ID FROM customer WHERE Fname = '" + send_fname + "' AND lname = '" + send_lname + "' AND email = '" + send_email + "' AND phone_no = '" + send_phoneNum + "' AND address = '" + return_add + "';"

                    r_query = "SELECT Cust_ID FROM customer WHERE Fname = '" + rec_fname + "' AND lname = '" + rec_lname + "' AND email = '" + rec_email + "' AND phone_no = '" + rec_phoneNum + "' AND address = '" + destAddress + "';"
                    cursor.execute(s_query) # returns none or what the db has for this customer
                    senderResult = cursor.fetchone()

                    if senderResult is None:
                        print("Sender query")
                        # no results, insert into customer table
                        # call cursor.execute again and get temp[0] as the sender ID
                        insert_customer = "INSERT INTO customer (fname, lname, email, phone_no, address, date_joined) VALUES ('" \
                                          + send_fname + "','" + send_lname + "','" + send_email + "','" + send_phoneNum \
                                          + "','" + return_add + "', now() );"
                        cursor.execute(insert_customer)
                        connection.commit()
                        print("In between insert_customer and s_query")
                        cursor.execute(s_query)
                        senderResult = cursor.fetchone() # returns result of the senders newly inserted info
                        print("Sender Result")
                        print(senderResult)


                    senderID = senderResult[0]

                    cursor.execute(r_query)
                    receiverResult = cursor.fetchone() # returns none or what the db has for this customer
                    if receiverResult == None:
                        print("\nReceiver query")
                        # no results, insert into customer table
                        # call cursor.execute again and get temp[0] as the sender ID
                        insert_customer = "INSERT INTO customer (fname, lname, email, phone_no, address, date_joined) VALUES ('" \
                                          + rec_fname + "','" + rec_lname + "','" + rec_email + "','" + rec_phoneNum \
                                          + "','" + destAddress + "', now() );"
                        cursor.execute(insert_customer)
                        connection.commit()
                        cursor.execute(r_query)
                        receiverResult = cursor.fetchone() # returns result of the senders newly inserted info
                        print("Receiver Result ======== ")
                        print(receiverResult)

                    recID = receiverResult[0]

                    insert_package = "INSERT INTO package(P_type, isFragile, weight, " \
                                     "insurance, status, Sender, Reciever, length, width, height)"

                    if delivery == 1:
                        if insurance == 1:
                            insert_package += " VALUES('s'" \
                                              ", " + str(fragile) + " , " + str(weight) + ", 0, " \
                                                                                          "'pending', " + str(
                                senderID) + " , " + str(recID) + ", " \
                                                                 " " + str(length) + ", " + str(width) + ", " + str(
                                height) + ");"
                            priority = 's'
                            insurance1 = 0

                        else:
                            priority = 's'
                            insurance1 = 1
                            insert_package += " VALUES('s'" \
                                              ", " + str(fragile) + " , " + str(weight) + ", 1, " \
                                                                                          "'pending', " + str(
                                senderID) + " , " + str(recID) + ", " \
                                                                 " " + str(length) + ", " + str(width) + ", " + str(
                                height) + ");"

                    else:
                        if (insurance == 1):
                            priority = 'p'
                            insurance1 = 0
                            insert_package += " VALUES('p', " + str(fragile) + " , " + str(weight) + ", 0, 'pending" \
                                              "', " + str(senderID) + " , " + str(recID) + ",  " + str(length) + ", " + str(width) + ", " + str(height) + ");"
                        else:
                            priority = 'p'
                            insurance1 = 1
                            insert_package += " VALUES('p', " + str(fragile) + " , " + str(weight) + ", 1, 'pending', " \
                                              "" + str(senderID) + " , " + str(recID) + ", " + str(length) + ", " + str(width) + ", " + str(height) + ");"


                    cursor.execute(insert_package)
                    print("Insert Package query")
                    connection.commit()

                    getPackageID = "SELECT package.ID FROM package " \
                                   "WHERE P_type = '" + priority + "' AND isFragile = " + str(fragile) + "" \
                                   " AND weight = " + str(weight) + " AND insurance = " + str(insurance1) + " AND " \
                                   "status = 'pending' AND Sender = " + str(senderID) + " " \
                                    "AND Reciever = " + str(recID) + " AND length= " + str(length) + " AND " \
                                    "width= " + str(width) + " AND height = " + str(height) + ";"
                    cursor.execute(getPackageID)
                    print("Get Package ID query")
                    packageIDResults = cursor.fetchone()
                    print(packageIDResults)
                    print("successfully inputted data into the database")

                    orderInfo = {
                        "send_fname": send_fname,
                        "send_lname": send_lname,
                        "rec_fname": rec_fname,
                        "rec_lname": rec_lname,
                        "send_email": send_email,
                        "send_phoneNum": send_phoneNum,
                        "rec_email": rec_email,
                        "rec_phoneNum": rec_phoneNum,
                        "return_add": return_add,
                        "dest_add": destAddress,
                        "weight": weight,
                        "width": width,
                        "height": height,
                        "length": length,
                        "checkboxes": checkboxes,
                        "delivery": delivery,
                        "branch_id": branchID,
                        "fragile": fragile,
                        "insurance": insurance,
                        "pkgID": packageIDResults[0],
                        "price": price,
                        "empID": employeeID
                    }
                    trackQ = """INSERT INTO tracking(current_office_num, arrival, Package_ID, employee)
                             VALUES(""" + str(branchID) + ", NOW()," + str(orderInfo['pkgID']) + ", " + str(employeeID) + ');'

                    cursor.execute(trackQ)
                    connection.commit()

        except Error as e:
            print(e)

        # return render_template(url_for("ConfirmationPage.html", priceDisp = price))
        # TODO: use confirmationPage here using url_for



        return render_template("ConfirmationPage.html", info=orderInfo)

    return render_template("shippingForm.html")


@views.route('/Submitted', methods=["GET", "POST"])
def confirmationPage(pagePrice):
    return render_template("ConfirmationPage.html", priceDisp=pagePrice)


# @views.route('/submitPkgUpdate', methods=["GET","POST"])
# def submitPkgUpdate()
#     return render_template("PakageUpdateConfirmation.html")


@views.route('/TrackingInfo', methods=["GET", "POST"])
def trackingInfo(order):
    return render_template("TrackingLandingPage.html", thisOrder=order)


if __name__ == '_@views__':
    views.run()


@views.route('/')
def index():
    return render_template('homePage.html')


@views.route('/packageUpdateForm', methods=["GET", "POST"])
@login_required
def packageUpdateForm():
    if request.method == "POST":
        packageID = request.form.get("packageID")
        empID = request.form.get("employeeID")
        status = request.form.get("delivery")

        try:
            with connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database
            ) as connection:
                print(connection)

                employeeIDQ = "SELECT Emp_ID, office_num, delete_flag FROM employee WHERE Emp_ID = " + empID + ";"
                packageQ = "SELECT Package_ID, departure, current_office_num, package.delete_flag, status, Tracking_ID " \
                           "FROM tracking, package " \
                           "WHERE tracking.Package_ID = " + packageID + " AND package.ID = " + packageID + \
                           ' ORDER BY Tracking_ID DESC;'
                delivered = "UPDATE package SET status = '" + status + "' WHERE ID = " + packageID + ";"

                with connection.cursor(buffered=True) as cursor:
                    cursor.execute(employeeIDQ)
                    result = cursor.fetchall()
                    if len(result) == 0:  # if employee ID isn't valid send them back with error
                        flash("Employee doesn't exist.")
                        return redirect(url_for('views.packageUpdateForm'))

                    for row in result:
                        branchID = row[1]
                        emp_dflag = row[2]

                    cursor.execute(packageQ)
                    result = cursor.fetchone()
                    if result is None:  # if Package ID isn't valid send them back with error
                        flash("Package doesn't exist.")
                        return redirect(url_for('views.packageUpdateForm'))
                    print(result)
                    depart = result[1]
                    packCurrOfficeNum = result[2]
                    p_dflag = result[3]
                    stat = result[4]
                    print("Depart below:")
                    print(depart)
                    if emp_dflag == 1:  # if employee had delete_flag == 1 ====> not valid
                        flash("Employee doesn't exist.")
                        return redirect(url_for('views.packageUpdateForm'))

                    if p_dflag == 1:  # if employee had delete_flag == 1 ====> not valid
                        flash("Package doesn't exist.")
                        return redirect(url_for('views.packageUpdateForm'))

                    if stat == "delivered":  # if db status is delivered or returned ==> not valid
                        flash("Package has been delivered")
                        return redirect(url_for('views.packageUpdateForm'))

                    elif stat == "returned":  # if db status is delivered or returned ==> not valid
                        flash("Package has been returned.")
                        return redirect(url_for('views.packageUpdateForm'))

                    else: # if db status is pending
                        print("Package is in transit")
                        arriving = "INSERT INTO tracking (current_office_num, arrival, Package_ID, employee)" \
                                   "VALUES ('" + str(branchID) + "', NOW(), '" + packageID + "', '" + empID + "');"

                        departing = "SELECT Tracking_ID FROM tracking " \
                                    "WHERE employee = '" + empID + "' AND " \
                                                                   "Package_ID = '" + packageID + "' AND " \
                                                                                                  "current_office_num = '" + str(branchID) + "' AND departure is NULL;  "

                        if status == "arriving":
                            if depart is None:  # if package has null departure ===> not valid
                                flash("Package hasn't arrived to the branch yet.")
                                return redirect(url_for('views.packageUpdateForm'))

                            cursor.execute(arriving)

                        elif status == "departing":  # if office_num and curr_office_num aren't equal ===> not valid.
                            if packCurrOfficeNum != branchID:
                                flash("Package has not left previous branch.")
                                return redirect(url_for('views.packageUpdateForm'))
                            cursor.execute(departing)
                            temp = cursor.fetchone()
                            if temp is None:
                                flash("Employee is not in charge of that package.")
                                return redirect(url_for('views.packageUpdateForm'))
                            print("temp = " + str(temp[0]))
                            departing2 = "UPDATE tracking SET departure = NOW() WHERE Tracking_ID = '" + str(
                                temp[0]) + "';"
                            cursor.execute(departing2)

                        elif status == "delivered" or status == "returned":
                            print("In webpage status.")
                            print("Depart below:")
                            print(depart)
                            if depart is None:  # if package has null departure ===> not valid
                                flash("Package cannot be delivered has not left previous branch.")
                                return redirect(url_for('views.packageUpdateForm'))
                            cursor.execute(delivered)

                        else:
                            print("error")

                        connection.commit()
                        print("successfully updated database")
        #
        except Error as e:
            print(e)
        #
        updateInfo = {
            "pkgID": packageID,
            "type" : status,
            "empID": empID,
            "branchID": branchID
        }

        return render_template("PackageUpdateConfirmation.html", info=updateInfo)

    return render_template("PackageUpdateForm.html")



@views.route('/customerSearch')
@login_required
def customerSearch():
    return render_template("CustomerSearch.html")

@views.route('/customerSearch', methods = ["POST"])
@login_required
def custQuery():
    with connect(
            host=host,
            user=user,
            password=password,
            database=database
    ) as connection:
        print(connection)
        cursor = connection.cursor(buffered=True)

        custID = request.form.get("IDsearch")
        lname = request.form.get("nameSearch")

        if custID is not None:
            cid = request.form.get("cid")
            if cid == "":
                flash('Please input data in the desired search field.')
                return redirect(url_for('views.customerSearch'))

            # cquery = f" SELECT Fname, lname, Cust_ID, email, phone_no, address, date_joined WHERE Cust_ID = '{cid}'; "
            cquery = "SELECT Fname, lname, Cust_ID, email, phone_no, address, date_joined " \
                     "FROM customer WHERE Cust_ID = "+cid+" ;"

            cursor.execute(cquery)
            result = cursor.fetchall()
            if len(result)==0:
                flash('Customer does not exist.')
                return redirect(url_for('views.customerSearch'))
            data = []
            for row in result:
                # print(row)
                data.append(row)
            headers = ['First Name', 'Last Name', 'ID ', 'Email', 'Phone Number', 'address', 'Date Joined']

            return render_template("QueryOutput.html", heading=headers, data=data, search_type="Customer ID",
                                   query=cid)
        elif lname is not None:
            # fpid = request.form.get("fname")
            lpid = request.form.get("lname")
            if lpid == "":
                flash('Please input data in the desired search field.','error')
                return redirect(url_for('views.customerSearch'))

            nmquery = " SELECT Fname, lname, Cust_ID, email, phone_no, address, date_joined " \
                      "FROM customer WHERE lname = '"+lpid+"';"

            cursor.execute(nmquery)
            result = cursor.fetchall()
            if len(result) == 0:
                flash("The customer does not exist.",'error')
                return redirect(url_for('views.customerSearch'))
            data = []
            for row in result:
                # print(row)
                data.append(row)
            headers = ['First Name', 'Last Name', 'ID ', 'Email', 'Phone Number', 'address', 'Date Joined']

            return render_template("QueryOutput.html", heading=headers, data=data, search_type="Customer Last Name",
                                   query=lpid)
        else:
            print("Error")

    return "Finished."


@views.route('/employeeSearch')#, methods=["GET", "POST"])
@login_required_test(role="supervisor")
def employeeSearch():
    return render_template("EmployeeSearch.html")

@views.route('/employeeSearch', methods = ["POST"])
@login_required_test(role="supervisor")
def empQuery():
    with connect(
            host=host,
            user=user,
            password=password,
            database=database
    ) as connection:
        print(connection)
        cursor = connection.cursor(buffered=True)

        branchID = request.form.get("branchSearch")
        empID = request.form.get("IDsearch")
        name = request.form.get("nameSearch")

        if branchID is not None:
            bid = request.form.get("branchID")
            if bid is None:
                flash('Please input data in the desired search field.')
                return redirect(url_for('views.employeeSearch'))
                # print("BID IS EMPTY")
            bquery = " SELECT Emp_ID, F_Name, L_Name, Ph_num, email, Employee_type, " \
                     "office_num, date_hired FROM employee WHERE office_num = " + bid + "; "
            cursor.execute(bquery)
            result = cursor.fetchall()
            data = []
            for row in result:
                # print(row)
                data.append(row)
            headers = ['Employee ID', 'First Name', 'Last Name', 'Phone Number', 'Email', 'Role', 'Branch ID', 'Date Hired']

            return render_template("QueryOutput.html", heading=headers, data=data, search_type="Branch ID",
                                   query=bid)

        elif empID is not None:
            eid = request.form.get("eid")
            if eid == "":
                flash('Please input data in the desired search field.', 'error')
                return redirect(url_for('views.employeeSearch'))

            equery = " SELECT Emp_ID, F_Name, L_Name, Ph_num, email, Employee_type, office_num," \
                     " date_hired FROM employee WHERE Emp_ID = " + eid + " ; "
            cursor.execute(equery)
            result = cursor.fetchall()
            if len(result) == 0:
                flash("The employee ID does not exist.", 'error')
                return redirect(url_for('views.employeeSearch'))
            data = []
            for row in result:
                # print(row)
                data.append(row)
            headers = ['Employee ID', 'First Name', 'Last Name', 'Phone Number', 'Email', 'Role', 'Branch ID',
                       'Date Hired']

            return render_template("QueryOutput.html", heading=headers, data=data, search_type="Employee ID",
                                   query=eid)

        elif name is not None:
            # fpid = request.form.get("fname")
            lpid = request.form.get("lname")
            if lpid == "":
                flash('Please input data in the desired search field.','error')
                return redirect(url_for('views.employeeSearch'))

            nquery = " SELECT Emp_ID, F_Name, L_Name, Ph_num, email, Employee_type, office_num," \
                    " date_hired FROM employee WHERE L_name = '" + lpid + "'; "
            cursor.execute(nquery)
            result = cursor.fetchall()
            if len(result) == 0:
                flash("The employee does not exist.",'error')
                return redirect(url_for('views.employeeSearch'))
            data = []
            for row in result:
                # print(row)
                data.append(row)
            headers = ['Employee ID', 'First Name', 'Last Name', 'Phone Number', 'Email', 'Role', 'Branch ID',
                       'Date Hired']

            return render_template("QueryOutput.html", heading=headers, data=data, search_type="Employee Last Name",
                                   query=lpid)

        else:
            print("Error")

        return "Finished."


@views.route('/packageSearch')
@login_required
def packSearch():
    return render_template("PackageSearch.html")


@views.route('/packageSearch', methods=["POST"])
@login_required
def packQuery():
    with connect(
            host=host,
            user=user,
            password=password,
            database=database
    ) as connection:
        print(connection)
        cursor = connection.cursor(buffered=True)

        branchSearch = request.form.get("branchSearch")
        empSearch = request.form.get("empSearch")
        pkgSearch = request.form.get("pkgSearch")
        custSearch = request.form.get("custSearch")

        if branchSearch is not None:
            print("BranchSearch")
            bid = request.form.get("bid")
            if bid is None:
                flash('Please input data in the desired search field.')
                return redirect(url_for('views.packSearch'))
            branchQuery = """SELECT ID, status, Sender, Reciever, price, length, width, height, employee
                    FROM package, tracking 
                    WHERE package.ID = Package_ID AND tracking.departure IS NULL AND tracking.current_office_num = """ \
                          + bid + ";"
            cursor.execute(branchQuery)
            result = cursor.fetchall()
            data = []
            for row in result:
                # print(row)
                data.append(row)
            headers = ['Package ID', 'Status', 'Sender', 'Receiver', 'Price', 'Length', 'Width', 'Height', 'Employee']

            return render_template("QueryOutput.html", heading=headers, data=data, search_type="Branch ID",
                                   query=bid)

        elif empSearch is not None:
            print("EmpSearch")
            eid = request.form.get("eid")
            if eid == "":
                flash('Please input data in the desired search field.')
                return redirect(url_for('views.packSearch'))
            empQuery = """SELECT ID, status, Sender, Reciever, price, length, width, height
                    FROM package, tracking
                    WHERE package.ID = Package_ID AND tracking.departure IS NULL AND tracking.employee = """ + eid + ';'
            cursor.execute(empQuery)
            result = cursor.fetchall()
            if len(result) == 0:
                flash("The employee ID does not exist.")
                return redirect(url_for('views.packSearch'))
            data = []
            for row in result:
                data.append(row)
            headers = ['Package ID', 'Status', 'Sender', 'Receiver', 'Price', 'Length', 'Width', 'Height']

            return render_template("QueryOutput.html", heading=headers, data=data, search_type="Employee ID",
                                   query=eid)

        elif pkgSearch is not None:
            print("pkgSearch")
            pid = request.form.get("pid")
            if pid == "":
                flash('Please input data in the desired search field.')
                return redirect(url_for('views.packSearch'))
            pkgQuery = """SELECT P_type, isFragile, weight, insurance, status, Sender, Reciever, price, length, width, 
            height, Fname, lname
            FROM package, customer
            WHERE package.ID = """ + pid + " AND customer.CUST_ID = Reciever; "
            cursor.execute(pkgQuery)
            result = cursor.fetchall()
            if len(result) == 0:
                flash("Your package ID does not exist.")
                return redirect(url_for('views.packSearch'))
            data = []
            for row in result:
                data.append(row)
            headers = ['Priority', 'Fragile', 'Weight', 'Insurance', 'Status', 'Sender', 'Reciever', 'Price', 'Length',
                       'Width', "Height", 'Receiver\'s First Name', 'Receiver\'s Last Name']

            return render_template("QueryOutput.html", heading=headers, data=data, search_type="Package ID",
                                   query=pid)


        elif custSearch is not None:
            print("custSearch")
            cid = request.form.get("cid")
            if cid == "":
                flash('Please input data in the desired search field.')
                return redirect(url_for('views.packSearch'))
            custQuery = """SELECT ID, status, Sender, Reciever, price, length, width, height
                    FROM package
                    WHERE Sender = """ + cid + " OR Reciever = " + cid + ";"
            cursor.execute(custQuery)
            result = cursor.fetchall()
            if len(result) == 0:
                flash("The customer you inputted doesn't exist or doesn't have any active packages.")
                return redirect(url_for('views.packSearch'))
            data = []
            for row in result:
                data.append(row)
            headers = ['Package ID', 'Status', 'Sender', 'Receiver', 'Price', 'Length', 'Width', 'Height']

            return render_template("QueryOutput.html", heading=headers, data=data, search_type="Customer ID",
                                   query=cid)
        else:
            return "Error."

@views.route('/report')
@login_required
def report():
    return render_template("ReportRequestPage.html")


@views.route('/report', methods=["POST"])
@login_required
def outputReport():
    reportType = request.form.get('reportType')
    startDate = request.form.get('start')
    endDate = request.form.get('end')
    print(reportType)
    print(startDate)
    print(endDate)
    profit = 0
    if startDate > endDate:
        flash("Start date cannot be greater than End date.")
        return redirect(url_for('views.outputReport'))
    with connect(
            host=host,
            user=user,
            password=password,
            database=database
    ) as connection:
        print(connection)
        cursor = connection.cursor(buffered=True)

        if reportType == 'pkg':
            pkgQ = """SELECT ID, status, Sender, Reciever, price, length, width, height, delivered_time
            FROM package
            WHERE status = 'delivered' AND delivered_time < '""" + str(endDate) + "' AND delivered_time > '" + str(startDate) + "';"

            cursor.execute(pkgQ)
            result = cursor.fetchall()
            print(result)
            resultLength = len(result)
            if resultLength == 0:
                flash("No packages were delivered during that time frame")
                return redirect(url_for('views.outputReport'))
            data = []
            for row in result:
                data.append(row)
                profit += row[4]

            print(profit)
            headers=['Package ID', 'Status', 'Sender', 'Receiver', 'Price', 'Length', 'Width', 'Height', 'Delivered Time']

            return render_template("ReportOutput.html", report="Total Deliveries", heading=headers, data=data, date_start=startDate,
                            date_end=endDate, search_type="Customer ID", profit=profit, num_items=resultLength)

        elif reportType == 'customers':
            custQ = "SELECT Cust_ID, Fname, lname, email, phone_no, address, date_joined " \
                    "FROM customer WHERE date_joined < '" + str(endDate) + "' AND date_joined > '" + str(startDate) + "';"

            cursor.execute(custQ)
            result = cursor.fetchall()
            print(result)
            resultLength = len(result)
            if resultLength == 0:
                flash("No customers joined time frame")
                return redirect(url_for('views.outputReport'))
            data = []
            for row in result:
                data.append(row)

            print(profit)
            headers = ['Customer ID', 'First Name', 'Last name', 'Email', 'Phone Number', 'Address', 'Date Joined' ]

            return render_template("ReportOutput.html", report="Total Customers Joined", heading=headers, data=data,
                                   date_start=startDate,
                                   date_end=endDate, search_type="Customer ID", profit=profit, num_items=resultLength)

        elif reportType == 'employee':
            empQ = " SELECT Emp_ID, F_Name, L_Name, Ph_num, email, Employee_type, office_num, date_hired FROM employee " \
                    "WHERE date_hired < '" + str(endDate) + "' AND date_hired > '" + str(startDate) + "'; "

            cursor.execute(empQ)
            result = cursor.fetchall()
            print(result)
            resultLength = len(result)
            if resultLength == 0:
                flash("No employees hired in time frame selected")
                return redirect(url_for('views.outputReport'))
            data = []
            for row in result:
                data.append(row)
                # profit += row[4]

            print(profit)
            headers = ['Employee ID', 'First Name', 'Last name','Phone', 'Email', 'Role', 'Branch', 'Date hired']

            return render_template("ReportOutput.html", report="Total Employees Hired", heading=headers, data=data,
                                   date_start=startDate,
                                   date_end=endDate, search_type="Customer ID", profit=profit, num_items=resultLength)

        else:
            print('Error')
        return render_template("ReportOutput.html")

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