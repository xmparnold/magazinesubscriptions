from flask import session, request, render_template, redirect, flash
from flask_app import app
from flask_app.models.magazine_model import Magazine
from flask_app.models.user_model import User

@app.route( "/dashboard" )
def display_dashboard():
    list_magazines = Magazine.get_all()
    list_users = User.get_all()

    if User.validate_session():
        return render_template( "dashboard.html", list_magazines = list_magazines, list_users = list_users )
    else:
        flash( "You must login first.", "error_login" )
        return redirect( "/" )

@app.route( "/magazine/new" )
def display_new_magazine_form():
    if User.validate_session():
        return render_template( "newMagazineForm.html" )
    else:
        flash( "You must login first.", "error_login" )
        return redirect( "/" )

@app.route( "/magazine/new", methods = [ 'POST' ] )
def create_magazine():
    if Magazine.validate_magazine( request.form ) == True:
        data = {
            "title" : request.form[ 'title' ]
        }

        result = Magazine.get_one_by_title( data )

        if result == None:
            # This means title doesn't already exist in db, create the magazine

            # create a dictionary with values from form and grab current user's id from session
            data = {
                "title" : request.form[ 'title' ],
                "description" : request.form[ 'description' ],
                "created_by" : session[ 'user_id' ]
            }

            # create the magazine in db
            new_magazine = Magazine.create( data )

            return redirect( "/dashboard" )
        else:
            flash( "That title already exists, please pick another.", "error_magazine_title" )
            return redirect( "/magazine/new" )
    else:
        # form not fully filled out correctly, error messages flashed by validate method, redirect to new magazine form
        return redirect( "/magazine/new" )
    
@app.route( "/magazine/<int:id>" )
def display_magazine_details( id ):
    if User.validate_session():
        data = {
            "id" : id
        }

        magazine = Magazine.get_one( data )

        data = {
            "magazine_id" : id
        }

        subscribers = Magazine.get_subscribers( data )
        list_users = User.get_all()
        list_subs = []
        for sub in subscribers:
            for user in list_users:
                if sub['user_id'] == user.id:
                    list_subs.append(user)
        

        return render_template( "magazineDetails.html", magazine = magazine, subscribers = subscribers, list_subs = list_subs )
    else:
        flash( "You must log in first.", "error_login" )
        return redirect( "/" )

@app.route( "/magazine/<int:id>/edit" )
def display_edit_magazine_form( id ):
    if User.validate_session():
        data = {
            "id" : id
        }
        magazine = Magazine.get_one( data )
        return render_template( "editMagazineForm.html", magazine = magazine )
    else:
        flash( "You must log in first.", "error_login" )
        return redirect( "/" )
        
@app.route( "/magazine/<int:id>/edit", methods = [ 'POST' ] )
def edit_magazine( id ):
    if Magazine.validate_magazine( request.form ) == True:
        data = {
            "title" : request.form[ 'title' ]
        }
        
        result = Magazine.get_one_by_title( data )

        if result == None:
            # title doesn't already exist in db so we can create the magazine
            # first create a dictionary with the values from the form and grab current user's id from session
            data = {
                "title" : request.form[ 'title' ],
                "description" : request.form[ 'description' ],
                "created_by" : session[ 'user_id' ]
            }
            
            magazine = Magazine.edit_one( data )
            return redirect( "/dashboard" )

@app.route( "/magazine/<int:id>/delete" )
def delete_magazine( id ):
    data = {
        "id" : id
    }

    Magazine.delete_one( data )
    return redirect( "/dashboard" )

@app.route( "/magazine/<int:id>/subscribe" )
def subscribe_to_magazine( id ):
    data = {
        "user_id" : session[ 'user_id' ],
        "magazine_id" : id
    }

    Magazine.subscribe( data )
    return redirect( "/dashboard" )