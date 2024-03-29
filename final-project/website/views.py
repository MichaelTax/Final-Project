from flask import Flask, Blueprint, render_template, jsonify, request, flash, session, redirect, url_for
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from bson import ObjectId
import pymongo
import os

# db_uri = "mongodb+srv://root:123123123@my-release-mongodb-sharded.default.svc.cluster.local:27017"
db_uri = os.getenv ('MONGODB_URI', "mongodb://root:HB46qiOROO@my-mongodb:27017/")
# Create a new client and connect to the server
mongo_client = MongoClient(db_uri)    

mydb = mongo_client["Login_Info"]
mycollection = mydb["Login_Info"]
notes_collection = mydb["Notes"]



views = Blueprint('views', __name__)    

@views.route('/')
def home():
    userid = request.cookies.get("userid")
    logged_in = False  # Default to False
    if userid:
        result = mycollection.find_one({"_id": ObjectId(userid)})
        if result:
            flash('Logged in! ' + result['firstName'], category='success')
            logged_in = True  # User is logged in
        else:
            flash('Unknown login!', category='error')
            logged_in = bool(userid)

    return render_template("home.html", logged_in=logged_in)

@views.route('/my_notes')
def my_notes():
    userid = request.cookies.get("userid")
    if not userid:
        flash('Please log in to view your notes.', category='error')
        return redirect(url_for('views.home')) # Redirect to home page if not logged in

# Retrieve the email associated with the current user
    user_email = mycollection.find_one({"_id": ObjectId(userid)})["email"]
    if not user_email:
        flash('User email not found.', category='error')
        return redirect(url_for('views.home'))  # Redirect to home page if email not found
    
     # Retrieve all notes associated with the user's email from the "Notes" collection
    user_notes = notes_collection.find({"user_id": user_email})

    return render_template("my_notes.html", user_notes=user_notes)

@views.route('/add-note', methods=['GET', 'POST'])
def add_note():
    userid = request.cookies.get("userid")
    if not userid:
        flash('Please log in to add a note.', category='error')
        return redirect(url_for('views.home'))  # Redirect to home page if not logged in

    if request.method == 'POST':
                                       # Handle note addition
        user_email = mycollection.find_one({"_id": ObjectId(userid)})["email"]
        note_content = request.form.get('note_content')

        if not note_content:
            flash('Note content cannot be empty.', category='error')
            return redirect(url_for('views.home'))  # Redirect to home page if note content is empty

        notes_collection.insert_one({"user_id": user_email, "content": note_content})
        flash('Note added successfully!', category='success')
        return redirect(url_for('views.my_notes'))  # Redirect to my_notes page after adding note

    return render_template('add-note.html')

@views.route('/delete-note', methods=['POST'])
def delete_note():
    userid = request.cookies.get("userid")
    if not userid:
        flash('Please log in to delete a note.', category='error')
        return redirect(url_for('views.home')) # Redirect to home page if not logged in
    
    if request.method == "POST":
        note_id = request.form.get('note_id') # Get the ID of the note to delete
        
        # Check if the note belongs to the logged-in user
        user_email = mycollection.find_one({"_id": ObjectId(userid)})["email"]
        note = notes_collection.find_one({"_id": ObjectId(note_id), "user_id": user_email})
        
        if note:
            notes_collection.delete_one({"_id": ObjectId(note_id)})
            flash('Note deleted successfully.', category='success')
        else:
            flash('Note not found or you do not have permission to delete it.', category='error')
        
        return redirect(url_for('views.my_notes'))