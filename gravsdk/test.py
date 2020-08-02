# This file is intended for use with pytest
# Usage: pytest -sx test.py
"""
# Gravitas Python SDK v1
This is version 1 of the gravitas SDK. This includes the legacy/compatibility implementation of Gravitas.

|Attribute|Required|Type|Description|
|-|-|-|-|
|`hoststring`|Required|string|Host connect string
|`protocol`|Optional|string|Protocol used for communication with the Gravitas API server. Options are `https` and `wss` (defaults to `https`).
|`port`|Optional|integer|Port number of the Gravitas API server (defaults to `443`)|
|`ssl_verify_enable`|Optional|boolean|Enables/disables SSL certificate verification (defaults to `True`). **NOTE: in production this must remain as `True`**

## Usage

	from gravsdk import sdkv1
	sdk = sdkv1(
		hoststring = 'https://10.10.10.10:4443', # The port is optional
		ssl_verify_enable = False # This should be `True` in production
	)
"""

import configparser
import pytest
from gravsdk import sdkv1, GravAuthError
import requests_mock
import urllib
host = 'https://127.0.0.1:443'
basepath = 'rest'

sdk = sdkv1 (
	host,
	False,
)

class Test_authentication():
	"""
	# Authentication

	Gravitas performs authentication in one of two ways:
	
	* Username and password (with optional 2FA token)
	* API Key

	Usage of these methods is entirely dependent on Gravitas system configuration

	## SDK Methods
	[login](authentication/login.md)
	[logout](authentication/logout.md)
	[login_session_check](authentication/login_session_check.md)

	"""
	def test_login(self):
		"""
		[<< Authentication](authentication/README.md)
		# `login` SDK method
		
		The `login` SDK method is used to log in and establish a session with the Gravitas API server
		
		|Attribute|Required|Type|Description|
		|-|-|-|-|
		|`username`|yes|string|Username of the user to be logged in|
		|`password`|yes|string|Password of the user to be logged in|
		
		## Expected return value format
		
		The expected return value format is `bool` to indicate the success or failure of the login.
		
		## Usage
		
		    success = sdk.login(
		        username = 'restuser',
		        password = 'gravitas1234567890'
		    )
		"""
		print("")
		print('`login` method tests')
		print('--------------------')
		path = 'login'
		testdata =	{
			'test' : 'Valid credentials',
			'login': 'restuser',
			'password': 'puppies1234567890',
			'responsecode': 200,
			'responsetext' : """{
				"rows":
					[
						{"FORCE_PWD_CHANGE":false,
						"LAST_ACCT":1,
						"NEXT_PWNED":null,
						"PWD_EXPIRE":"2020-10-23",
						"ROOT":true,
						"USER":"restuser"
						,"USER_ID":2,
						"expired_pwd":false
						}
					],
				"success":true
			}"""
		}
		print(f"Test: `{testdata['test']}`")
		with requests_mock.mock() as m:
			m.post(
				f'{host}/{basepath}/{path}',
				status_code = testdata['responsecode'],
				text = testdata['responsetext']
			)
			assert sdk.login(testdata['login'], testdata['password']) == True
		print('Passed!!!')
		testdata = [
			{
				'test': 'Invalid Credentials',
				'login': 'rest123',
				'password': 'puppies7890',
				'responsecode': 400,
				'exception': "Login error: `invalid credentials`",
				'responsetext' : """{
					"error":"invalid credentials",
					"success":false
				}"""
			},
			{
				'test': 'Expired Password',
				'login': 'rest123',
				'password': 'puppies7890',
				'responsecode': 200,
				'exception': f'Login error: `Password has expired. Please log in with a browser to {host} to change your password`',
				'responsetext' : """{
					"rows":
						[
							{"FORCE_PWD_CHANGE":false,
							"LAST_ACCT":1,
							"NEXT_PWNED":null,
							"PWD_EXPIRE":"2020-07-25",
							"ROOT":true,
							"USER":"restuser"
							,"USER_ID":2,
							"expired_pwd":true
							}
						],
					"success":true
				}"""
			},
			{
				'test': 'Forced Password Reset',
				'login': 'rest123',
				'password': 'puppies7890',
				'responsecode': 200,
				'exception': f'Login error: `Password must be changed. Please log in with a browser to {host} to change your password`',
				'responsetext' : """{
					"rows":
						[
							{"FORCE_PWD_CHANGE":true,
							"LAST_ACCT":1,
							"NEXT_PWNED":null,
							"PWD_EXPIRE":"2020-07-30",
							"ROOT":true,
							"USER":"restuser"
							,"USER_ID":2,
							"expired_pwd":false
							}
						],
					"success":true
				}"""
			},
			{
				'test': 'IP Address Control',
				'login': 'rest123',
				'password': 'puppies7890',
				'responsecode': 400,
				'exception': f'Login error: `user cannot access from this ip address`',
				'responsetext' : """{
					"error":"user cannot access from this ip address",
					"success":false
				}"""
			}
		]
		for row in testdata:
			print(f"Test: `{row['test']}`")
			with requests_mock.mock() as m:
				m.post(
					f'{host}/{basepath}/{path}',
					status_code = row['responsecode'],
					text = row['responsetext']
				)
				with pytest.raises(GravAuthError) as e:
					assert sdk.login(row['login'], row['password'])
				assert f'{e.value}' == row['exception']
			print('Passed!!!')


	def test_login_session_check(self):
		"""
		# `login_session_check` SDK method
		
		The `login_session_check` SDK method is used to check if the current user is logged in and has a session. This is useful to avoid authentication errors.
		
		## Expected return value format

		A tuple with the following information is returned:

		* A boolean that represents whether or not the user is logged in
		* A dictionary with user information (if logged in):
		
		|Attribute|Type|Description|Example|
		|-|-|-|-|
		|`FORCE_PWD_CHANGE`|boolean|Determines if user is forced to change their password|`False`|
		|`LAST_ACCT`|integer|The last account that this user accessed|`1`|
		|`NEXT_PWNED`|??? or `None`|TODO FIXME: get description for this|`None`|
		|`PWD_EXPIRE`|string (formatted as `YYYY-MM-DD` date)|Date that the user's password expires|`2020-10-23`|
		|`ROOT`|boolean|The administrative status of the user|`True`|
		|`USER`|string|The username of the user|`restuser`|
		|`USER_ID`|integer|The user ID number of the user|`2`|
		|`expired_pwd`|boolean|Whether or not the user's password is expired|`False`|

		## Usage

		    status, userdata = sdk.login_session_check()
		"""
		print("")
		print("`login_session_check` method tests")
		print("---------------------")
		print("Test: `login_session_check: logged in`")
		path = 'login'
		with requests_mock.mock() as m:
			m.get(
				f'{host}/{basepath}/{path}',
				status_code = 200,
				reason = 'OK',
				text="""{
					"rows":
						[
							{"FORCE_PWD_CHANGE":true,
							"LAST_ACCT":1,
							"NEXT_PWNED":null,
							"PWD_EXPIRE":"2020-07-30",
							"ROOT":true,
							"USER":"restuser",
							"USER_ID":2,
							"expired_pwd":false
							}
						],
					"success":true
				}"""
			)
			session_check = sdk.login_session_check()
			assert session_check[0] == True
			assert session_check[1]['FORCE_PWD_CHANGE'] == True
			assert session_check[1]['LAST_ACCT'] == 1
			assert session_check[1]['NEXT_PWNED'] == None
			assert session_check[1]['ROOT'] == True
			assert session_check[1]['USER_ID'] == 2
			assert session_check[1]['USER'] == 'restuser'
			assert session_check[1]['expired_pwd'] == False
			print("Passed!!!")
			print("Test: `login_session_check: not logged in`")
			m.get(
				f'{host}/{basepath}/{path}',
				status_code = 200,
				reason = 'OK',
				text="""{
					"rows":	[],
					"success":false
				}"""
			)
			session_check = sdk.login_session_check()
			assert session_check[0] == False
			assert not session_check[1] # dictionary should be empty
		print("Passed!!!")

	def test_logout(self):
		"""
		# `logout` SDK method
		
		The `logout` SDK method is used to perform a logout for the currently logged in user.
		
		## Expected return value format
		
		The expected return value format is `bool` to indicate the success or failure of the logout attempt.
		
		## Usage
		
		    success = sdk.logout()
		"""
		print("")
		print("`logout` method tests")
		print("---------------------")
		print("Test: `logout`")
		path = 'login'
		with requests_mock.mock() as m:
			m.delete(
				f'{host}/{basepath}/{path}',
				status_code = 200,
				reason = 'OK',
				text="""{
					"rows":[],
					"success":true
				}""")
			assert sdk.logout() == True
		print("Passed!!!")

