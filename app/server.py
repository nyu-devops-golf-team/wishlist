import os
from flask import Flask, jsonify, request, url_for, make_response
from flask_api import status
from flasgger import Swagger
import sys
import logging
from werkzeug.exceptions import NotFound
from app.model import Customer, DataValidationError, Wishlist
from . import app


# Create Flask application
app = Flask(__name__)

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('VCAP_APP_PORT', '5000')

# Configure Swagger before initilaizing it
app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "specs": [
        {
            "version": "1.0.0",
            "title": "Wishlist App",
            "description": "The wishlists resource allow customers to create a collection of products that they wish they had the money to purchase.",
            "endpoint": 'v1_spec',
            "route": '/v1/spec'
        }
    ]
}

# Initialize Swagger after configuring it
Swagger(app)

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

######################################################################
#  Index
######################################################################
@app.route("/")
def index():
    return jsonify(name='Wishlist REST API Service',
                   version='1.0',
                   docs=request.base_url + 'apidocs/index.html'), status.HTTP_200_OK

######################################################
########                DELETE                ########
######################################################
@app.route('/wishlists/<int:cust_id>/<int:wishlist_id>', methods=['DELETE'])
def delete_wishlist(cust_id, wishlist_id):
    # """ Delete the wishlist with the provided id"""
    """
    Delete a Wishlist
    This endpoint will delete a Wishlist based on the customer id and Wishlist id specified in the path
    ---
    tags:
      - Wishlists
    description: Deletes a wishlist from the database
    parameters:
      - name: cust_id
        in: path
        description: ID of customer who wants to delete his/her wishlist
        required: true
        type: integer
      - name: wishlist_id
        in: path
        description: ID of wishlist to be deleted
        required: true
        type: integer
    responses:
      204:
        description: Wishlist deleted
    """
    success = Customer.delete_by_id(cust_id, wishlist_id)
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################
########              POST/CREATE             ########
######################################################
@app.route('/wishlists/<int:cust_id>', methods=['POST'])
def create_wishlist(cust_id):
    # """ create the wishlist with the provided id"""
    """
    Create a Wishlist
    This endpoint will create a Wishlist based on the customer id specified in the path
    ---
    tags:
      - Wishlists
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: cust_id
        in: path
        description: ID of customer who wants to create his/her wishlist
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - Product List
          properties:
            name:
              type: string
              description: name for the Wishlist
            Product List:
              type: array
              items:
                type: string
              description: the list of products in a Wishlist
    responses:
      201:
        description: Wishlist created
        schema:
          id: Wishlist
          properties:
            Customer ID:
              type: integer
              description: ID of customer
            Wishlist:
              type: object
              properties:
                wishlist name:
                  type: string
                  description: the Wishlists's name
                Product list:
                  type: array
                  items:
                    type: string
                  description: the list of products in a Wishlist
      400:
        description: Bad Request (the posted data was not valid)
    """
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
    # """ Update the wishlist name if it exists, otherwise returns not found """
    """
    Update a Wishlist
    This endpoint will update a Wishlist based on the customer id and Wishlist id specified in the path
    ---
    tags:
      - Wishlists
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: cust_id
        in: path
        description: ID of customer who wants to update his/her wishlist
        required: true
        type: integer
      - name: wishlist_id
        in: path
        description: ID of wishlist to be updated
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              description: name for the Wishlist
    responses:
      200:
        description: Wishlist updated
        schema:
          id: Wishlist
          properties:
            Customer ID:
              type: integer
              description: ID of customer
            Wishlist:
              type: object
              properties:
                wishlist name:
                  type: string
                  description: the Wishlists's name
                Product list:
                  type: array
                  items:
                    type: string
                  description: the list of products in a Wishlist
      400:
        description: Bad Request (the put data was not valid)
      404:
        description: Not Found (either customer ID or wishlist ID is not valid, no record found)
    """
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
    # """ Add product ID to a wishlist """
    """
    Add a product to a Wishlist
    This endpoint will add a product to a wishlist based on the customer ID, Wishlist ID, an product ID specified in the path
    ---
    tags:
      - Wishlists
    parameters:
      - name: cust_id
        in: path
        description: ID of customer who wants to add a product to his/her wishlist
        required: true
        type: integer
      - name: wishlist_id
        in: path
        description: ID of wishlist to be updated
        required: true
        type: integer
      - name: pid
        in: path
        description: ID of product to be added
        required: true
        type: integer
    responses:
      200:
        description: Product added to a wishlist
        schema:
          id: Wishlist
          properties:
            Customer ID:
              type: integer
              description: ID of customer
            Wishlist:
              type: object
              properties:
                wishlist name:
                  type: string
                  description: the Wishlists's name
                Product list:
                  type: array
                  items:
                    type: string
                  description: the list of products in a Wishlist
      400:
        description: Bad Request (the put data was not valid)
      404:
        description: Not Found (either customer ID or wishlist ID is not valid, no record found)
    """
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
    # """ delete product ID to a wishlist """
    """
    Delete a product from a Wishlist
    This endpoint will delete a product from a wishlist based on the customer ID, Wishlist ID, an product ID specified in the path
    ---
    tags:
      - Wishlists
    parameters:
      - name: cust_id
        in: path
        description: ID of customer who wants to delete a product from his/her wishlist
        required: true
        type: integer
      - name: wishlist_id
        in: path
        description: ID of wishlist to be updated
        required: true
        type: integer
      - name: pid
        in: path
        description: ID of product to be deleted
        required: true
        type: integer
    responses:
      200:
        description: Product deleted from a wishlist
        schema:
          id: Wishlist
          properties:
            Customer ID:
              type: integer
              description: ID of customer
            Wishlist:
              type: object
              properties:
                wishlist name:
                  type: string
                  description: the Wishlists's name
                Product list:
                  type: array
                  items:
                    type: string
                  description: the list of products in a Wishlist
      404:
        description: Not Found (either customer ID or wishlist ID is not valid, no record found)
    """
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
    # """ List the wishlist with the provided name"""
    """
    Retrieve a list of Wishlists
    This endpoint will return all Wishlists based on the customer ID specified in the path and the optional wishlist name
    ---
    tags:
      - Wishlists
    description: The Wishlists endpoint allows you to query Wishlists
    parameters:
      - name: cust_id
        in: path
        description: ID of customer who wants to view a list of his/her Wishlists
        required: true
        type: integer
      - name: name
        in: query
        description: Name of the wishlist the customer wants to view
        required: false
        type: string
    responses:
      200:
        description: A list of Wishlists retrieved
        schema:
          id: Wishlist
          properties:
            Customer ID:
              type: integer
              description: ID of customer
            Wishlist:
              type: array
              items:
                type: object
                properties:
                  wishlist name:
                    type: string
                    description: the Wishlists's name
                  Product list:
                    type: array
                    items:
                      type: string
                    description: the list of products in a Wishlist
      404:
        description: Not Found (either customer ID or wishlist ID is not valid, no record found)
    """
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
        return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)



