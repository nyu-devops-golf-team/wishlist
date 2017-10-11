import threading

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Customer(object):
	
	
    
	def __init__(self, wishlist={}, wishlist_id={}):
		self.wishlist = wishlist
		self.wishlist_id = wishlist_id
		self.index = 0
		
	
	def create(self,name):
		self.wishlist[name] = {}
		self.wishlist_id[name] = self.__next_index()
		
	
        def __next_index(self):
            """ Generates the next index in a continual sequence """
           
            self.index += 1
            return self.index
		
		

class CustomerList(object):
	cust_id = {}
	
	def __init__(self, id, name=''):
        	self.id = id
		self.name = name      
	
	def deserialize(self, data):
		    	if not isinstance(data, dict):
            		raise DataValidationError('Invalid customer: body of request contained bad or no data')
        	
		if data.has_key('name'):
			self.name = data['name']
		return
		
	def save(self):   
		if CustomerList.cust_id.has_key(self.id):
			c = CustomerList.cust_id[self.id]
			if c.wishlist.has_key(self.name):
				return
			else:
				c.create(self.name)
		else:
			c = Customer({},{})
			c.create(self.name)
			CustomerList.cust_id[self.id] = c
			
		return
		
	def serialize(self):
		
		c = CustomerList.cust_id[self.id]
		return {"id": self.id, "Wishlist name": self.name, "Wishlist ID": c.wishlist_id[self.name],"Wishlist": c.wishlist[self.name]}
	
	@staticmethod
	def find(custid):
		if CustomerList.cust_id.has_key(custid):
			c = CustomerList.cust_id[custid]
			return c.wishlist
