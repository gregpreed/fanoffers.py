import json
from celery import Celery, chain
from tornado.web import RequestHandler
from app.settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from app.utils import filter_dict

# debug__
from time import time
# __debug

celery_app = Celery('tasks', broker=CELERY_BROKER_URL)

TWITTER_FIELDS = ('id', 'name', 'followers_count', 'time_zone', 'utc_offset',)
TWITTER_LABEL = 'TwitterUser'


def get_twitter_user_node(user_id, db):
    """ Returns a neo4j node from a node_id. """
    return db.labels[TWITTER_LABEL].get(id=user_id)


def get_or_create_twitter_user_node(user_dict, db):
    """ Returns a neo4j node from a user dict from twitter api response. """
    user_dict = filter_dict(user_dict, TWITTER_FIELDS)
    user_node = db.labels[TWITTER_LABEL].get(id=user_dict['id'])
    if not user_node:
        user_node = db.node(**user_dict)
        user_node.labels.add(TWITTER_LABEL)
    return user_node


@celery_app.task
def process_facebook_friends(user_id, friend_list, db):
    pass  # TODO create a chain of processes with friends' likes


@celery_app.task
def process_facebook_likes(user_id, like_list, db):
    pass  # TODO same way twitter? use create unique?


@celery_app.task
def process_twitter_followers(user_id, follower_list, db):
    user_node = get_twitter_user_node(user_id, db)
    with db.transaction() as _:
        for i in follower_list:
            i_node = get_or_create_twitter_user_node(i, db)
            i_node.follows(user_node)


@celery_app.task
def process_twitter_following(user_id, following_list, db):
    user_node = get_twitter_user_node(user_id, db)
    with db.transaction() as _:
        for i in following_list:
            i_node = get_or_create_twitter_user_node(i, db)
            user_node.follows(i_node)


class FacebookProcess(RequestHandler):

    def post(self):
        # debug__
        print 'POST'
        print 'processing facebook...'
        _time = time()
        print '  t = 0'
        # __debug

        body = json.loads(self.request.body)
        friend_list = body.get('friend_list', None)
        if friend_list:
            process_facebook_friends.delay(
                body['id'], friend_list, self.application.db)
        like_list = body.get('like_list', None)
        if like_list:
            process_facebook_likes.delay(
                body['id'], like_list, self.application.db)

        # debug__
        print '...done!'
        print '  t =', time() - _time
        # __debug

        self.set_status(204)
        self.finish()


class TwitterProcess(RequestHandler):

    def post(self):
        # debug__
        print 'POST'
        print 'processing facebook...'
        _time = time()
        print '  t = 0'
        # __debug

        body = json.loads(self.request.body)
        follower_list = body.get('follower_list', None)
        if follower_list:
            process_twitter_followers.delay(
                body['id'], follower_list, self.application.db)
        following_list = body.get('following_list', None)
        if following_list:
            process_twitter_following.delay(
                body['id'], following_list, self.application.db)

        # debug__
        print '...done!'
        print '  t =', time() - _time
        # __debug

        self.set_status(204)
        self.finish()
