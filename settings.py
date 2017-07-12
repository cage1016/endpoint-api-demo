# coding: utf-8

__author__ = 'cage'

import os
import logging
import endpoints

if os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
    DEBUG = True

else:
    DEBUG = False

logging.info("Starting application in DEBUG mode: %s", DEBUG)

# endpoint api
if DEBUG:
    API_ROOT = 'http://localhost:8080/_ah/api'
    HOST = 'http://localhost:8080'

else:
    API_ROOT = 'https://<your-project-id>.appspot.com/_ah/api'
    HOST = 'https://<your-project-id>.appspot.com'

CLIENT_ID = '<GCP_CLIENT_ID>'
CLIENT_SECRET = '<GCP>_CLIENT_SECRET'

DEVELOPER_KEY = '<GCP_DEVELOPER_KEY>'

ADMINS = [
    # admin email
    "cage.chung@gmail.com"
]

books_api = endpoints.api(name='dummy',
                         version='v1',
                         description='dummy API',
                         allowed_client_ids=[CLIENT_ID,
                                             endpoints.API_EXPLORER_CLIENT_ID],
                         scopes=[endpoints.EMAIL_SCOPE])
