from flask import Flask, render_template,redirect,flash,request
from mysqlconnection import MySQLConnector
app=Flask(__name__)
app.secret_key='123'
mysql=MySQLConnector(app,'Wall')
@app.route('/')
def index():
    print "Hello"
    return render_template('index.html')
@app.route('/')
@app.route('/createuser', methods=['POST'])
def create():
    print request.form
    f_name=request.form['first_name']
    l_name=request.form['last_name']
    r_email=request.form['email']
    r_password=request.form['password']
    c_password=request.form['c_password']
    query='INSERT INTO users (first_name,last_name,email,password,created_at,updated_at)VALUES (:first_name,:last_name,:email,:password,now(),now())'
    data={
        'first_name':f_name,
        'last_name':l_name,
        'email':r_email,
        'password':r_password,
    }
    mysql.query_db(query, data)
    return redirect('/')
@app.route('/login', methods=['POST'])
def login():
    print "logged_in"
    return redirect('/')
@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')

app.run(debug=True)
