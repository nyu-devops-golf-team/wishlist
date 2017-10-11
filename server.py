import os
from flask import Flask, make_response
from flask_api import status

# Create Flask application
app = Flask(__name__)

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

@app.route('/wishlists/<int:wishlist_id>', methods=['DELETE'])
def delete_wishlist(wishlist_id):
    """ Deletes the wishlist with the provided id""" 
    # TODO undo these fixtures once persistance is added
    if wishlist_id == 3:
        return make_response('Wishlist {} deleted'.format(wishlist_id))
    elif wishlist_id == 2:
        return make_response('Wishlist does not exist', status.HTTP_404_NOT_FOUND)
    else:
        return make_response('Wishlist does not exist', status.HTTP_403_FORBIDDEN)
    
 @app.route('/<int:cust_id>/wishlist', methods=['POST'])
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

@app.route('/<int:cust_id>/wishlist' , methods=['GET'])
def display_cust_wishlist(cust_id):
    """ List the wishlists with the provided id"""
	dic = CustomerList.find(cust_id)
	return make_response(jsonify(dic), status.HTTP_200_OK)

if __name__ == "__main__":
    print "Wishlist Service Starting..."
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
