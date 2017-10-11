import unittest
from flask_api import status
import server

# TODO: change these when persistance is added
class DeleteWishlistTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.app.debug=False

    def setUp(self):
        self.app = server.app.test_client()

    def test_delete_wishlist_success(self):
        """Delete a wishlist"""
        resp = self.app.delete('/wishlists/3')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.data
        self.assertEqual(data, 'Wishlist 3 deleted')

    def test_delete_wishlist_not_found(self):
        """Delete a wishlist that does not exist"""
        resp = self.app.delete('/wishlists/2')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.data
        self.assertEqual(data, 'Wishlist does not exist')

    def test_delete_wishlist_not_owned(self):
        """ Delete a wishlist that isn't owned by this user"""
        resp = self.app.delete('/wishlists/1')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        data = resp.data
        self.assertEqual(data, 'Wishlist does not exist')
 

if __name__ == '__main__':
    unittest.main()
