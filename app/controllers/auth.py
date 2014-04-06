import json
from tornado.web import RequestHandler
from tornado.gen import coroutine
from tornado.auth import FacebookGraphMixin, _auth_return_future
# from neo4jrestclient.query import Q


class FacebookAuth(RequestHandler, FacebookGraphMixin):
    """
    Facebook authentication from access token. This class does not manage the
    obtention of the access token, needs to be provided as an argument.
    """

    DB_FIELDS = (
        'id',
        'first_name',
        'last_name',
        'name',
        'username',
        'email',
        'picture',
        'likes',
        'friends',
    )

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
            user['picture'] = user['picture']['data']['url']
            users = self.application.db.labels.get('User')
            try:
                db_user = users.get(facebookId=user['id'])[0]
            except IndexError:
                db_user = None
            user_ = dict((k, v) for k, v in user.items()
                         if k in self.DB_FIELDS)
            user_['facebookId'] = user_.pop('id')
            if not db_user:
                user_['registered'] = True
                self.process_friends_and_likes(user_)
                db_user = self.application.db.node(**user_)
                db_user.labels.add('User')
                # TODO send to async function the creation of likes and friends.

            elif not db_user.get('registered', False):
                user_['registered'] = True
                self.process_friends_and_likes(user_)
                db_user.properties = user_

            fields = (
                'id',
                'name',
                'username',
                'email',
                'picture',
            )
            user = dict((k, v) for k, v in user.items() if k in fields)
            self.json_write(json.dumps(user))
        self.finish()

    @_auth_return_future
    def get_authenticated_user(self, session, callback):
        # Assume the token received is ok, user will be None otherwise.
        self.facebook_request(
            path='/me',
            callback=self.async_callback(
                self._on_get_user_info, callback, session, self.DB_FIELDS),
            access_token=session['access_token'],
            fields=','.join(self.DB_FIELDS)
        )

    def process_friends_and_likes(self, user):
        try:
            friends = user.pop('friends')['data']
        except KeyError, AttributeError:
            friends = None
        try:
            likes = user.pop('likes')['data']
        except KeyError, AttributeError:
            likes = None
        # TODO

    # def create_user(self, user, register=False):
    #     if friends:
    #         print 'looping friends'
    #         for friend in friends:
    #             db_friend = self.get_user_from_db(friend['id'])
    #             if not db_friend:
    #                 print 'friend not in db'
    #                 friend = {'id': friend['id'],
    #                           'name': friend['name']}
    #                 db_friend = self.create_user(friend)
    #             db_friend.relationships.create('friend_of', db_user)
    #     if likes:
    #         for like in likes:
    #             db_like = self.get_or_create_like(like)
    #             db_user.relationships.create('likes', db_like)
    #     return db_user

    # def get_or_create_like(self, like):
    #     try:
    #         likes = self.application.db.labels.get('Like')
    #     except KeyError:
    #         db_like = None
    #     else:
    #         db_like = likes.get(id=like['id'])
    #     if not db_like:
    #         db_like = self.application.db.node(**like)
    #         db_like.labels.add('Like')
    #     return db_like

    def json_write(self, chunk):
        self.set_header('Content-Type', 'application/json')
        self.write(chunk)
