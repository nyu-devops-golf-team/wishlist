from redis import Redis
from redis.exceptions import ConnectionError
from cerberus import Validator
from app.custom_exceptions import DataValidationError
import json
import threading
import os
import pickle
import logging


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Wishlist(object):

    def __init__(self):
        self.index = 0
        self.wishlist_data = {}

    def save_values(self, i, name, productList):
        self.index = i
        Wname_product = {}
        if productList:
            product = [p for p in productList]
            Wname_product[name] = product
            self.wishlist_data[self.index] = Wname_product

        else:
            product = []
            Wname_product[name] = product
            self.wishlist_data[self.index] = Wname_product


    def display_by_id(self):
        index = self.index
        result = {}
        if self.wishlist_data.has_key(index):
            Wname_product = self.wishlist_data[index]
            for k,v in Wname_product.iteritems():
                message =  {"wishlist name" : k, "Product list" : [p for p in v]}
                result[index] = message
                return result
        else:
            return None


class Customer(object):
    
    """ Wishlist Schema to Database"""
    logger = logging.getLogger(__name__)
    redis = None
    schema = {
        'id': {'type': 'integer'},
        'name': {'type': 'string', 'required': True}
        }
    __validator = Validator(schema)

    def __init__(self,custid,name,plist):
        self.cust_id = custid
        self.wishlist_name = name
        self.product_list = plist


    def deserialize(self, data):
          if not isinstance(data, dict):
              raise DataValidationError('Invalid wishlist data: body of request contained bad or no data')

          if data.has_key('Product List'):
              self.product_list = [p for p in data['Product List']]

          try:
              self.wishlist_name = data['name']
          except KeyError as err:
              raise DataValidationError('Invalid wishlist: missing wishlist name')
          return

    def save(self):
          if self.cust_id == 0:
              raise DataValidationError('Invalid customer ID : Please provide a valid ID')
          if Customer.redis.exists(self.cust_id):
              maxi = 0
              message = pickle.loads(Customer.redis.get(self.cust_id))

              for m in message.iteritems():
                  if m[0]>maxi:
                      maxi = m[0]

              w = Wishlist()
              i = maxi+1
              w.save_values(i,self.wishlist_name,self.product_list)
              new_message = w.display_by_id()
              message.update(new_message)
              Customer.redis.set(self.cust_id,pickle.dumps(message))
              message = w.display_by_id()
              return {"Customer ID" : self.cust_id , "Wishlist" : message}
          else:
              w = Wishlist()
              w.save_values(1,self.wishlist_name,self.product_list)
              message = w.display_by_id()
              Customer.redis.set(self.cust_id,pickle.dumps(message))
              return {"Customer ID" : self.cust_id , "Wishlist" : message}

    @staticmethod
    def serialize(m):
        data = {}
        data[m[0]] = {"wishlist name" : m[1]["wishlist name"], "Product list" : [p for p in m[1]["Product list"]]}
        return data

    @staticmethod
    def find_by_id(custid,wid):
          message = pickle.loads(Customer.redis.get(custid))
          result = {}
          for m in message.iteritems():
              if m[0] == wid:
                  result = m
                  return {"Customer ID" : custid , "Wishlist" : result}
          else:
              return None

    @staticmethod
    def find_by_name(custid,wname):
          message = pickle.loads(Customer.redis.get(custid))
          result = {}
          k=0
          for m in message.iteritems():
              if m[1]["wishlist name"] == wname:
                  data = Customer.serialize(m)
                  result.update(data)
                  k=1
          if k == 1:
              return {"Customer ID" : custid , "Wishlist" : result}
          else:
              return None



    @staticmethod
    def find_by_custid(custid):
          message = pickle.loads(Customer.redis.get(custid))
          result = {}
          for m in message.iteritems():
              data = Customer.serialize(m)
              result.update(data)

          return {"Customer ID" : custid , "Wishlist" :result}

    @staticmethod
    def display_all():
          for k in Customer.redis.keys():
              return True
          return False

    @staticmethod
    def check_custid(custid):
          if Customer.redis.exists(custid):
              return True
          else:
              return False

    @staticmethod
    def delete_by_id(custid,wid):
          message = pickle.loads(Customer.redis.get(custid))
          result = {}
          for m in message.iteritems():
              if m[0] != wid:
                  data = Customer.serialize(m)
                  result.update(data)
          Customer.redis.set(custid,pickle.dumps(result))
          return True

    @staticmethod
    def update(custid,wid,data):
          message = pickle.loads(Customer.redis.get(custid))
          result = {}
          for m in message.iteritems():
              if m[0] == wid:
                  m[1]["wishlist name"] = data['name']
                  data = Customer.serialize(m)
                  result.update(data)
              else:
                  data = Customer.serialize(m)
                  result.update(data)

          Customer.redis.set(custid,pickle.dumps(result))
          return True

    @staticmethod
    def addProduct(custid,wid,pid):
          message = pickle.loads(Customer.redis.get(custid))
          result = {}
          for m in message.iteritems():
              if m[0] == wid:
                  productList = [p for p in m[1]["Product list"] if p!=pid]
                  productList.append(pid)
                  m[1]["Product list"] = [p for p in productList]
                  data = Customer.serialize(m)
                  result.update(data)
              else:
                  data = Customer.serialize(m)
                  result.update(data)
          Customer.redis.set(custid,pickle.dumps(result))
          return True

    @staticmethod
    def deleteProduct(custid,wid,pid):
          message = pickle.loads(Customer.redis.get(custid))
          result = {}
          for m in message.iteritems():
              if m[0] == wid:
                  productList = [p for p in m[1]["Product list"] if p!=pid]
                  m[1]["Product list"] = [p for p in productList]
                  data = Customer.serialize(m)
                  result.update(data)
              else:
                  data = Customer.serialize(m)
                  result.update(data)
          Customer.redis.set(custid,pickle.dumps(result))
          return True

    @staticmethod
    def clear_list(custid,wid):
          message = pickle.loads(Customer.redis.get(custid))
          result = {}
          for m in message.iteritems():
              if m[0] == wid:
                  m[1]["Product list"] = []
                  data = Customer.serialize(m)
                  result.update(data)
              else:
                  data = Customer.serialize(m)
                  result.update(data)

          Customer.redis.set(custid,pickle.dumps(result))
          return True

    @staticmethod
    def remove_all():
        """ Removes all entrie from the database """
        Customer.redis.flushdb()


    @staticmethod
    def connect_to_redis(hostname, port, password):
        """ Connects to Redis and tests the connection """
        Customer.redis = Redis(host=hostname, port=port, password=password)
        try:
            Customer.redis.ping()
        except ConnectionError:
            Customer.redis = None
        return Customer.redis

    @staticmethod
    def init_db(redis=None):
        if redis:
            Customer.redis = redis
            try:
                Customer.redis.ping()
            except ConnectionError:
                Customer.redis = None
                raise ConnectionError('Could not connect to the Redis Service')
            return
        # Get the credentials from the Bluemix environment
        if 'VCAP_SERVICES' in os.environ:
            vcap_services = os.environ['VCAP_SERVICES']
            services = json.loads(vcap_services)
            creds = services['rediscloud'][0]['credentials']
            Customer.connect_to_redis(creds['hostname'], creds['port'], creds['password'])
        else:
            Customer.connect_to_redis('127.0.0.1', 6379, None)
            if not Customer.redis:
                Customer.connect_to_redis('redis', 6379, None)


        if not Customer.redis:
            # if you end up here, redis instance is down.
            raise ConnectionError('Could not connect to the Redis Service')
