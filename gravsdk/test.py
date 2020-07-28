# This file is intended for use with pytest
# Usage: pytest -sx test.py
import configparser
import pytest
from gravsdk import sdkv1, GravAuthError
import requests_mock

host = 'https://127.0.0.1:443'
basepath = 'rest'

sdk = sdkv1 (
	host,
	False,
)

def test_login():
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


def test_logout():
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