#########################################################################
########                GET/SEE  a Specific Wishlist             ########
#########################################################################
@app.route('/wishlists/<int:cust_id>/<int:wishlist_id>' , methods=['GET'])
def get_wishlist(cust_id,wishlist_id):
    # """ List the wishlist with the provided name"""
    """
    List products of a Wishlist
    This endpoint will list products of a Wishlist based on the customer id and Wishlist id specified in the path
    ---
    tags:
      - Wishlists
    parameters:
      - name: cust_id
        in: path
        description: ID of customer who wants to view his/her wishlist
        required: true
        type: integer
      - name: wishlist_id
        in: path
        description: ID of wishlist to be retrieved
        required: true
        type: integer
    responses:
      200:
        description: Wishlist retrieved
        schema:
          id: Wishlist
          properties:
            Customer ID:
              type: integer
              description: ID of customer
            Wishlist:
              type: object
              properties:
                wishlist name:
                  type: string
                  description: the Wishlists's name
                Product list:
                  type: array
                  items:
                    type: string
                  description: the list of products in a Wishlist
      404:
        description: Not Found (either customer ID or wishlist ID is not valid, no record found)
    """
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
    # """ Clear the contents of the wishlist with the given id"""
    """
    Clear all products of a Wishlist
    This endpoint will clear all products of a Wishlist based on the customer id and Wishlist id specified in the path
    ---
    tags:
      - Wishlists
    parameters:
      - name: cust_id
        in: path
        description: ID of customer who wants to view his/her wishlist
        required: true
        type: integer
      - name: wishlist_id
        in: path
        description: ID of wishlist to be retrieved
        required: true
        type: integer
    responses:
      200:
        description: Wishlist cleared
        schema:
          id: Wishlist
          properties:
            Customer ID:
              type: integer
              description: ID of customer
            Wishlist:
              type: object
              properties:
                wishlist name:
                  type: string
                  description: the Wishlists's name
                Product list:
                  type: array
                  items:
                    type: string
                  description: the list of products in a Wishlist
      404:
        description: Not Found (either customer ID or wishlist ID is not valid, no record found)
    """
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
    # """ Display wishlists of all customers if created"""
    """
    Retrieve a list of Wishlists of all customers
    This endpoint will return all Wishlists of all customers
    ---
    tags:
      - Wishlists
    description: The Wishlists endpoint allows you to query all Wishlists of all customers
    responses:
      200:
        description: All Wishlists retrieved
        schema:
          id: Wishlist
          properties:
            Customer ID:
              type: integer
              description: ID of customer
            Wishlist:
              type: array
              items:
                type: object
                properties:
                  wishlist name:
                    type: string
                    description: the Wishlists's name
                  Product list:
                    type: array
                    items:
                      type: string
                    description: the list of products in a Wishlist
      404:
        description: Not Found (No wishlist created for any customer)
    """
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


################################################
# SERVER LOGGING (SPECIFIC TO BDD's INDEX.html)#
################################################


def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print 'Setting up logging...'
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Logging handler established')

