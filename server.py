import os
from flask import Flask, jsonify, request, url_for, make_response
from flask_api import status
import sys
from werkzeug.exceptions import NotFound
from create_wishlist import CustomerList, DataValidationError, Customer

# Create Flask application
app = Flask(__name__)

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

######################################################
########                DELETE                ########
######################################################
@app.route('/wishlist/<int:wishlist_id>', methods=['DELETE'])
def delete_wishlist(wishlist_id):
    """ Deletes the wishlist with the provided id""" 
    # TODO undo these fixtures once persistance is added
    if wishlist_id == 3:
        return make_response('Wishlist {} deleted'.format(wishlist_id))
    elif wishlist_id == 2:
        return make_response('Wishlist does not exist', status.HTTP_404_NOT_FOUND)
    else:
        return make_response('Wishlist does not exist', status.HTTP_403_FORBIDDEN)


######################################################
########              POST/CREATE             ########
######################################################    
@app.route('/wishlist/<int:cust_id>', methods=['POST'])
def create_wishlist(cust_id):
    """ create the wishlist with the provided id""" 
    wishlist = CustomerList(cust_id)
    wishlist.deserialize(request.get_json())
    wishlist.save()
    message = wishlist.serialize()
    location_url = url_for('create_wishlist',cust_id = wishlist.id)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             'Location': location_url
                         })

######################################################
########                GET/SEE               ########
######################################################
@app.route('/wishlist/<int:cust_id>' , methods=['GET'])
def display_cust_wishlist(cust_id):
    """ List the wishlists with the provided id"""
    dic = CustomerList.find(cust_id)
    return make_response(jsonify(dic), status.HTTP_200_OK)

######################################################
########               PUT/UPDATE             ########
######################################################
@app.route('/wishlist/<int:wishlist_id>', methods=['PUT','PATCH'])
def update_wishlist(wishlist_id):
    """ Updates the wishlist if it exists, otherwise returns not found """
    # TODO add products changes as well, for now just asses the wishlists 
    wishlists = CustomerList.find(wishlist_id)
    if wishlists:
        wishlists.deserialize(request.get_json())
        wishlists.save()
        message = wishlists.serialize()
        return_code = HTTP_200_OK
    	return make_response(jsonify(message) ,status.HTTP_200_OK) 
    else:
    
        message = {'Error' : 'Wishlist not found'}
        #return_code = HTTP_404_NOT_FOUND
    	return make_response(jsonify(message),status.HTTP_404_NOT_FOUND)

######################################################
########                GET/SEE               ########
######################################################
@app.route('/wishlist/<int:cust_id>/<string:wishlist_name>' , methods=['GET'])
def query_wishlist(cust_id,wishlist_name):
	""" List the wishlist with the provided name"""
	wishlists = CustomerList.find(cust_id)
	if wishlists: 
		message = CustomerList.find_wishlist(wishlists,wishlist_name)
		if message:
			return make_response(jsonify(message),status.HTTP_200_OK)
		else:
			message = {'Error' : 'Wishlist with the given name not found'}
			return make_response(jsonify(message),status.HTTP_404_NOT_FOUND)
	else:
		message = {'Error' : 'Customer ID not found'}
		return make_response(jsonify(message),status.HTTP_404_NOT_FOUND)


if __name__ == "__main__":
    print "Wishlist Service Starting..."
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
