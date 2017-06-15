from flask import Flask, render_template,redirect,flash,request,session
from mysqlconnection import MySQLConnector
import os, binascii,re,md5
app=Flask(__name__)
app.secret_key='123'
mysql=MySQLConnector(app,'Wall')
@app.route('/')
def index():
    session['status']='loggedoff'
    print "Hello"
    return render_template('index.html')

@app.route('/createuser', methods=['POST'])
def create():
    f_name=request.form['first_name']
    l_name=request.form['last_name']
    r_email=request.form['email']
    r_password=request.form['password']
    c_password=request.form['confirm-password']
    salt =  binascii.b2a_hex(os.urandom(15))
    hashed_pw = md5.new(r_password + salt).hexdigest()
    error_count=0
    empty_field_error="The {} field can't be empty"
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    name_regex=re.compile('\d+')
    def empty_input(arg):
        return len(arg)<1
    keys=['email','first_name','last_name','password','confirm-password']
    #check if field is empty
    for k in keys:
        if empty_input(k):
            error_count+=1
            flash(empty_field_error.format(k))
    #email check
    if not EMAIL_REGEX.match(r_email):
        error_count+=1
        flash('Please correct the error in the email field before you submit','email')
    #check for password length
    if len(r_password) < 8:
        error_count+=1
        flash('A password has to be at least 8 characters in length', 'password')
    #check if password==confirm_password
    if r_password!=c_password:
        error_count+=1
        flash('Password and password confirmation should match', 'password')
    #check if first_name or last_name contain numbers
    for n in [f_name,l_name]:
        if name_regex.search(n):
            error_count+=1
            flash("Names can't have numbers in them",n)
    print error_count
    if error_count==0:
        flash("You have signed up succesfully",'green')
        query='INSERT INTO users (first_name,last_name,email,password,created_at,updated_at,salt)VALUES (:first_name,:last_name,:email,:password,now(),now(),:salt)'
        data={
            'first_name':f_name,
            'last_name':l_name,
            'email':r_email,
            'password':hashed_pw,
            'salt': salt
        }
        mysql.query_db(query, data)
        return redirect('/show')
    else:
        return redirect('/sign_up')
@app.route('/show')
def show():
    if session['status']=="loggedin":
        query='SELECT u.first_name AS first_name,u.last_name AS last_name,m.created_at AS created_at, m.message AS message, m.user_id AS user_id, m.id AS m_id,c.message_id FROM users u LEFT JOIN messages m ON u.id=m.user_id LEFT JOIN comments c ON m.id=c.message_id GROUP BY m.message'

        query2='SELECT c.message_id, c.comment, u.first_name, u.last_name, c.created_at, m.user_id AS user_id, m.id AS m_id FROM users u LEFT JOIN messages m ON u.id=m.user_id LEFT JOIN comments c ON m.id=c.message_id'

        session['query']=mysql.query_db(query)
        session['query2']=mysql.query_db(query2)
        print len(session['query'])
        print "ids",session['query'][0]['message_id'],session['query'][0]['m_id']
        return render_template('show.html')
    else:
        return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    r_email=request.form['email']
    r_password=request.form['password']
    query='SELECT u.first_name AS first_name,u.password, m.message AS message, c.comment AS comment, m.user_id AS user_id, m.id AS message_id, c.message_id,u.salt FROM users u LEFT JOIN messages m ON u.id=m.user_id LEFT JOIN comments c ON m.id=c.message_id WHERE u.email=:email'
    data={
        'email': r_email,
    }
    session['query']=mysql.query_db(query,data)
    print session['query']
    if len(session['query'])<1:
        flash("Invalid email", 'red')
        return redirect('/')
    else:
        hashed_pw = md5.new(r_password + session['query'][0]['salt']).hexdigest()
        if hashed_pw==session['query'][0]['password']:
            session['user_id']=session['query'][0]['user_id']
            print session['user_id']
            session['status']="loggedin"
            return redirect('/show')
    # except:
    #     return redirect('/')
@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')


@app.route('/creatcomment', methods=['POST'])
def create_comment():
    if session['status']=="loggedin":
        print "comment-", request.form
        query='INSERT INTO comments(comment,user_id,message_id, created_at,updated_at) VALUES (:comment,:user_id,:message_id,now(),now())'
        data={
            'comment': request.form['comment'],
            'message_id': request.form['message_id'],
            'user_id': session['user_id']
        }
        mysql.query_db(query,data)
    return redirect('/show')

@app.route('/createmessage', methods=['POST'])
def create_message():
    query='INSERT INTO messages(message,user_id,created_at,updated_at) VALUES (:message,:user_id,now(),now())'
    data={
        'message':request.form['message'],
        'user_id':session['user_id']
    }
    mysql.query_db(query,data)
    return redirect('/show')
@app.route('/logout')
def log_out():
    print "logged out"
    s_keys=session.keys()
    for k in s_keys:
        session.pop(k)
    session['status']="loggedoff"
    return redirect('/')

app.run(debug=True)
