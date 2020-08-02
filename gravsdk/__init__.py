import sys
from typing import *
import requests
import json
from urllib.parse import urlparse

from gravsdk import gravcrud

class GravError(Exception):
	"""
	# Exception Class: `GravError`
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
	# Exception Class: `GravAuthError`
	
	The `GravAuthError` exception class is raised when invalid credentials are used or response received from the API is missing data
	
	|Attribute|Type|Description|
	|-|-|-|
	|`responsetext`|str|Descriptive text of the failed authentication attempt|
	
	## Usage:
	
	    raise GravAuthError('No user data received')
	"""
	def __init__(self, responsetext: str):
		self.message = f"Login error: `{responsetext}`"
		super().__init__(self.message)

class GravGeneralError(Exception):
	"""
	# Exception Class: GravGeneralError

	The `GravGeneralError` exception class is raised when general non-specific errors occur, such as passing an incorrectly typed variable or other user mistakes occur.

	|Attribute|Type|Description|
	|-|-|-|
	|`responsetext`|str|Descriptive text of the error encountered|
	
	## Usage:
	
	    raise GravGeneralError('Invalid method specified: sdk.PUPPIES')

	"""
	def __init__(self, responsetext: str):
		self.message = f"General error: `{responsetext}`"
		super().__init__(self.message)

class sdkv1:

	def __init__(self, hoststring: str, ssl_verify_enable: bool = True):
		try:
			self.hostparts = urlparse(
				hoststring
			)
		except Exception as e:
			raise GravError(
				f'invalid url specified: `{e}`'
			)
		self.ssl_verify_enable = ssl_verify_enable
		self.protocol = self.hostparts.scheme
		#TODO FIXME: make this cleaner with enum
		if self.protocol == 'https':
			self.CRUD = gravcrud.HTTPCRUD(
				self.hostparts.geturl(),
				self.ssl_verify_enable,
			)
		#elif self.protocol == 'wss':
		#	self.CRUD = gravcrud.WSCRUD(
		#		self.hostparts.geturl(),
		#		self.ssl_verify_enable
		#	)
		else:
			raise GravError(
				'invalid protocol specified, must be `https` or `wss`'
			)

	def _login_sanity_check(self, result: bool, responsedata: Dict[str, str]) -> bool:
		if not result:
			raise GravAuthError(
				'Invalid API data received'
			)
		try:
			success = responsedata[
				'success'
			]
		except KeyError:
			raise GravAuthError(
				'api response missing `success` key'
			)
		if not success and 'error' in responsedata:
			# API authentication call was not successful
			raise GravAuthError(
				responsedata['error']
			)
		if not success:
			return False
		return True
	
	def login_session_check(self) -> Tuple[bool,Dict[str,str]]:
		result, responsedata = self.CRUD.read(
			'login',
			{}
		)
		if not self._login_sanity_check(result, responsedata):
			return False, {}
		if len(responsedata['rows']) == 0:
			return False, {}
		else:
			return True, responsedata['rows'][0]
		
	
	def login(self, username: str, password: str) -> bool:
		payload = {
			'USER' : username,
			'PASSWORD' : password
		}
		result, responsedata = self.CRUD.create(
			'login',
			payload
		)
		if not self._login_sanity_check(result, responsedata):
			return False
		if 'rows' not in responsedata:
			# For some reason we didn't receive any info for the user
			raise GravAuthError(
				'No user data received'
			)
		rows = responsedata['rows'][0]
		force_pwd_change = rows.get(
			'FORCE_PWD_CHANGE',
			False
		)
		if force_pwd_change:
			# Password must be changed
			raise GravAuthError(
				f'Password must be changed. Please log in with a browser to https://{self.hostparts.netloc} to change your password'
			)
		if rows['expired_pwd']:
			# Password has expired
			raise GravAuthError(
				f'Password has expired. Please log in with a browser to https://{self.hostparts.netloc} to change your password'
			)
		#TODO FIXME: deal with other scenarios
		return True

	def logout(self) -> bool:
		result, responsedata = self.CRUD.delete(
			'login',
			{}
		)
		if not self._login_sanity_check(result, responsedata):
			return False
		return True
	
	def client ( self, client_id: int = 0 ): #TODO FIXME: Need return type
		return sdkv1client ( self, client_id )


class sdkv1client:
	def __init__ ( self, sdk: sdkv1, client_id: int ) -> None:
		self.sdk = sdk
		self.client_id = client_id
	
	def listing(self, limit: int = 9999) -> Tuple[bool,Dict[str,str]]:
		uri = '/rest/OE_CLIEN'
		params = {
			'limit' : limit
		}
		if self.client_id != 0:
			params['filter'] = f'CLIENT_ID={self.client_id}'
		else:
			# To limit spamming the API for large amounts of data
			params['fields'] = 'CLIENT_ID,NAME'
		return self.sdk.CRUD.read ( uri, params )

	def orders(self): 
		return sdkv1endpoint(
			self.sdk,
			f'/rest/client/{self.client_id}/ORDERS'
		)

	def contacts(self): #TODO FIXME: Need return type
		return sdkv1endpoint(
			self.sdk,
			f'/rest/client/{self.client_id}/PT_CONTC'
		)


class sdkv1endpoint:
	def __init__(self, sdk: sdkv1, endpoint: str) -> None:
		self.sdk = sdk
		self.endpoint = endpoint
	
	"""
	sdkv1endpoint can be used by many methods for CRUD operations
	"""
	def search(self, *, fields: Optional[Sequence[str]] = None, limit: int = 100, offset: int = 0, filter: Optional[Dict[str,str]] = None) -> Tuple[bool,Dict[str,str]]:
		params: Dict[str,str] = {}
		if limit:
			params['limit'] = limit
		if offset:
			params['offset'] = offset
		if fields:
			params['fields'] = ','.join ( fields )
		if filter:
			params['filter'] = ','.join ( f'{k}={v!r}' for k, v in filter.items() )
		opresult = self.sdk.CRUD.read(
			self.endpoint,
			params
		)
		return opresult


# sdk.client().listing()
# sdk.client ( 123 ).orders().search ( ... )
# aggreko = sdk.client ( 709 )
# aggreko.orders().search
# aggreko.pt_hist().update ( )