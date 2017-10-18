import unittest
from flask_api import status
import server
import json
from coverage import coverage

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
        # create wishlist
        new_wishlist = {'name': 'to delete', 'PID': 5}
        data = json.dumps(new_wishlist)
        resp = self.app.post('/wishlist/1', data=data, content_type='application/json')
        # delete created wishlist
        resp = self.app.delete('/wishlist/1/3')
        data = resp.data
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data, 'Wishlist 3 deleted')

    def test_delete_wishlist_not_found(self):
        """Delete a wishlist that does not exist"""
        # Delete wishlist that does not exist
        resp = self.app.delete('/wishlist/5/201')
        data = resp.data
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
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
        self.assertEqual(len(data), count + 1)
        self.assertIn(new_data, data)
        
    def test_update_wishlist(self):
        """Update the name of a wishlist """
        new_name = {'name' : 'laugh'}
        data = json.dumps(new_name)
        resp = self.app.put('/wishlist/1/1', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get('/wishlist/1/1')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['Wishlist name'], 'laugh')
        
    def test_update_non_existing_wishlist(self):
        """ Update a non existing wishlist """
        new_name = {'name' : 'laugh'}
        data = json.dumps(new_name)
        resp = self.app.put('/wishlist/1/3', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_update_empty_wishlist(self):
        """ Update an empty wishlist """
        new_name = {'name' : 'laugh'}
        data = json.dumps(new_name)
        resp = self.app.put('/wishlist/2/3', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_action_product_add(self):
        """ Add a product to an existing wishlist """
        resp = self.app.put('/wishlist/1/1/add/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        product = data['Product list']
        self.assertIn(2, product)
        
    def test_add_product_no_wishlist(self):
        """ Add a product to a non existing wishlist """
        resp = self.app.put('/wishlist/1/3/add/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        
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
        
    def test_query_a_wishlist_by_name(self):
        """Get 1 wishlist of a customer"""
        resp = self.app.get('/wishlist/1', query_string='query=happy')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertTrue('happy' in resp.data)
        self.assertFalse('sad' in resp.data)
        data = json.loads(resp.data)
        self.assertEqual(data['Wishlist name'], 'happy')
            
    def test_query_a_wishlist_with_no_name(self):
        """Get 1 wishlist of a customer"""
        resp = self.app.get('/wishlist/1', query_string='query=laugh')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
            
    def test_query_wishlist_not_created_by_customer(self):
        """ Search a  wishlist not created by a customer"""
        resp = self.app.get('/wishlist/2', query_string='query=happy')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        
    def test_get_wishlist(self):
        """get a specific wishlist of a customer"""
        resp = self.app.get('/wishlist/1/1')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['Wishlist name'], 'happy')
        
    def test_get_non_existing_wishlist(self):
        """get a wishlist not found"""
        resp = self.app.get('/wishlist/1/3')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_get_empty_wishlist(self):
        """get a wishlist for a non existing customer"""
        resp = self.app.get('/wishlist/2/1')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_wishlist_empty(self):
        """ Empty wishlist for a new customer"""
        resp = self.app.get('/wishlist/2')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        
    def get_wishlist_count(self):
        """get the number of wishlist"""
        resp = self.app.get('/wishlist/1')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)
 
if __name__ == '__main__':
     unittest.main()

