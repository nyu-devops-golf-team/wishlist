import os
from flask import Flask, jsonify, request, url_for, make_response
from flask_api import status
import sys
from werkzeug.exceptions import NotFound
from model import CustomerList, DataValidationError, Customer

# Create Flask application
app = Flask(__name__)

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')


######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)


@app.errorhandler(400)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=400, error='Bad Request', message=message), 400


######################################################
########                DELETE                ########
######################################################
@app.route('/wishlist/<int:cust_id>/<int:wishlist_id>', methods=['DELETE'])
def delete_wishlist(cust_id, wishlist_id):
    """ Deletes the wishlist with the provided id"""
    success = CustomerList.delete_by_id(cust_id, wishlist_id)
    if success:
        return make_response('Wishlist {} deleted'.format(wishlist_id))
    else:
        return make_response('Wishlist does not exist', status.HTTP_404_NOT_FOUND)

######################################################
########              POST/CREATE             ########
######################################################
@app.route('/wishlist/<int:cust_id>', methods=['POST'])
def create_wishlist(cust_id):
    """ create the wishlist with the provided id"""
    wishlist = CustomerList(cust_id, '')
    wishlist.deserialize(request.get_json())
    wishlist.save()
    message = wishlist.serialize()
    location_url = url_for('create_wishlist', cust_id=wishlist.id)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             'Location': location_url
                         })


######################################################
########               PUT/UPDATE             ########
######################################################
@app.route('/wishlist/<int:cust_id>/<int:wishlist_id>', methods=['PUT', 'PATCH'])
def update_wishlist(cust_id,wishlist_id):
    """ Updates the wishlist name if it exists, otherwise returns not found """
    # TODO add products changes as well, for now just asses the wishlists
    wishlists = CustomerList.find_by_id(cust_id,wishlist_id)
    if wishlists:
        old_name = wishlists['Wishlist name']
        message = CustomerList.update(request.get_json(),old_name,cust_id)
        return make_response(jsonify(message), status.HTTP_200_OK)
    else:
        message = {'Error': 'Wishlist not found'}
        return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)
        
######################################################
########               PUT/ADD A PRODUCT      ########
######################################################
@app.route('/wishlist/<int:cust_id>/<int:wishlist_id>/add/<int:pid>', methods=['PUT', 'PATCH'])
def add_product(cust_id,wishlist_id,pid):
    """ Add product ID to a wishlist """
    # TODO add products changes as well, for now just asses the wishlists
    wishlists = CustomerList.find_by_id(cust_id,wishlist_id)
    if wishlists:
        product = wishlists['Product list']
        name = wishlists['Wishlist name']
        product.append(pid)
        c = CustomerList(cust_id,name)
        c.pid = pid
        c.save()
        message = c.serialize()
        return make_response(jsonify(message), status.HTTP_200_OK)
    else:
        message = {'Error': 'Wishlist not found'}
        return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)

##########################################################################
########                GET/SEE all wishlists of a Customer       ########
##########################################################################
@app.route('/wishlist/<int:cust_id>' , methods=['GET'])
def query_wishlist(cust_id):
    """ List the wishlist with the provided name"""
    
    wishlists = CustomerList.find(cust_id)
    wishlist_name = request.args.get('query')
    if wishlist_name:
        if wishlists: 
            message = CustomerList.find_wishlist(wishlists,wishlist_name)
            if message:
                return make_response(jsonify(message),status.HTTP_200_OK)
            else:
                message = {'Error' : 'Wishlist with the given name not found'}
                return make_response(jsonify(message),status.HTTP_404_NOT_FOUND)
        else:
            message = {'No Content' : 'Wishlist Empty'}
            return make_response(jsonify(message),status.HTTP_204_NO_CONTENT)
    else:
        if wishlists:
            message = [{'Wishlist name': w, 'Product list': [p for p in wishlists[w]]} for w in wishlists]
            return make_response(jsonify(message), status.HTTP_200_OK)
        else:
            message = {'No Content' : 'Wishlist Empty'}
            return make_response(jsonify(message), status.HTTP_204_NO_CONTENT)
        
#########################################################################
########                GET/SEE  a Specific Wishlist             ########
#########################################################################
@app.route('/wishlist/<int:cust_id>/<int:wishlist_id>' , methods=['GET'])
def get_wishlist(cust_id,wishlist_id):
    """ List the wishlist with the provided name"""
    
    wishlists = CustomerList.find_by_id(cust_id,wishlist_id)
    
    if wishlists:
        return make_response(jsonify(wishlists),status.HTTP_200_OK)
    else:
        message = {'Error' : 'Wishlist with the given ID not found'}
        return make_response(jsonify(message),status.HTTP_404_NOT_FOUND)


if __name__ == "__main__":
    print "Wishlist Service Starting..."
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
