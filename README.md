# wishlist
[![Build Status](https://travis-ci.org/nyu-devops-golf-team/wishlist.svg?branch=master)](https://travis-ci.org/nyu-devops-golf-team/wishlist)
[![codecov](https://codecov.io/gh/nyu-devops-golf-team/wishlist/branch/master/graph/badge.svg)](https://codecov.io/gh/nyu-devops-golf-team/wishlist)

[Live Service](http://nyu-wishlist-service-f17.mybluemix.net/)  | | [BDD UI Dashboard](http://nyu-wishlist-service-f17.mybluemix.net/)  | | [API Docs](http://nyu-wishlist-service-f17.mybluemix.net/apidocs/index.html?url=/v1/spec)



The wishlists resource allow customers to create a collection of products that they wish they had the money to purchase. At a minimum it should contain references to a product. A customer might have multiple wish lists so they might want to name them for easy identification.

## Developing

It's easiest to develop using Vagrant. After installing Vagrant run the following:

```
vagrant up
vagrant ssh
cd /vagrant
python run.py
```

and the server will be live on "http://localhost:5000"



If you can't or won't use Vagrant than you must install Redis then run the following commands:

```
virtualenv venv
./venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Testing

### Unit
Unit tests and coverage are run after sshing into vagrant and going to the `/vagrant` folder by running the following:

```
nosetests
```

### BDD
BDD tests are run after sshing into vagrant and going to the `/vagrant` folder by running the following:

```
behave
```

