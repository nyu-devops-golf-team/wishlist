import threading


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass


class Customer(object):
    def __init__(self, wishlist={}, wishlist_id={}):
        self.wishlist = wishlist
        self.wishlist_id = wishlist_id
        self.index = 0

    def create(self, name):
        self.wishlist[name] = []
        w_id = self.__next_index()
        self.wishlist_id[w_id] = name

    def add_product(self, name, pid):
        if pid == 0:
            return
        else:
            dict = self.wishlist[name]
            val = [id for id in dict if id == pid]
            if val:
                return
            else:
                dict.append(pid)

    def display(self, name):
        dict = self.wishlist[name]
        return dict

    def __next_index(self):
        """ Generates the next index in a continual sequence """

        self.index += 1
        return self.index


class CustomerList(object):
    cust_id = {}

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.pid = 0

    def deserialize(self, data):
        if not isinstance(data, dict):
            raise DataValidationError('Invalid wishlist data: body of request contained bad or no data')

        if data.has_key('PID'):
            self.pid = data['PID']

        try:
            self.name = data['name']
        except KeyError as err:
            raise DataValidationError('Invalid wishlist: missing wishlist name')
        return

    def save(self):
        if CustomerList.cust_id.has_key(self.id):
            c = CustomerList.cust_id[self.id]
            if c.wishlist.has_key(self.name):
                c.add_product(self.name, self.pid)
                return
            else:
                c.create(self.name)
                c.add_product(self.name, self.pid)
        else:
            c = Customer({}, {})
            c.create(self.name)
            c.add_product(self.name, self.pid)
            CustomerList.cust_id[self.id] = c

        return

    def serialize(self):
        c = CustomerList.cust_id[self.id]
	for k,v in c.wishlist_id.iteritems():
	    if self.name == v:
	        id = k
        product_list = c.display(self.name)
        return {"ID": id, "Wishlist name": self.name, "Product list": [p for p in product_list]}


    @staticmethod
    def find(custid):
        if CustomerList.cust_id.has_key(custid):
            c = CustomerList.cust_id[custid]
            return c.wishlist
        else:
            return None

    @staticmethod
    def find_wishlist(wishlists,name,custid):
        if wishlists.has_key(name):
			c = CustomerList.cust_id[custid]
			for k,v in c.wishlist_id.iteritems():
				if name == v:
					id = k
                        return {"ID": id, "Wishlist name": name, "Product list": [p for p in wishlists[name]]}
        else:
            return None


    @staticmethod
    def delete_by_id(custid,wid):
        if CustomerList.cust_id.has_key(custid):
            c = CustomerList.cust_id[custid]
            if c.wishlist_id.has_key(wid):
                c.wishlist_id.pop(wid, None)
                return True
        return False

    @staticmethod
    def find_by_id(custid,wid):
        if CustomerList.cust_id.has_key(custid):
            c = CustomerList.cust_id[custid]
            if c.wishlist_id.has_key(wid):
                name = c.wishlist_id[wid]
                return {"ID": wid, "Wishlist name": name, "Product list": [p for p in c.wishlist[name]]}
            else:
                return None
        else:
            return None

    @staticmethod
    def update(data,oldName,custid):
        c = CustomerList.cust_id[custid]
        if(c.wishlist.has_key(oldName)):
            product = c.wishlist[oldName]
            del c.wishlist[oldName]
            new_name = data['name']
            c.wishlist[new_name] = product
            for key,value in c.wishlist_id.iteritems():
                if value == oldName:
                    index = key
            c.wishlist_id[index] = new_name
            CustomerList.cust_id[custid] = c
            return {"Successfully updated wishlist with new name ": new_name}



    @staticmethod
    def remove_all():
        """ Removes all of the wishlists from the database """
        CustomerList.cust_id = {}
        return CustomerList.cust_id

    @staticmethod
    def clear_list(custid,data):
        wid = data['ID']
        c = CustomerList.cust_id[custid]
        name = c.wishlist_id[wid]
        c.wishlist[name] = []
        CustomerList.cust_id[custid] = c
        return {"Successfully cleared wishlist with ID ": wid}

    @staticmethod
    def display_all():
        if not CustomerList.cust_id:
            return None
        else:
            return CustomerList.cust_id
