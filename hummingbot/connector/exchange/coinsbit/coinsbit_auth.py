import base64
import hashlib
import hmac
import json
from typing import Any, Dict
from urllib.parse import urlencode

from hummingbot.core.web_assistant.auth import AuthBase
from hummingbot.core.web_assistant.connections.data_types import RESTMethod, RESTRequest


class CoinsbitAuth(AuthBase):
    def __init__(self, api_key, secret_key, websocket_token) -> None:
        self.api_key = api_key
        self.secret_key = secret_key
        self.websocket_token = websocket_token

    async def rest_authenticate(self, request: RESTRequest) -> RESTRequest:
        """
        Adds the server time and the signature to the request, required for authenticated interactions. It also adds
        the required parameter in the request header.
        :param request: the request to be configured for authenticated interaction
        """
        headers = {}
        if request.headers is not None:
            headers.update(request.headers)

        if request.method == RESTMethod.POST:
            headers.update(self.header_for_authentication(params=json.loads(request.data)))
        else:
            headers.update(self.header_for_authentication(params=request.data))
        request.headers = headers

        return request

    def _generate_signature(self, params: Dict[str, Any]):
        encoded_params_str = urlencode(params)
        digest = hmac.new(self.secret_key.encode("utf8"), encoded_params_str.encode("utf8"), hashlib.sha256).hexdigest()
        return digest

    def header_for_authentication(self, params: Dict[str, Any]) -> Dict[str, Any]:
        payload = base64.b64encode(params)
        headers = {
            'X-TXC-APIKEY': self.api_key,
            'X-TXC-PAYLOAD': payload,
            'X-TXC-SIGNATURE': self._generate_signature(params)
        }
        return headers