def client():
	print("")
	print("`client` method tests")
	print("----------------------")
	path = 'client'
	testdata = [
		{
			'test': 'Valid Test Data - All Records',
			'method': sdk.READ,
			'fields': [
				'CLIENT_ID',
				'NAME'
			],
			'order': [
				'CLIENT_ID'
			],
			'limit': 100,
			'responsecode': 200,
			'responsetext' : """{
				"rows":[
					{
						"CLIENT_ID":1,
						"NAME":"Wakeups"
					},
					{
						"CLIENT_ID":7,
						"NAME":"Msgs Found During Checks"
					}
				],
				"success":true
			}"""
		}
	]
	for row in testdata:
		print(f"Test: {row['test']}")
		params = {}
		params['fields'] = ','.join(row['fields'])
		params['limit'] = row['limit']
		params['order'] = ','.join(row['order'])
		print(f'{host}/{basepath}/{path}?{urllib.parse.urlencode(params)}')
		with requests_mock.mock() as m:
			m.get(
				f'{host}/{basepath}/{path}?{urllib.parse.urlencode(params)}',
				status_code = row['responsecode'],
				text = row['responsetext'],
				complete_qs = True
			)
		success, data = sdk.client(
			method = row['method'],
			fields = row['fields'],
			order = row['order'],
			limit = 100
		)
		assert success == True
		assert len(data) == 2

#class test_client:
	"""
	# The `clients` SDK method

	The `clients` SDK method is used to get information about clients as well as setting attributes for clients.

	The `clients` SDK also allows for modification of client tickets, contacts, and all other client attributes

	"""

