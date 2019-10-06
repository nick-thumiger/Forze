import sys
sys.path.append('source')

from flask import render_template, request, redirect, url_for, abort, Flask, session, make_response, Response
from source.system import *
from source.sql import *
import re
import uuid
import hashlib
from datetime import datetime, timedelta
from source.exceptions import *
from init import bootstrap_system
import json

autoLog = False

'''
Setup email server
'''
# Enter your email server details below
# app.config['MAIL_SERVER']= 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USERNAME'] = 'forze.inventory@gmail.com'
# app.config['MAIL_PASSWORD'] = 'qhkeyhdclbqncpkn'
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True
# Intialize Mail
# mail = Mail(app)
# Enable account activation?
account_activation_required = False


app = Flask(__name__)
app.secret_key = 'very-secret-123'  # Used to add entropy
system = bootstrap_system()

@app.route('/search/<category>', methods=['GET'])
def search(category):
    dataList = system.search(category, request.args)

    columnNames = system.get_pretty_column_names(category)

    return render_template('search.html', dataList=dataList, columnNames=columnNames)
    
@app.route('/add_type', methods=['POST'])
def add_type():
    req_data = request.get_json()

    category = req_data['category']
    item_type = req_data['type']

    try:
        system.add_type(category, item_type)
    except Exception as e:
        print(str(e))
        return Response("Failure", status=400, mimetype='application/text')

    return Response("Success", status=200, mimetype='application/text')


@app.route('/authenticate', methods=['POST'])
def authenticate():
    req_data = request.get_json()

    username = req_data['username']
    password = req_data['password']

    res = system.check_auth(username, password, app.secret_key)

    if res == None:
        return Response("Invalid username/password", status=400)

    userToken = res[0]
    userID = res[1]

    body = {
        'token':userToken,
        'id':userID
    }

    return Response(json.dumps(body), status=200, mimetype='application/json')

@app.route('/delete_item', methods=['POST'])
def delete_item():
    req_data = request.get_json()

    table = req_data['table']
    item_id = req_data['item_id']

    system.delete_entry(table, item_id)

    return 'Success'

@app.route('/add_item', methods=['POST'])
def add_item():
    req_data = request.get_json()

    columns = req_data['columns']
    values = req_data['values']
    table = req_data['table']

    if len(columns) != len(values):
        raise Exception('unequal line lengths')

    try:
        system.add_entry(table, columns,values)
    except Exception as err:
        return ("Fail", "400 Error")

    return 'Success'

@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    req_data = request.get_json()

    try:
        table = req_data['table']
        item_id = req_data['item_id']
        diff_quantity = int(req_data['quantity'])
        user_id = req_data['user_id']

        temp = system.get_entry_by_category_id(table, item_id)
        total_weight = float(temp[-1])
        pp_weight = float(temp[-2])
        curr_quantity = int(total_weight/pp_weight)

        new_quantity = int(curr_quantity+diff_quantity)
        new_weight = float(new_quantity*pp_weight)

        if user_id != None:
            system.set_value(table,item_id,['weight_per_piece','weight_total'],[pp_weight, new_weight],user_id)
        elif 'id' in session.keys():
            system.set_value(table,item_id,['weight_per_piece','weight_total'],[pp_weight, new_weight],session['id'])
        else:
            system.set_value(table,item_id,['weight_per_piece','weight_total'],[pp_weight, new_weight])

        return 'Success'

    except Exception as err:
        print(str(err))
        return ("Fail", "400 Error")

@app.route('/edit_item', methods=['POST'])
def edit_item():
    req_data = request.get_json()

    try:
        columns = req_data['columns']
        values = req_data['values']
        table = req_data['table']
        item_id = req_data['item_id']

        print(values)
        print(columns)

        if len(columns) != len(values):
            raise Exception('unequal line lengths')

        if 'id' in session.keys():
            system.set_value(table,item_id,columns,values,session['id'])
        else:
            system.set_value(table,item_id,columns,values)

        return 'Success'
    except Exception as err:
        print(str(err))
        # res =
        return Response(str(err), status=400, mimetype='application/text')

