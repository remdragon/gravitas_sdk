from distutils.core import setup

setup(
	name = 'gravsdk',
	packages = ['gravsdk'],
	version = '0.0.2',
	install_requires = [
		'websockets'
	],
	description = 'Python SDK for accessing the Gravitas call center environment API',
	author = 'joshpatten',
	author_email = 'joshpatten@gmail.com',
	url = 'https://github.com/remdragon/gravitas_sdk.git',
	download_url = 'https://github.com/remdragon/gravitas_sdk.git/tarball/master',
	keyworks = ['gravitas', 'sdk', 'api'],
	classifiers = [],
)
