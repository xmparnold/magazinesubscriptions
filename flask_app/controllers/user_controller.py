from flask import session, request, render_template, redirect, flash
from flask_app import app
from flask_app.models.magazine_model import Magazine
from flask_app.models.user_model import User
from flask_bcrypt import Bcrypt

# set bcrypt object that we will use to encrypt passwords and to compare entered passwords to the encrypted one in db
bcrypt = Bcrypt( app )

@app.route( "/" )
def display_login_registration():
    if User.validate_session():
        return redirect( "/dashboard" )
    else:
        return render_template( "index.html" )

@app.route( "/user/new", methods = [ 'POST' ] )
def create_user():

    # Validate form fields actually contain values, if it does, make sure email doesn't already exist in db. if it returns None, then we will create the user in db, otherwise request new email
    if User.validate_register( request.form ) == True:
        data = {
            "email" : request.form[ 'email' ]
        }

        result = User.get_one( data )

        if result == None:
            # add user to db because this means they don't exist already
            # first create dictionary to store values from form, for password we will encrypt using bcrypt first
            data = {
                "email" : request.form[ 'email' ],
                "first_name" : request.form[ 'first_name' ],
                "last_name" : request.form[ 'last_name' ],
                "password" : bcrypt.generate_password_hash( request.form[ 'password' ] )
            }
            # create the user in db and set user_id to the id value returned by the db query from create()
            user_id = User.create( data )
            # set session to current user information
            session[ 'email' ] = request.form[ 'email' ]
            session[ 'first_name' ] = request.form[ 'first_name' ]
            session[ 'last_name' ] = request.form[ 'last_name' ]
            session[ 'user_id' ] = user_id
            # redirect to dashboard, now logged in
            return redirect( "/dashboard" )
        else:
            # flash message requesting new email since it already exists in db
            flash( "Email already exists, please use another.", "error_register_email" )
            return redirect( "/" )
    else:
        # form not fully filled out, redirect to same page with error messages now flashed to the page
        return redirect( "/" )

# route to log user out
@app.route( "/logout" )
def logout():
    # simply clear the session and redirect to login registration page (index.html)
    session.clear()
    return redirect( "/" )

# this route handles user login
@app.route( "/login", methods = [ 'POST' ] )
def login():
    # create dictionary containing email from login form
    data = {
        "email" : request.form[ 'email' ]
    }
    # check if user exists by email and set returned value to result variable 
    result = User.get_one( data )

    # if the user doesn't exist, flash wrong credentials error message and redirect to login page
    if result == None:
        flash( "Wrong credentials", "error_login")
        return redirect( "/" )
    else:
        # if user does exist, we need to check if password matches the encrypted on in db, if it doesn't match, flash same wrong credentials message
        if not bcrypt.check_password_hash( result.password, request.form[ 'password' ] ):
            flash( "Wrong credentials", "error_login" )
            return redirect( "/" )
        else:
            # if it does exist, set current session to query result from get_one() method and redirect to dashbaord, now logged in
            session[ 'email' ] = result.email
            session[ 'first_name' ] = result.first_name
            session[ 'last_name' ] = result.last_name
            session[ 'user_id' ] = result.id
            session[ 'password' ] = result.password
            return redirect( "/dashboard" )

@app.route( "/user/details" )
def display_user_details():
    if User.validate_session():
        data = {
            "user_id" : session[ 'user_id' ]
        }

        user_magazines = Magazine.get_all_by_user_id( data )

        magazine_subscriptions = {}

        for mag in user_magazines:
            data = {
                "magazine_id" : mag.id
            }

            result = Magazine.get_subscribers( data )
            magazine_subscriptions[ mag.id ] = len( result )
        
        return render_template( "userDetails.html", user_magazines = user_magazines, magazine_subscriptions = magazine_subscriptions )
    else:
        flash( "You must login first.", "error_login" )
        return redirect( "/" )

@app.route( "/user/details", methods = [ 'POST' ] )
def edit_user_details():
    data = {
            "email" : request.form[ 'email' ]
        }

    result = User.get_one( data )

    if result == None:
        # this means email is not taken in db, so we can update
        if User.validate_user_details_edit_form( request.form ) == True:
            
            data = {
                "id" : session[ "user_id" ],
                "first_name" : request.form[ 'first_name' ],
                "last_name" : request.form[ 'last_name' ],
                "email" : request.form[ 'email' ],
                "password" : session[ "password" ]
            }
            
            User.edit_details( data )
            session[ 'first_name' ] = request.form[ 'first_name' ]
            session[ 'last_name' ] = request.form[ 'last_name' ]
            session[ 'email' ] = request.form[ 'email' ]

            return redirect( "/user/details" )
        else:
            return redirect( "/user/details" )
    elif result.id == session[ "user_id" ]:
        # this means the email belongs to the current user, so it is okay to update since we won't have multiples of the same email on table
        if User.validate_user_details_edit_form( request.form ) == True:
            
            data = {
                "id" : session[ "user_id" ],
                "first_name" : request.form[ 'first_name' ],
                "last_name" : request.form[ 'last_name' ],
                "email" : request.form[ 'email' ],
                "password" : session[ "password" ]
            }
            
            User.edit_details( data )
            session[ 'first_name' ] = request.form[ 'first_name' ]
            session[ 'last_name' ] = request.form[ 'last_name' ]
            session[ 'email' ] = request.form[ 'email' ]

            return redirect( "/user/details" )
        else:
            return redirect( "/user/details" )
    else:
        flash( "Email already in use, please choose another.", "error_edit_email")