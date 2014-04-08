import json
from celery import Celery, chain
from tornado.web import RequestHandler
from neo4jrestclient import client
from app.settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from app.utils import filter_dict, dict_to_neo4j_str

# debug__
from time import time
# __debug

celery_app = Celery('tasks', broker=CELERY_BROKER_URL)

TWITTER_FIELDS = ('id', 'name', 'followers_count', 'time_zone', 'utc_offset',)
TWITTER_LABEL = 'TwitterUser'


def get_twitter_user_node(user_id, db):
    """ Returns a neo4j node from a node_id. """
    try:
        return db.labels[TWITTER_LABEL].get(id=user_id)[0]
    except:
        return None


# def get_or_create_twitter_user_node(user_dict, db):
#     """ Returns a neo4j node from a user dict from twitter api response. """
#     user_dict = filter_dict(user_dict, TWITTER_FIELDS)
#     user_node = get_twitter_user_node(user_dict['id'], db)
#     if not user_node:
#         q = 'create (n:{label} {properties}) return n'.format(
#             label=TWITTER_LABEL, properties=dict_to_neo4j_str(user_dict))
#         user_node = db.query(q, returns=(client.Node,))[0][0]
#     return user_node


@celery_app.task
def process_facebook_friends(user_id, friend_list, db):
    pass  # TODO create a chain of processes with friends' likes


@celery_app.task
def process_facebook_likes(user_id, like_list, db):
    pass  # TODO same way twitter? use create unique?


@celery_app.task
def process_twitter_followers(user_id, follower_list, db):
    print 'processing twitter followers'
    user_node = get_twitter_user_node(user_id, db)
    with db.transaction(for_query=True) as _:
        for i in follower_list:
            i = filter_dict(i, TWITTER_FIELDS)
            i_node = get_twitter_user_node(i['id'], db)
            if i_node:
                q = 'start x=node(%s), y=node(%s) create (x)<-[:%s]-(y)' % (
                    user_node.id,
                    i_node.id,
                    'follows')
            else:
                q = 'start x=node(%s) create (x)<-[:%s]-(y:%s %s)' % (
                    user_node.id,
                    'follows',
                    TWITTER_LABEL,
                    dict_to_neo4j_str(i))
            db.query(q)
            print 'TwitterUser node created'


@celery_app.task
def process_twitter_following(user_id, following_list, db):
    print 'processing twitter followings'
    user_node = get_twitter_user_node(user_id, db)
    with db.transaction(for_query=True) as _:
        for i in following_list:
            i = filter_dict(i, TWITTER_FIELDS)
            i_node = get_twitter_user_node(i['id'], db)
            if i_node:
                q = 'start x=node(%s), y=node(%s) create (x)-[:%s]->(y)' % (
                    user_node.id,
                    i_node.id,
                    'follows')
            else:
                q = 'start x=node(%s) create (x)-[:%s]->(y:%s %s)' % (
                    user_node.id,
                    'follows',
                    TWITTER_LABEL,
                    dict_to_neo4j_str(i))
            db.query(q)
            print 'TwitterUser node created'


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
        print 'processing twitter...'
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
