import os
from flask import Flask, jsonify, request, url_for, make_response
from flask_api import status
import sys
from werkzeug.exceptions import NotFound
from model import Customer, DataValidationError, Wishlist

# Create Flask application
app = Flask(__name__)

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('VCAP_APP_PORT', '5000')


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
@app.route('/wishlists/<int:cust_id>/<int:wishlist_id>', methods=['DELETE'])
def delete_wishlist(cust_id, wishlist_id):
    """ Deletes the wishlist with the provided id"""
    success = Customer.delete_by_id(cust_id, wishlist_id)
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################
########              POST/CREATE             ########
######################################################
@app.route('/wishlists/<int:cust_id>', methods=['POST'])
def create_wishlist(cust_id):
    """ create the wishlist with the provided id"""
    wishlist = Customer(cust_id,"",[])
    wishlist.deserialize(request.get_json())
    message = wishlist.save()

    location_url = url_for('create_wishlist', cust_id=wishlist.cust_id)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             'Location': location_url
                         })


######################################################
########               PUT/UPDATE             ########
######################################################
@app.route('/wishlists/<int:cust_id>/<int:wishlist_id>', methods=['PUT', 'PATCH'])
def update_wishlist(cust_id,wishlist_id):
    """ Updates the wishlist name if it exists, otherwise returns not found """
    # TODO add products changes as well, for now just asses the wishlists
    if Customer.check_custid(cust_id):
        message = Customer.find_by_id(cust_id,wishlist_id)
        if message:
            result = Customer.update(cust_id,wishlist_id,request.get_json())
            res = Customer.find_by_id(cust_id,wishlist_id)
            return make_response(jsonify(res), status.HTTP_200_OK)
        else:
            message = {'Error': 'Wishlist with given ID not found'}
            return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)
    else:
        message = {'Invalid' : 'Invalid customer ID'}
        return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)

######################################################
########               PUT/ADD A PRODUCT      ########
######################################################
@app.route('/wishlists/<int:cust_id>/<int:wishlist_id>/<int:pid>', methods=['PUT', 'PATCH'])
def add_product(cust_id,wishlist_id,pid):
    """ Add product ID to a wishlist """
    # TODO add products changes as well, for now just asses the wishlists
    if Customer.check_custid(cust_id):
        message = Customer.find_by_id(cust_id,wishlist_id)
        if message:
            result = Customer.addProduct(cust_id,wishlist_id,pid)
            res = Customer.find_by_id(cust_id,wishlist_id)
            return make_response(jsonify(res), status.HTTP_200_OK)
        else:
            message = {'Error': 'Wishlist with given ID not found'}
            return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)
    else:
        message = {'Invalid' : 'Invalid customer ID'}
        return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)

######################################################
########               Delete A PRODUCT      ########
######################################################
@app.route('/wishlists/<int:cust_id>/<int:wishlist_id>/<int:pid>', methods=['DELETE'])
def delete_product(cust_id,wishlist_id,pid):
    """ delete product ID to a wishlist """
    # TODO add products changes as well, for now just asses the wishlists
    if Customer.check_custid(cust_id):
        message = Customer.find_by_id(cust_id,wishlist_id)
        if message:
            result = Customer.deleteProduct(cust_id,wishlist_id,pid)
            res = Customer.find_by_id(cust_id,wishlist_id)
            return make_response(jsonify(res), status.HTTP_200_OK)
        else:
            message = {'Error': 'Wishlist with given ID not found'}
            return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)
    else:
        message = {'Invalid' : 'Invalid customer ID'}
        return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)

##########################################################################
########                GET/SEE all wishlists of a Customer       ########
##########################################################################
@app.route('/wishlists/<int:cust_id>' , methods=['GET'])
def query_wishlist(cust_id):
    """ List the wishlist with the provided name"""
    if Customer.check_custid(cust_id):
        query_name = request.args.get('name')
        if query_name:
            message = Customer.find_by_name(cust_id,query_name)
            if message:
                return make_response(jsonify(message),status.HTTP_200_OK)
            else:
                message = {'Error' : 'Wishlist with the given name not found'}
                return make_response(jsonify(message),status.HTTP_404_NOT_FOUND)
        else:
            message = Customer.find_by_custid(cust_id)
            return make_response(jsonify(message),status.HTTP_200_OK)
    else:
        message = {'Invalid' : 'Invalid customer ID'}
        return make_response(jsonify(message), status.HTTP_204_NO_CONTENT)



#########################################################################
########                GET/SEE  a Specific Wishlist             ########
#########################################################################
@app.route('/wishlists/<int:cust_id>/<int:wishlist_id>' , methods=['GET'])
def get_wishlist(cust_id,wishlist_id):
    """ List the wishlist with the provided name"""
    if Customer.check_custid(cust_id):
        message = Customer.find_by_id(cust_id,wishlist_id)
        if message:
            return make_response(jsonify(message),status.HTTP_200_OK)
        else:
            message = {'Error' : 'Wishlist with the given ID not found'}
            return make_response(jsonify(message),status.HTTP_404_NOT_FOUND)
    else:
        message = {'Invalid' : 'Invalid customer ID'}
        return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)

#########################################################################
########                Clear  a Specific Wishlist               ########
#########################################################################

@app.route('/wishlists/<int:cust_id>/<int:wishlist_id>/clear' , methods=['PUT','PATCH'])
def clear_wishlist(cust_id,wishlist_id):
    """ Clear the contents of the wishlist with the given id"""
    if Customer.check_custid(cust_id):
        message = Customer.find_by_id(cust_id,wishlist_id)
        if message:
            res = Customer.clear_list(cust_id,wishlist_id)
            return make_response(jsonify(message),status.HTTP_200_OK)
        else:
            message = {'Error' : 'Wishlist with the given ID not found'}
            return make_response(jsonify(message),status.HTTP_404_NOT_FOUND)
    else:
        message = {'Invalid' : 'Invalid customer ID'}
        return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)

#########################################################################
########                Display all wishlists                    ########
#########################################################################

@app.route('/wishlists' , methods=['GET'])
def display_all_wishlists():
    """ Display wishlists of all customers if created"""

    if Customer.display_all():
        message = [Customer.find_by_custid(k) for k in Customer.redis.keys()]
        return make_response(jsonify(message),status.HTTP_200_OK)
    else:
        message = {'Error' : 'No wishlist created for any customer'}
        return make_response(jsonify(message),status.HTTP_404_NOT_FOUND)

@app.before_first_request
def init_db(redis=None):
    """ Initlialize the model """
    Customer.init_db(redis)

def data_reset():
    Customer.remove_all()





if __name__ == "__main__":
    print "Wishlist Service Starting..."
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
