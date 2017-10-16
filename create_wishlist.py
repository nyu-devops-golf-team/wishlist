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
		self.wishlist[name] = []
		self.wishlist_id[name] = self.__next_index()
		
	def add_product(self,name,pid):
		if pid == 0:
			return
		else:
			dict = self.wishlist[name]
			val = [id for id in dict if id == pid]
			if val:
				return
			else:
				dict.append(pid)
				
	def display(self,name):
		dict = self.wishlist[name]
		return dict
		
	
        def __next_index(self):
            """ Generates the next index in a continual sequence """
           
            self.index += 1
            return self.index
			
	
			
		
		

class CustomerList(object):
	cust_id = {}
	
	def __init__(self, id, name=''):
        	self.id = id
		self.name = name
		self.pid = 0
		
	
	def deserialize(self, data):
		if not isinstance(data, dict):
            		raise DataValidationError('Invalid customer: body of request contained bad or no data')
        	
		if data.has_key('name'):
			self.name = data['name']
		
		if data.has_key('PID'):
			self.pid = data['PID']
		return
		
	def save(self):   
		if CustomerList.cust_id.has_key(self.id):
			c = CustomerList.cust_id[self.id]
			if c.wishlist.has_key(self.name):
				c.add_product(self.name,self.pid)
				return
			else:
				c.create(self.name)
				c.add_product(self.name,self.pid)
		else:
			c = Customer({},{})
			c.create(self.name)
			c.add_product(self.name,self.pid)
			CustomerList.cust_id[self.id] = c
			
		return
		
	def serialize(self):
		
		c = CustomerList.cust_id[self.id]
		product_list = c.display(self.name)
		return {"Customer_id": self.id, "Wishlist name": self.name, "Wishlist ID": c.wishlist_id[self.name],"Wishlist": product_list}
	
	@staticmethod
	def find(custid):
		if CustomerList.cust_id.has_key(custid):
			c = CustomerList.cust_id[custid]
			return c.wishlist
		else:
			return None
			
	@staticmethod
	def find_wishlist(wishlists,name):
		if wishlists.has_key(name):
			return {"Wishlist name": name, "Product list": wishlists[name]}
		else:
			return None
