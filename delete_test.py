import unittest
from flask_api import status
import server

class DeleteWishlistTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.app.debug=False

    def setUp(self):
        self.app = server.app.test_client()

    def test_delete_wishlist(self):
        """ Delete a wishlist"""
        # TODO: adjust this later when persistance is added
        resp = self.app.delete('/wishlists/3')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.data
        self.assertEqual(data, 'Wishlist 3 deleted')
        

if __name__ == '__main__':
    unittest.main()
