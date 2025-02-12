import json
import urllib
import urllib.request
import urllib.error
from urllib.parse import urljoin, urlencode
import ssl


class Http(object):
    def __init__(self, version, url, debug=False):
        self.version = version
        self.url = url
        self._debug = debug

    def _call_server(self, url, post_data):
        if not url:
            response = dict(error=True, message='AttributeError: Bad URL')
            return json.dumps(response)
        data = urlencode(post_data)
        request = urllib.request.Request(url, data.encode())
        context = ssl._create_unverified_context()
        try:
            res = urllib.request.urlopen(request, context=context)
        except urllib.error.HTTPError as e:
            headers = e.headers if self._debug else ''
            response = dict(
                error=True,
                message='HTTPError: {0} {1} {2}'.format(e.code, e.reason, headers),
            )
            response = json.dumps(response)
        except urllib.error.URLError as e:
            response = dict(error=True, message='URLError: {0}'.format(e.reason))
            response = json.dumps(response)
        else:
            response = res.read()
        return response

    def request(self, api_name, data):
        path = '{version}/{api_name}'.format(version=self.version, api_name=api_name)
        response = self._call_server(urljoin(self.url, path), data)
        try:
            response = json.loads(response)
        except ValueError as e:
            response = dict(error=True, message=repr(e))
        return response

    def post(self, url, data):
        response = self._call_server(url, data)
        try:
            response = json.loads(response)
        except ValueError as e:
            response = dict(error=True, message=repr(e))
        return response
