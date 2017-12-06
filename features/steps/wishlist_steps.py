from os import getenv
import json
import requests
from behave import *
from app import server

BASE_URL = getenv('BASE_URL', 'http://localhost:1234/')

@given(u'the following wishlists')
def step_impl(context):
    """ Delete all Pets and load new ones """
    headers = {'Content-Type': 'application/json'}
    #context.resp = requests.delete(context.base_url + '/wishlist/reset', headers=headers)
    assert context.resp.status_code == 204
    create_url = context.base_url + '/wishlist'
    for row in context.table:
        data = {
            "name": row['name'],
            "id": row['id'],
               }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        assert context.resp.status_code == 201

@when(u'I visit the "home page"')
def step_imp1(context,message):
    """ Get the home page URL"""
    context.driver.get(context.base_url)

@then(u'I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    assert message in context.driver.title

@then(u'I should not see "{message}"')
def step_impl(context, message):
    assert message not in context.resp.text