'''
Get the user history for a particular entry
'''
@app.route('/condF', methods=['POST'])
def cond_formatting():
    req_data = request.get_json()

    try:
        types = req_data['type']
        hvals = req_data['hvals']
        lvals = req_data['lvals']

        print(types)
        print(hvals)
        print(lvals)

        if (len(types) != len(hvals)) or (len(types) != len(lvals)):
            raise Exception('unequal line lengths')

        print("1233")
        system.edit_type_table(types, lvals, hvals)

        return 'Success'
    except Exception as err:
        print(str(err))
        # res =
        return Response(str(err), status=400, mimetype='application/text')

@app.route('/get_item_ID', methods=['GET'])
def get_item_ID():
    itemID = request.args.get('itemID')

    if itemID == None:
        return Response("itemID not passed in", status=400, mimetype='application/text')

    res = {
        "response" : system.get_entry_by_id(itemID)
    }

    return Response(json.dumps(res), status=200, mimetype='application/json')

@app.route('/get_item/<category>/<itemID>', methods=['GET'])
def get_item(category, itemID):
    # itemID = request.args.get('itemID')
    # return itemID

    res = {
        "response" : system.get_entry_by_category_id(category, itemID)
    }

    return json.dumps(res)

@app.route('/get_columns/<category>', methods=['GET'])
def get_columns(category):
    res = {
        "response" : system.get_pretty_column_names(category)
    }

    return json.dumps(res)

'''
Get the user history for a particular entry
'''
@app.route('/get_history/<item_id>', methods=['GET'])
def get_history(item_id):
    res = {
        "response" : system.get_user_changes(item_id)
    }

    return Response(json.dumps(res), status=200, mimetype='application/json')

'''
Dedicated page for "page not found"
'''
@app.route('/404')
@app.errorhandler(404)
def page_not_found(e=None):
    type_data = None
    if 'username' in session.keys():
        user=session['username']
    else:
        user = None

    try:
        try:
            type_data = system.get_type_table()
        except:
            type_data = None
            raise systemException("SQL error upon retrieving conditional formatting shit")
        category_list = system.get_category_list()

        return render_template('index.html', category=None, category_list=category_list, item_type=None, unique_types=None, dataList=None, columnNames=None, username=user, msg="ERROR 404: Page not found", type_data=type_data)

    except CustomException as err:
        return render_template('index.html', category=None, category_list=None, item_type=None, unique_types=None, dataList=None, username=user, columnNames=None, msg="ERROR 404: Page not found", type_data=type_data)
    except Exception as err:
        syserr = builtInException(err)
        return render_template('index.html', category=None, category_list=None, item_type=None, unique_types=None, dataList=None, username=user, columnNames=None, msg="ERROR 404: Page not found", type_data=type_data)
    return redirect(url_for('login'))

'''
Dedicated page for mobile
'''
@app.route('/mobile.html')
def mob():
    return render_template('mobile.html')

'''
Home Page
'''
@app.route('/', methods=['GET'])
def home():
    type_data = None
    if 'username' in session.keys():
        user=session['username']
    else:
        user = None

    if loggedin() or autoLog:
        try:
            try:
                type_data = system.get_type_table()
            except:
                type_data = None
                raise systemException("SQL error upon retrieving conditional formatting shit")
            category_list = system.get_category_list()

            return render_template('index.html', category=None, category_list=category_list, item_type=None, unique_types=None, dataList=None, columnNames=None, username=user, msg="", type_data=type_data)

        except CustomException as err:
            return render_template('index.html', category=None, category_list=None, item_type=None, unique_types=None, dataList=None, username=user, columnNames=None, msg=err.log(), type_data=type_data)
        except Exception as err:
            syserr = builtInException(err)
            return render_template('index.html', category=None, category_list=None, item_type=None, unique_types=None, dataList=None, username=user, columnNames=None, msg=syserr.log(), type_data=type_data)
    return redirect(url_for('login'))

