import json
import os
import time

import endpoints
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError

from settings import ADMINS


def get_user_from_token():
    """A workaround implementation for getting userid."""
    auth = os.getenv('HTTP_AUTHORIZATION')
    bearer, token = auth.split()
    token_type = 'id_token'
    if 'OAUTH_USER_ID' in os.environ:
        token_type = 'access_token'
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?%s=%s'
           % (token_type, token))
    user = {}
    wait = 1
    for i in range(3):
        resp = urlfetch.fetch(url)
        if resp.status_code == 200:
            user = json.loads(resp.content)
            break
        elif resp.status_code == 400 and 'invalid_token' in resp.content:
            url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?%s=%s'
                   % ('access_token', token))
        else:
            time.sleep(wait)
            wait = wait + i
    return user


def LoginAdminRequired(function):
    def _decorated(self, *args, **kwargs):
        try:
            email = get_user_from_token().get('email')
            if not email in ADMINS:
                raise endpoints.UnauthorizedException('You don\'t have permission to access')

        except Exception, e:
            raise endpoints.UnauthorizedException('You don\'t have permission to access')

        return function(self, *args, **kwargs)

    return _decorated


def get_entity_by_websafeKey_key(websafeKey):
    if not websafeKey:
        raise endpoints.BadRequestException("websafeKey field required.")

    try:
        entity = ndb.Key(urlsafe=websafeKey).get()

    except ProtocolBufferDecodeError, e:
        raise endpoints.BadRequestException("websafeKey '%s' error, %s" % (websafeKey, e.message))

    except TypeError, e:
        raise endpoints.BadRequestException("websafeKey '%s' error, %s" % (websafeKey, e.message))

    if not entity:
        raise endpoints.NotFoundException(
                "No Entity found with user id '%s'" % websafeKey)

    return entity