# This file is intended for use with pytest

from gravsdk import sdkv1

sdk = sdkv1('https://127.0.0.1:4443', False)

def test_login():
	# Test valid credentials
	login = 'restuser'
	password = 'puppies1234567890'
	assert sdk.login(login, password) == True

def test_logout():
	assert sdk.logout() == True
