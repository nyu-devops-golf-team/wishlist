from os import getenv
import json
import requests
import responses
from behave import *
from app import server
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions



BASE_URL = getenv('BASE_URL', 'http://localhost:5000/')
WAIT_SECONDS = 30

@given(u'the following wishlists')
def step_impl(context):
    """ Delete all Pets and load new ones """
    headers = {'Content-Type': 'application/json'}
    #context.resp = requests.delete(context.base_url + '/wishlist/reset', headers=headers)
    #assert context.resp.status_code == 204
    create_url = context.base_url + '/wishlists/1'
    for row in context.table:
        data = {
            "id": row['id'],
            "name": row['name'],
               }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        assert context.resp.status_code == 201

@when(u'I visit the "home page"')
def step_impl(context):
    """ Get the home page URL"""
    context.driver.get(context.base_url)

@then(u'I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    assert message in context.driver.title

@then(u'I should not see "{message}"') #maybe don't need this 'then' test
def step_impl(context, message):
    error_msg = "I should not see '$s' in '%s' " % (message,context.resp.text)
    ensure(message in context.resp.text,False,error_msg)

@when(u'I see the "{element_name} to {text_string}" ')
def step_impl(context,element_name,text_string):
    element_id = 'wishlist_' + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)

###################################################
# The following involve the button id in index.html
###################################################

@when(u'I press the "{button}" button')
def step_impl(context,button):
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()

@then(u'I should see "{name}" in the results')
def step_impl(context,name):
    found = WebDriverWait(context.driver,WAIT_SECONDS).until(expected_conditions.text_to_be_present_in_element((By.ID,'search_results'),name))
    expect(found).to_be(True)

@then(u'I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('search_results')
    error_msg = "I should not see '%s' in '%s'" % (name, element.text)
    ensure(name in element.text, False, error_msg)

@then(u'I should see the message "{message}"')
def step_impl(context,message):
    found = WebDriverWait(context.driver,WAIT_sECONDS).until(expected_conditions.text_to_be_present_in_element((By.ID,'flash_message'),message))
    expect(found).to_be(True)

@when(u'I change "{element_name}" to "{text_string}"')
def step_impl(context,element_name,text_string):
    element_id = 'wishlist_' + element_name.lower()
    element = WebDriverWait(context.driver,WAIT_SECONDS).until(expected_conditions.presence_of_element_located((By.ID, element_id)))
    element.clear()
    element.send_keys(text_string)


@when(u'I set the "name" to "wishlist1"')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I set the "name" to "wishlist1"')

@when(u'I set the "id" to "1"')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I set the "id" to "1"')

@when(u'I change the "name" to "test_change"')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I change the "name" to "test_change"')

@when(u'I set the "id" to "2"')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I set the "id" to "2"')

