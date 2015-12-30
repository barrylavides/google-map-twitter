import os

ENV = {
	'DEBUG': os.environ['DEBUG'],
	'HOST': os.environ['HOST'],
	'PORT': int(os.environ['PORT']),
	'CONSUMER_KEY': os.environ['CONSUMER_KEY'],
	'CONSUMER_SECRET': os.environ['CONSUMER_SECRET'],
	'ACCESS_TOKEN_KEY': os.environ['ACCESS_TOKEN_KEY'],
	'ACCESS_TOKEN_SECRET': os.environ['ACCESS_TOKEN_SECRET']
} 