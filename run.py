"""
Start the Wishlist Service and initializes logging
"""

import os
from app import app,server

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('VCAP_APP_PORT', '5000')

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    print "****************************************"
    print " W I S H L I S T   S E R V I C E"
    print "****************************************"
    server.initialize_logging()
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
