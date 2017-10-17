import unittest
from flask_api import status
import server
import json
from coverage import coverage
cov = coverage(branch=True, omit=['venv/*', 'flask/*', 'tests.py'])
cov.start()

# TODO: change these when persistance is added
class WishlistTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.app.debug=False

    def setUp(self):
        server.CustomerList.remove_all()
        server.CustomerList(1,'happy').save()
        server.CustomerList(1,'sad').save()
        self.app = server.app.test_client()

    def test_delete_wishlist_success(self):
        """Delete a wishlist"""
        resp = self.app.delete('/wishlist/3')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.data
        self.assertEqual(data, 'Wishlist 3 deleted')

    def test_delete_wishlist_not_found(self):
        """Delete a wishlist that does not exist"""
        resp = self.app.delete('/wishlist/2')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.data
        self.assertEqual(data, 'Wishlist does not exist')

    def test_delete_wishlist_not_owned(self):
        """ Delete a wishlist that isn't owned by this user"""
        resp = self.app.delete('/wishlist/1')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        data = resp.data
        self.assertEqual(data, 'Wishlist does not exist')
        
    def test_create_wishlist_success(self):
        """Create a wishlist"""
        count = self.get_wishlist_count()
        new_wishlist = {'name': 'laugh', 'PID': 1}
        data = json.dumps(new_wishlist)
        resp = self.app.post('/wishlist/1', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)
        new_data = json.loads(resp.data)
        self.assertEqual(new_data['Wishlist name'], 'laugh')
        resp = self.app.get('/wishlist/1')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        print len(data)
        self.assertEqual(len(data), count + 1)
        self.assertIn(new_data, data)
        
    def test_create_wishlist_no_name(self):
        """Create a wishlist with no wishlist name"""
        new_wishlist = {'PID': 1}
        data = json.dumps(new_wishlist)
        resp = self.app.post('/wishlist/1', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_get_all_wishlist(self):
        """Get all the wishlist of a customer"""
        resp = self.app.get('/wishlist/1')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        
    def test_get_a_wishlist(self):
        """Get 1 wishlist of a customer"""
        resp = self.app.get('/wishlist/1/happy')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['Wishlist name'], 'happy')
        
    def test_get_non_existing_wishlist(self):
        """get a wishlist not found"""
        resp = self.app.get('/wishlist/1/laugh')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_get_empty_wishlist(self):
        """get a wishlist for a non existing customer"""
        resp = self.app.get('/wishlist/2/happy')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        
        
    def get_wishlist_count(self):
        """get the number of wishlist"""
        resp = self.app.get('/wishlist/1')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)
 
if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print("\n\nCoverage Report:\n")
    cov.report()

