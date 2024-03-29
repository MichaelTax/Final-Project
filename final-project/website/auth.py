from flask import Blueprint, render_template, request, flash, make_response, redirect
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
import os

auth = Blueprint('auth', __name__)

# db_uri = "mongodb+srv://root:123123123@my-release-mongodb-sharded.default.svc.cluster.local:27017"
# db_uri = os.getenv ('MONGODB_URI', "mongodb://root:HB46qiOROO@my-mongodb:27017/")
db_uri = "mongodb://root:HB46qiOROO@my-mongodb:27017/"
# Create a new client and connect to the server
mongo_client = MongoClient(db_uri)    

mydb = mongo_client["Login_Info"]
mycollection = mydb["Login_Info"]

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        result = mycollection.find_one({"email": email, "password": password})
        if not result:
            flash("Incorrect login infore", category="error")
            return render_template("login.html")
        else:
            flash('Logged in!', category='success')
            resp = make_response(render_template("home.html"))
            resp.set_cookie('userid', str(result['_id']))
            return resp 
        
    data = request.form
    print(data)
    return render_template("login.html")

@auth.route('/logout')
def logout():
    userid = request.cookies.get("userid")
    if not userid:
        flash('No user is connected!', category='error')
        return redirect('/')
    
    # Delete the session cookie
    response = make_response(redirect('/'))
    response.set_cookie('userid', '', expires=0)
    flash('Logged out successfully!', category='success')
    return response


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
            return render_template("sign_up.html")
        elif len(first_name) < 2 :
            flash('First name must be greater than 2 characters.', category='error')
            return render_template("sign_up.html")
        elif password1 != password2:
            flash('Passwords dont match.', category='error')
            return render_template("sign_up.html")
        elif len(password1) <7:
            flash('Passwords must be atleast 7 characters long.', category='error')  
            return render_template("sign_up.html")
        else:
            mydict = {"email": email,"firstName":first_name, "password":password1}
            # raise RuntimeError('Another specific error message')
            add_to_db = mycollection.insert_one(mydict)
            if add_to_db.inserted_id:
                flash('Account created!', category='success')
                resp = make_response(render_template("sign_up.html"))
                resp.set_cookie('userid', str(add_to_db.inserted_id))
                return resp 
            else:
                flash('Error creating.', category='error')

            # added user to the database
            
    return render_template("sign_up.html")

#create image of the app 
#mongo-mongodb.mongo.svc.cluster.local
#chart that will lnow to create a depl and serive on top of the image