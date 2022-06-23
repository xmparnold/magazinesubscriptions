from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DATABASE
from flask import flash, session

# some constants that can be changed to alter minimum length requirements

MAGAZINE_TITLE_MINIMUM_LENGTH = 2
MAGAZINE_DESCRIPTION_MINIMUM_LENGTH = 10

# string form of ints for error messages

MAGAZINE_TITLE_MINIMUM_LENGTH_STRING = "2"
MAGAZINE_DESCRIPTION_MINIMUM_LENGTH_STRING = "10"

class Magazine:
    def __init__( self, data ):
        self.id = data[ 'id' ]
        self.title = data[ 'title']
        self.description = data[ 'description' ]
        self.created_by = session[ 'user_id' ]

    # static method to validate magazine form fields
    @staticmethod
    def validate_magazine( data ):
        isValid = True

        if data[ 'title' ] == "":
            isValid = False
            flash( "Please enter a title for the magazzine.", "error_magazine_title" )
        
        if len( data[ 'title' ] ) < MAGAZINE_TITLE_MINIMUM_LENGTH:
            isValid = False
            flash( "Title must be at least " + MAGAZINE_TITLE_MINIMUM_LENGTH_STRING + " characters long.", "error_magazine_title" )
        
        if data[ 'description' ] == "":
            isValid = False
            flash( "Please enter a description for the magazine.", "error_magazine_description" )
        
        if len( data[ 'description' ] ) < MAGAZINE_DESCRIPTION_MINIMUM_LENGTH:
            flash( "Description must be at leasat " + MAGAZINE_DESCRIPTION_MINIMUM_LENGTH_STRING + " characters long.", "error_magazine_description" )
        
        return isValid

    
    # get one from db by id
    @classmethod
    def get_one( cls, data ):
        query = "SELECT * FROM magazines WHERE id = %(id)s;"
        result = connectToMySQL( DATABASE ).query_db( query, data )

        if len( result ) > 0:
            return cls( result[ 0 ] )
        else:
            return None

    # get one from db by title
    @classmethod
    def get_one_by_title( cls, data ):
        query = "SELECT * FROM magazines WHERE title = %(title)s;"
        result = connectToMySQL( DATABASE ).query_db( query, data )

        if len( result ) > 0:
            return cls( result[ 0 ] )
        else:
            return None

    # get all from magazzines table, no conditional
    @classmethod
    def get_all( cls ):
        query = "SELECT * FROM magazines;"
        result = connectToMySQL( DATABASE ).query_db( query )
        list_magazines = []

        if len( result ) > 0:
            for magazine in result:
                list_magazines.append( cls( magazine ) )
        
        return list_magazines

    # get all magazines by user id that created it
    @classmethod
    def get_all_by_user_id( cls, data ):
        query = "SELECT * FROM magazines;"
        result = connectToMySQL( DATABASE ).query_db( query, data )
        user_magazines = []

        if len( result ) > 0:
            for magazine in result:
                if magazine[ 'created_by' ] == session[ 'user_id' ]:
                    user_magazines.append( cls( magazine ) )
                else:
                    continue
                
        return user_magazines

    # create new magazine method
    @classmethod
    def create( cls, data ):
        query = "INSERT INTO magazines( title, description, created_by ) VALUES( %(title)s, %(description)s, %(created_by)s );"
        return connectToMySQL( DATABASE ).query_db( query, data )

    # delete magazine method, we will also delete from joining table for subscriptions to avoid errors
    @classmethod
    def delete_one( cls, data ):
        query = "DELETE FROM magazine_subscriptions WHERE magazine_id = %(id)s;"
        connectToMySQL( DATABASE ).query_db( query, data )
        query = "DELETE FROM magazines WHERE id = %(id)s;"
        return connectToMySQL( DATABASE ).query_db( query, data )

    # edit a magazine method, not curently under use
    @classmethod
    def edit_one( cls, data ):
        query = "UPDATE magazines SET title = %(title)s, description = %(description)s, created_by = %(created_by)s WHERE id = %(id)s;"
        return connectToMySQL( DATABASE ).query_db( query, data )

    # subscribe current user to magazine
    @classmethod
    def subscribe( cls, data ):
        query = "INSERT INTO magazine_subscriptions( user_id, magazine_id ) VALUES( %(user_id)s, %(magazine_id)s);"
        return connectToMySQL( DATABASE ).query_db( query, data )
    
    # get all subscribers from specific magazine id
    @classmethod
    def get_subscribers( cls, data ):
        query = "SELECT * FROM magazine_subscriptions WHERE magazine_id = %(magazine_id)s;"
        result = connectToMySQL( DATABASE ).query_db( query, data )
        list_subscriptions = []

        if len( result ) > 0:
            for subscription in result:
                list_subscriptions.append( subscription )
        
        return list_subscriptions