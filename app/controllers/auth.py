import json
from tornado.web import RequestHandler
from tornado.gen import coroutine
from tornado.auth import FacebookGraphMixin, _auth_return_future


class FacebookAuth(RequestHandler, FacebookGraphMixin):
    """
    Facebook authentication from access token. This class does not manage the
    obtention of the access token, needs to be provided as an argument.
    """

    @coroutine
    def get(self):
        session = {
            'access_token': self.get_argument('access_token'),  # 400 if missed
            'expires': self.get_argument('expires', None)
        }
        user = yield self.get_authenticated_user(session)
        if not user:
            self.set_status(400, 'access_token invalid or expired')
        else:
            fields = (
                'id',
                'name',
                'email',
                'picture',
            )
            self.json_write(json.dumps(user.fromkeys(fields)))
        self.finish()

    @_auth_return_future
    def get_authenticated_user(self, session, callback):
        fields = (
            'id',
            'name',
            'email',
            'picture',
            'likes',
            'friends',
        )
        # Assume the token received is ok, user will be None otherwise.
        self.facebook_request(
            path='/me',
            callback=self.async_callback(
                self._on_get_user_info, callback, session, fields),
            access_token=session['access_token'],
            fields=','.join(fields)
        )

    def json_write(self, chunk):
        self.set_header('Content-Type', 'application/json')
        self.write(chunk)
