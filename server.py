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

if __name__ == "__main__":
    print "Wishlist Service Starting..."
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
