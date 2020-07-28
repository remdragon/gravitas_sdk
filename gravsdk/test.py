# This file is intended for use with pytest
import configparser
import pytest
from gravsdk import sdkv1


sdk = sdkv1(
	'https://127.0.0.1',
	False
)

def test_login():
	# Test valid credentials
	login = 'restuser'
	password = 'puppies123456789'
	assert sdk.login(login, password, testmode=True, {}) == True

def test_logout():
	assert sdk.logout(testmode=True, {}) == True
