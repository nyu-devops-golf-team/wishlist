import unittest
from flask_api import status
import server
import json
import os
from mock import patch
from redis import Redis, ConnectionError
from coverage import coverage

# TODO: change these when persistance is added
class WishlistTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.app.debug=False

    def setUp(self):
        self.app = server.app.test_client()
        server.init_db()
        server.data_reset()
        server.Customer(1,'happy',[1,2]).save()
        server.Customer(1,'sad',[3]).save()



    def test_delete_wishlist_success(self):
        """Delete a wishlist"""
        # create wishlist
        new_wishlist = {'name': 'happy', 'Product List': [5]}
        data = json.dumps(new_wishlist)
        resp = self.app.post('/wishlists/1', data=data, content_type='application/json')
        # delete created wishlist
        resp = self.app.delete('/wishlists/1/1')
        data = resp.data
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(data, '')

    def test_delete_wishlist_not_found(self):
        """Delete a wishlist that does not exist"""
        # Delete wishlist that does not exist
        resp = self.app.delete('/wishlists/1/201')
        data = resp.data
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(data, '')

    def test_create_wishlist_success(self):
        """Create a wishlist"""
        new_wishlist = {'name': 'laugh', 'Product List': [1]}
        data = json.dumps(new_wishlist)
        resp = self.app.post('/wishlists/1', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)
        new_data = json.loads(resp.data)
        resp_check = new_data['Wishlist']
        self.assertEqual(resp_check['3']['wishlist name'], 'laugh')
        resp = self.app.get('/wishlists/1')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        resp_check = data['Wishlist']
        self.assertEqual(len(resp_check), 3)


    def test_clear_wishlist(self):
        """ clear contents of a wishlist"""
        resp = self.app.put('/wishlists/1/1/clear', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get('/wishlists/1/1')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        resp_check = data['Wishlist']
        new_data = []
        self.assertEqual(resp_check[1]['Product list'],new_data)

    def test_clear_nonExisting_wishlist(self):
        """Clear contents of a non existing wishlist"""
        resp = self.app.put('/wishlists/1/3/clear', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_clear_nonExisting_Customer_wishlist(self):
        """Clear contents of wishlist for a non existing customer"""
        resp = self.app.put('/wishlists/4/1/clear', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_wishlist(self):
        """Update the name of a wishlist """
        new_name = {'name' : 'laugh'}
        data = json.dumps(new_name)
        resp = self.app.put('/wishlists/1/1', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get('/wishlists/1/1')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        resp_check = data['Wishlist']
        self.assertEqual(resp_check[1]['wishlist name'],'laugh')


    def test_update_non_existing_wishlist(self):
        """ Update a non existing wishlist """
        new_name = {'name' : 'laugh'}
        data = json.dumps(new_name)
        resp = self.app.put('/wishlists/1/3', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_non_existing_customer_wishlist(self):
        """ Update an empty wishlist """
        new_name = {'name' : 'laugh'}
        data = json.dumps(new_name)
        resp = self.app.put('/wishlists/2/3', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_product_add(self):
        """ Add a product to an existing wishlist """
        resp = self.app.put('/wishlists/1/1/4', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        resp_check = data['Wishlist']
        product = resp_check[1]['Product list']
        self.assertIn(4, product)

    def test_product_no_wishlist(self):
        """ Add a product to a non existing wishlist """
        resp = self.app.put('/wishlists/1/3/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_product_no_customer(self):
        """ Add a product to a non existing customer """
        resp = self.app.put('/wishlists/2/3/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_wishlist_no_name(self):
        """Create a wishlist with no wishlist name"""
        new_wishlist = {'Product List': [1]}
        data = json.dumps(new_wishlist)
        resp = self.app.post('/wishlists/1', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_wishlist(self):
        """Get all the wishlist of a customer"""
        resp = self.app.get('/wishlists/1')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        resp_check = data['Wishlist']
        self.assertEqual(len(resp_check), 2)

    def test_display_all_wishlists(self):
        """Display wishlists of all customers"""
        resp = self.app.get('/wishlists')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


    def test_query_a_wishlist_by_name(self):
        """Get 1 wishlist of a customer"""
        resp = self.app.get('/wishlists/1', query_string='name=happy')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        resp_check = data['Wishlist']
        self.assertEqual(resp_check['1']['wishlist name'],'happy')



    def test_query_a_wishlist_with_no_name(self):
        """Get 1 wishlist of a customer"""
        resp = self.app.get('/wishlists/1', query_string='name=laugh')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_query_wishlist_not_created_by_customer(self):
        """ Search a  wishlist not created by a customer"""
        resp = self.app.get('/wishlists/2', query_string='name=happy')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_wishlist(self):
        """get a specific wishlist of a customer"""
        resp = self.app.get('/wishlists/1/1')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        resp_check = data['Wishlist']
        self.assertEqual(resp_check[1]['wishlist name'],'happy')

    def test_get_non_existing_wishlist(self):
        """get a wishlist not found"""
        resp = self.app.get('/wishlists/1/3')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_empty_wishlist(self):
        """get a wishlist for a non existing customer"""
        resp = self.app.get('/wishlists/2/1')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_wishlist_empty(self):
        """ Empty wishlist for a new customer"""
        resp = self.app.get('/wishlists/2')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_no_data_in_database(self):
        """Database is empty : get the list"""
        server.data_reset()
        resp = self.app.get('/wishlists')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_a_product(self):
        """Delete a product from a wishlist"""
        resp = self.app.delete('/wishlists/1/1/1')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        resp_check = data['Wishlist']
        self.assertNotIn(1,resp_check[1]['Product list'])

    def test_delete_product_of_no_wishlist(self):
        """Delete a product of non existing wishlist"""
        resp = self.app.delete('/wishlists/1/4/1')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product_no_customer(self):
        """Delete a product of non existing customer"""
        resp = self.app.delete('/wishlists/2/4/1')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


if __name__ == '__main__':
     unittest.main()