'''
View Table
'''
@app.route('/<category>/<item_type>', methods=['GET'])
def view_table(category, item_type):
    if 'username' in session.keys():
        user=session['username']
    else:
        user = None
    type_data = None
    if loggedin() or autoLog:
        try:
            try:
                category_list = system.get_category_list()
            except:
                category_list = None
                raise systemException("SQL error upon generating list of categories")

            try:
                type_data = system.get_type_table()
            except:
                type_data = None
                raise systemException("SQL error upon retrieving conditional formatting shit")

            try:
                dataList = system.get_category_table(category, item_type, ['type'])
            except Exception as err:
                raise mixedException("Invalid SQL category routes query", "The category requested is invalid. Please try again. Contact support if the issue persists.")

            # dataList = system.sort_by_columns(category)
            columnNames = system.get_pretty_column_names(category)
            unique_types = system.get_types_in_cat(category)
            columnNames.append('Quantity')

            if item_type == "*":
                dataList = None
                columnNames = None
                condForm = None
            elif (len(dataList) == 0):
                raise mixedException("Invalid SQL item_type routes query", "The item type requested is invalid. Please try again. Contact support if the issue persists.")
            else:
                print(item_type)
                condForm = system.get_conditional_formatting(item_type)
                print(condForm)
                for item in dataList:
                    temp = float(item['data'][-2])
                    if temp == 0:
                        quantity = 0
                    else:
                        quantity = round(float(item['data'][-1])/float(item['data'][-2]))
                    item['data'].append(quantity)



            if columnNames != None:
                addModalColumnNames = columnNames.copy()
                addModalColumnNames.remove('Quantity')
                addModalColumnNames.remove('Type')
            else:
                addModalColumnNames = None


            print("Columns")
            print(addModalColumnNames)
            print(f"Category {category}")

            return render_template('index.html', addModalColumnNames=addModalColumnNames, category=category, item_type=item_type, category_list=category_list, unique_types=unique_types, dataList=dataList, columnNames=columnNames, username=user, msg="", condForm=condForm, type_data=type_data)

        except CustomException as err:
            return render_template('index.html', addModalColumnNames=None, item_type=item_type, category=None, category_list=category_list, unique_types=None, dataList=None, username=user, columnNames=None, msg=err.log(), type_data=type_data )
        except Exception as err:
            syserr = builtInException(err)
            return render_template('index.html', addModalColumnNames=None, item_type=item_type, category=None, category_list=category_list, unique_types=None, dataList=None, username=user, columnNames=None, msg=syserr.log(), type_data=type_data)
    return redirect(url_for('login'))

'''
login screen
'''
@app.route('/login/', methods=['GET', 'POST'])
def login():
    try:
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
            password = hash.hexdigest()
            # Check if account exists using MySQL
            account = system.check_credentials(username, password)

        # If account exists in accounts table in out database
            if account != None:
                #check if account is activated
                print(account[7])

                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[3]

                # Create hash to store as cookie
                hash = account[3] + request.form['password'] + app.secret_key
                hash = hashlib.sha1(hash.encode())
                hash = hash.hexdigest()
                # the cookie expires in 90 days
                expire_date = datetime.now() + timedelta(days=90)
                resp = make_response('Success', 200)
                resp.set_cookie('rememberme', hash, expires=expire_date)
                # Update remember-me in accounts table to the cookie hash
                query = f"UPDATE `users` SET `rememberme` = '{hash}' WHERE `user_id` = '{account[0]}'"
                makeCommit(system, query)

                return resp
            else:
                # Account doesnt exist or username/password incorrect
                return 'Incorrect username/password!'
    except CustomException as err:
        return err.log()
    except Exception as err:
        return builtInException(err).log()

    return render_template('login.html', msg=msg)

'''
Register
'''
@app.route('/login/register', methods=['GET', 'POST'])
def register():
    try:
        # Output message if something goes wrong...
        msg = ''
        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            # Create variables for easy access
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            fname = request.form['fname']
            lname = request.form['lname']
            # Hash the password
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest();
            # Check if account exists using MySQL
            print("hello1")
            account = system.checkExistance(username)
            print("hello2")
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
                makeCommit(system, f"INSERT INTO `users` VALUES (NULL, '{fname}', '{lname}', '{username}', '{email}', '{password}', '', '{activation_code}')")
                address = email
                email = Message('Account Activation Required', sender = 'forze.inventory@gmail.com', recipients = [email])
                # change yourdomain.com to your website, to test locally you can go to: http://localhost:5000/pythonlogin/activate/<email>/<code>
                activate_link = 'http://yourdomain.com/pythonlogin/activate/' + str(address) + '/' + str(activation_code)
                # change the email body below
                email.body = 'Welcome to the forze inventory management system! Please click the following link to activate your account: ' + str(activate_link)
                mail.send(email)
                return 'Please check your email to activate your account!'
            else:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                makeCommit(system, f"INSERT INTO `users` VALUES (NULL, '{fname}', '{lname}', '{username}', '{email}', '{password}', '', '')")
                print("hello3")
                return 'You have successfully registered!'
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            return 'Please fill out the form!'
        return render_template('register.html', msg=msg)
    except CustomException as err:
        return err.log()
    except Exception as err:
        return builtInException(err).log()


