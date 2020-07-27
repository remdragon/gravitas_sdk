# This file is intended for use with pytest
# you must have gravsettings.ini in folder you are testing from
import configparser
import pytest
from gravsdk import sdkv1

config = configparser.ConfigParser
config.read('gravsettings.ini')

sdk = sdkv1(
	config.get('connection', 'hoststring'),
	config.get('connection', 'checkssl')
)

def test_login():
	# Test valid credentials
	login = config.get('login','gooduser')
	password = config.get('login','goodpass')
	assert sdk.login(login, password) == True

def test_logout():
	assert sdk.logout() == True
