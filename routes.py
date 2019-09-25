import sys
sys.path.append('source')

from flask import render_template, request, redirect, url_for, abort, Flask, session
from server import app, system
from system import *
from sql import *

'''
Setup email server
'''
# Enter your email server details below
app.config['MAIL_SERVER']= 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your password'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# Intialize Mail
# mail = Mail(app)
# Enable account activation?
account_activation_required = False

@app.route('/get_item/<category>/<item_id>', methods=['GET'])
def get_item(category, item_id):
    res = {
        "response" : system.get_entry_by_id(category, item_id)
    }

    return res


@app.route('/get_history/<item_id>', methods=['GET'])
def get_history(item_id):
    res = {
        "response" : system.get_user_changes(item_id)
    }

    return res

'''
Dedicated page for "page not found"
'''
@app.route('/404')
@app.errorhandler(404)
def page_not_found(e=None):
    return render_template('404.html', errorStr = e), 404

'''
Home / Welcome page
'''
@app.route('/<category>/<item_type>', methods=['GET', 'POST'])
def home(category, item_type):
    dataList = system.sort_by_columns('Bolts', ['type'])
    columnNames = system.get_column_names('Bolts')
    unique_types = system.get_unique_column_items('Bolts','type')

    return render_template('index.html', unique_types=unique_types, dataList=dataList, columnNames=columnNames)

'''
login screen
'''
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Get the hashed password
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest();
        # Check if account exists using MySQL
        account = system.check_credentials(username, password)

    # If account exists in accounts table in out database
        if len(account) > 0:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account(0)
            session['username'] = account(3)
            
            if 'rememberme' in request.form:
                # Create hash to store as cookie
                hash = account['username'] + request.form['password'] + app.secret_key
                hash = hashlib.sha1(hash.encode())
                hash = hash.hexdigest();
                # the cookie expires in 90 days
                expire_date = datetime.datetime.now() + datetime.timedelta(days=90)
                resp = make_response('Success', 200)
                resp.set_cookie('rememberme', hash, expires=expire_date)
                # Update remember-me in accounts table to the cookie hash
                system.makeQuery(f"UPDATE `users` SET `rememberme` = '{hash}' WHERE `user_id` = '{account(0)}'")
                return resp
            # Redirect to home page
            return 'Logged in successfully!'
        else:
            # Account doesnt exist or username/password incorrect
            return 'Incorrect username/password!'
    return render_template('index.html', msg=msg)

'''
Register
'''
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Hash the password
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest();
        # Check if account exists using MySQL
        account = system.checkExistance(username)
        # If account exists show error and validation checks
        if account:
            return 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            return 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            return 'Please fill out the form!'
        elif account_activation_required:
            # Account activation enabled
            # Generate a random unique id for activation code
            activation_code = uuid.uuid4()
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, "")', (username, password, email, activation_code))
            mysql.connection.commit()
            # Change your_email@gmail.com
            email = Message('Account Activation Required', sender = 'your_email@gmail.com', recipients = [email])
            # change yourdomain.com to your website, to test locally you can go to: http://localhost:5000/pythonlogin/activate/<email>/<code>
            activate_link = 'http://yourdomain.com/pythonlogin/activate/' + str(email) + '/' + str(activation_code)
            # change the email body below
            email.body = '<p>Please click the following link to activate your account: <a href="' + str(activate_link) + '">' + str(activate_link) + '</a></p>'
            mail.send(email)
            return 'Please check your email to activate your account!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, "", "")', (username, password, email))
            mysql.connection.commit()
            return 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        return 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


'''
Logout
'''
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))