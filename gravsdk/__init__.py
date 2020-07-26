import sys
from typing import *
import requests
import json

from gravsdk import gravcrud

class GravError(Exception):
	"""
	# Exception Class: GravError
	Exception raised for general SDK errors
	
	|Attribute|Description|
	|-|-|
	|`responsetext`|Descriptive text of the error|
	"""
	def __init__(self, responsetext: str):
		self.message = f"API error: `{responsetext}`"
		super().__init__(self.message)

class GravAuthError(Exception):
	"""
	# Exception Class: GravAuthError
	
	The GravAuthError exception class is raised when invalid credentials are used or response received from the API is missing data
	
	|Attribute|Type|Description|
	|-|-|-|
	|`responsetext`|str|Descriptive text of the failed authentication attempt|
	
	## Usage:
	
	    raise GravAuthError('No user data received')
	"""
	def __init__(self, responsetext: str):
		self.message = f"Login error: `{responsetext}`"
		super().__init__(self.message)

class sdkv1(object):
	"""
	# Gravitas Python SDK v1
	This is version 1 of the gravitas SDK. This includes legacy/compatibility implementation of Gravitas.
	
	|Attribute|Required|Type|Description|
	|-|-|-|-|
	|`host`|Required|string|Hostname of the Gravitas API server|
	|`protocol`|Optional|string|Protocol used for communication with the Gravitas API server. Options are `https` and `wss` (defaults to `https`).
	|`port`|Optional|integer|Port number of the Gravitas API server (defaults to `443`)|
	|`ssl_verify_enable`|Optional|boolean|Enables/disables SSL certificate verification (defaults to `True`). **NOTE: in production this must remain as `True`**
	
	## Usage
	
	    from gravsdk import sdkv1
	    sdk = sdkv1(
	        host = '10.10.10.10',
	        port = 4443,
	        ssl_verify_enable = False
	    )
	"""
	def __init__(self, host: str, protocol: str = 'https', port: int = 443, ssl_verify_enable: bool = True):
		self.host = host
		self.port = port
		self.ssl_verify_enable = ssl_verify_enable
		self.protocol = protocol
		self.loggedin = False
		self.userdata = {}
		#TODO FIXME: make this cleaner with enum
		if self.protocol == 'https':
			self.CRUD = gravcrud.HTTPCRUD(
				self.host,
				self.port,
				self.ssl_verify_enable
			)
		elif self.protocol == 'wss':
			self.CRUD = gravcrud.WSCRUD(
				self.host,
				self.port,
				self.ssl_verify_enable
			)
		else:
			raise GravError('invalid protocol specified, must be `https` or `wss`')

	def _login_sanity_check(self, result: bool, responsedata: Dict[str, str]) -> bool:
		if not result:
			raise GravAuthError('Invalid API data received')
			return False
		try:
			success = responsedata['success']
		except KeyError:
			raise GravAuthError ( 'api response missing `success` key' )
		if not success:
			# API authentication call was not successful
			raise GravAuthError(responsedata['error'])
			return False
		return True
	
	def _login_session_check(self) -> Tuple[bool,Dict[str,str]]:
		result, responsedata = self.CRUD.read('login', {})
		if not self._login_sanity_check(result, responsedata):
			return False, responsedata
		if len(responsedata['rows']) == 0:
			return False, responsedata
		else:
			return True, responsedata
		
	
	def login(self, username: str, password: str) -> None:
		"""
		# `login` SDK method
		
		The `login` SDK method is used to log in and establish a session with the Gravitas API server
		
		|Attribute|Required|Type|Description|
		|-|-|-|-|
		|`username`|yes|string|Username of the user to be logged in|
		|`password`|yes|string|Password of the user to be logged in|
		
		## Expected return value format
		
		The expected return value format is `None`.
		* The class variable `loggedin` is the success (`True`) or failure ('False`) of the login request
		* If the login is successful then the class variable `userdata` is a dictionary of the user attributes provided by the API:
		
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
		
		    sdk.login(
		        username = 'restuser',
		        password = 'gravitas1234567890'
		    )
		    print(sdk.loggedin)
		    print(sdk.userdata)
		"""
		result, responsedata = self._login_session_check()
		if result:
			# We're already logged in, just return results from session check
			self.loggedin = result
			self.userdata = responsedata['rows'][0]
			return
		payload = {
			'USER' : username,
			'PASSWORD' : password
		}
		result, responsedata = self.CRUD.create('login', payload)
		if not self._login_sanity_check(result, responsedata):
			self.loggedin = False
			self.userdata = {}
			return
		if 'rows' not in responsedata:
			# For some reason we didn't receive any info for the user
			raise GravAuthError('No user data received')
			self.loggedin = False
			self.userdata = {}
			return
		rows = responsedata['rows'][0]
		force_pwd_change = rows.get ( 'FORCE_PWD_CHANGE', False )
		if force_pwd_change:
			# Password must be changed
			raise GravAuthError(f'Password must be changed. Please log in with a browser to https://{self.host}:{self.port} to change your password')
			self.loggedin = False
			self.userdata = {}
			return
		if rows['expired_pwd']:
			# Password has expired
			raise GravAuthError(f'Password has expired. Please log in with a browser to https://{self.host}:{self.port} to change your password')
			self.loggedin = False
			self.userdata = {}
			return
		#TODO FIXME: deal with other scenarios
		self.loggedin = True
		self.userdata = responsedata['rows'][0]
		return

	def logout(self) -> None:
		"""
		# `logout` SDK method
		
		The `logout` SDK method is used to perform a logout for the currently logged in user.
		
		## Expected return value format
		
		The expected return value format is `Tuple[bool, Dict[str,str]]`.
		* The resulting tuple's first position is the success (`True`) or failure ('False`) of the logout request
		* The resulting tuple's second position will always be a dictionary with a `rows` element that is an empty array.
		
		## Usage
		
		    sdk.logout()
		"""
		if self._login_session_check():
			result, responsedata = self.CRUD.delete('login', {})
			if not self._login_sanity_check(result, responsedata):
				return
			self.loggedin = False
			self.userdata = {}
			return
		else:
			# If we're already logged out there's no need to do it again, return defaults
			self.loggedin = False
			self.userdata = {}
			return