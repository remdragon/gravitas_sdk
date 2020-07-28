"""
Gavitas CRUD library
"""
import sys
from typing import *
from typing import Optional as Opt
import json

class GravJSONValueError(Exception):
	"""# Exception Class: GravJSONValueError
	
	Exception raised for invalid API responses. All API responses are expected to be JSON parseable, so if a response is received that is not this exception is thrown
	
	|Attributes|Description|
	|-|-|
	|responsetext|The full response provided by the API|
	
	## Usage:
	    raise GravJSONValueError(req.text)
	"""
	def __init__(self, responsetext):
		self.message = f"Response is not valid JSON: `{responsetext}`"
		super().__init__(self.message)

class HTTPCRUD(object):
	"""
	HTTP API CRUD interface
	"""
	def __init__(self, host: str, ssl_verify_enable: bool, testmode: bool = False) -> None:
		import requests
		self.testmode = testmode
		self.host = host
		self.ssl_verify_enable = ssl_verify_enable
		self.session = requests.Session()
	
	def _request ( self,
		method: Callable[...,Any],
		endpoint: str,
		*,
		params: Opt[Dict[str,str]] = None,
		json_body: Opt[Dict[str,str]] = None,
		txt_method: str = '',
		json_response: Dict[str,str] = {}
	) -> Tuple[bool,Dict[str,str]]:
		uri = f'{self.host}/rest/{endpoint}'
		if self.testmode:
			import requests_mock # pip install requests_mock
			adapter = requests_mock.Adapter()
			self.session.mount('https://', adapter)
			adapter.register_uri(txt_method, uri, text = json.dumps(json_response))
		req = method ( uri, params = params, json = json_body, verify = self.ssl_verify_enable, testmode = self.testmode )
		try:
			responsedata = req.json()
		except (ValueError):
			raise GravJSONValueError (
				req.text
			)
		return True, responsedata
	
	def create(self, endpoint: str, params: dict, testmode: bool, testresponse: Dict[str,str]) -> Tuple[bool,Dict[str,str]]:
		return self._request ( self.session.post, endpoint, json_body = params )
	
	def read(self, endpoint: str, params: dict, testmode: bool, testresponse: Dict[str,str]) -> Tuple[bool,Dict[str,str]]:
		return self._request ( self.session.get, endpoint, params = params )
	
	def update(self, endpoint: str, params: dict, testmode: bool, testresponse: Dict[str,str]) -> Tuple[bool,Dict[str,str]]:
		return self._request ( self.session.patch, endpoint, json_body = params )

	def delete(self, endpoint: str, params: dict, testmode: bool, testresponse: Dict[str,str]) -> Tuple[bool,Dict[str,str]]:
		return self._request ( self.session.delete, endpoint, params = params )

"""
class WSCRUD(object):
	# TODO FIXME: write this whole class
	def __init__(self, host:, ssl_verify_enable: bool = True):
		import asyncio
		import websockets # pip install websockets
		self.host = host
		self.port = port
		self.ssl_verify_enable = ssl_verify_enable
		asyncio.get_event_loop().run_until_complete(
			self.connect(f'wss://{self.host}', 'hello')
		)

	async def connect(self, hoststr, xmit):
		async with websockets.connect(hoststr) as websocket:
			await websocket.send(xmit)
			await websocket.recv()
"""
