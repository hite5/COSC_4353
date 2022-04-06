from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from mysql.connector import connect, Error
import re

auth = Blueprint('auth', __name__)

host = "localhost"
user = "root"
password = "C0ug@rs!"
database = "group_5_db"


@auth.route('/login')
def login():
    return render_template("Login.html")


@auth.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('name', None)
    return render_template("HomePage.html")


@auth.route('/login', methods=['POST'])
def login_post():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form.get('username')
        userpass = request.form.get('password')
        try:
            with connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database
            ) as connection:
                cursor = connection.cursor(buffered=True)
                query = f"SELECT * FROM users WHERE email = '{username}'"
                cursor.execute(query)
                account = cursor.fetchone()
                if account:
                    authenticate = check_password_hash(account[9], userpass)
                    if authenticate:
                        session['loggedin'] = True
                        session['id'] = account[0]
                        session['username'] = account[3]
                        session['name'] = account[1] + " " + account[2]
                        return redirect(url_for('views.home'))
                flash('Incorrect username or password !')
                return render_template('Login.html')

        except Error as e:
            print(e)