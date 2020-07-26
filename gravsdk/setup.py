from distutils.core import setup

setup(
	name = 'gravitas_sdk',
	packages = ['gravitas_sdk'],
	version = '0.0.1',
	install_requires = [
		'websockets'
	]
	description = 'Python SDK for accessing the Gravitas call center environment API',
	author = 'joshpatten',
	author_email = 'joshpatten@gmail.com',
	url = 'https://github.com/remdragon/gravitas_sdk.git',
	download_url = 'https://github.com/remdragon/gravitas_sdk.git/tarball/master',
	keyworks = ['gravitas', 'sdk', 'api'],
	classifiers = [],
)