# http://localhost:5000/pythinlogin/activate/<email>/<code> - this page will activate a users account if the correct activation code and email are provided
@app.route('/login/activate/<string:email>/<string:code>', methods=['GET'])
def activate(email, code):
    # Check if the email and code provided exist in the accounts table
    account = makeQuery(system, f"SELECT * FROM `users` WHERE `email` = '{email}' AND `activation_code` = '{code}'")
    if len(account) > 0:
        # account exists, update the activation code to "activated"
        makeCommit(system, f"UPDATE `users` SET `activation_code` = 'activated' WHERE `email` = '{email}' AND `activation_code` = '{code}'")
        # print message, or you could redirect to the login page...
        return redirect(url_for('login'))
    return 'Account doesn\'t exist with that email or incorrect activation code!'

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
#@app.route('/pythonlogin/home')
#def home():
#    # Check if user is loggedin
#    if loggedin():
#        # User is loggedin show them the home page
#        return render_template('home.html', username=session['username'])
#    # User is not loggedin redirect to login page
#    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if loggedin():
        # We need all the account info for the user so we can display it on the profile page
        account = makeQuery(system, f"SELECT * FROM `users` WHERE `user_id` = '{session['id']}'")
        #account = [listAsciiSeperator(x) for x in rawresult]
        #print(account)
        if len(account) == 0:
            err = systemException("ERROR: No user matches user_id in the 'profile' page.").log()
        else:
            err = ""
        # Show the profile page with account info
        return render_template('profile.html', account=account, err=err)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

'''
Edit Profile
'''
@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    # Check if user is loggedin
    if loggedin():
        # We need all the account info for the user so we can display it on the profile page`
        # Output message
        msg = ''
        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
            # Create variables for easy access
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            if email == "" or username == "" or password == "":
                msg = "Please enter all fields, including the new password (it can be the same as the old password)"
            else:
                # Hash the password
                hash = password + app.secret_key
                hash = hashlib.sha1(hash.encode())
                password = hash.hexdigest()
                # update account with the new details
                makeCommit(system, f"UPDATE `users` SET `username` = '{username}', `pw_hash` = '{password}', `email` = '{email}' WHERE `user_id` = '{session['id']}'")
                msg = 'Updated!'
        account = makeQuery(system, f"SELECT * FROM `users` WHERE `user_id` = '{session['id']}'")
        # Show the profile page with account info
        return render_template('profile-edit.html', account=account, msg=msg)
    return redirect(url_for('login'))

'''
Logout
'''
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Remove cookie data "remember me"
   resp = make_response(redirect(url_for('login')))
   resp.set_cookie('rememberme', expires=0)
   # Redirect to login page
   return redirect(url_for('login'))

'''
Loggedin
'''
# Check if logged in function, update session if cookie for "remember me" exists
def loggedin():
    if 'loggedin' in session:
        return True
    elif 'rememberme' in request.cookies:
        # check if remembered, cookie has to match the "rememberme" field
        rawresult = makeQuery(system, f"SELECT * FROM `users` WHERE `rememberme` = '{request.cookies['rememberme']}'")
        account = [asciiSeperator(x) for x in rawresult]
        print(account)
        if len(account) > 0:
            # update session variables
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[3]
            return True
    # account not logged in return false
    return False


@app.route('/discon')
def testing():
   sqlDisconnect(system.cursor, system.connection)
   return redirect(url_for('login'))

@app.route('/con')
def testing2():
   system._connection = sqlConnect()
   system._cursor = sqlCursor(system.connection)
   return redirect(url_for('login'))