import json
from celery import Celery, chain
from tornado.web import RequestHandler
from app.settings import CELERY_BROKER_URL
import app.utils as u
from app.neo4j_namespace import labels

# debug__
from time import time
# __debug


celery_app = Celery('tasks', broker=CELERY_BROKER_URL)


# Desired fields to filter.
TWITTER_FIELDS = (
    'id',
    'name',
    'followers_count',
    'time_zone',
    'utc_offset',)
FACEBOOK_FIELDS = (
    'id',
    'gender',
    'username',
    'hometown',
    'locale',
    'location',)
LIKE_FIELDS = (
    'id',
    'name',)


def get_twitter_user_node(id_, db):
    return u.get_node(id_, db, labels['twitter_user'])


def get_facebook_user_node(id_, db):
    return u.get_node(id_, db, labels['facebook_user'])


def get_facebook_like_node(id_, db):
    return u.get_node(id_, db, labels['facebook_like'])


@celery_app.task
def process_facebook_likes(id_, list_, db, is_node_id=False, *kwargs):
    """
    Parse and save facebook likes.
    id_: facebook user id if is_node_id is equal to False, node id otherwise.
    """
    if not is_node_id:
        id_ = get_facebook_user_node(id_, db).id
    with db.transaction(for_query=True) as _:
        for i in list_:
            i = u.filter_dict(i, LIKE_FIELDS)
            db.query(u.get_relation_query(
                node_0_id=id_,
                node_1=get_facebook_like_node(i['id'], db),
                label=labels['facebook_like'],
                rel='likes',
                properties=i))


@celery_app.task
def process_facebook_friends(user_id, list_, db):
    """
    Parse and save facebook friends. Create a chain of processes for friends'
    likes
    """
    print 'process_facebook_friends'
    id_ = get_facebook_user_node(user_id, db).id
    gender_nodes = u.get_gender_nodes(db)
    likes_chain = []
    with db.transaction(for_query=True) as _:
        for i in list_:
            try:
                like_list = i.pop('likes')
            except KeyError:
                friend_node = None
            else:
                friend_node = get_facebook_user_node(i['id'], db)
                if friend_node:
                    likes_chain.append(process_facebook_likes.s(
                        friend_node.id, like_list, db, True))
                else:
                    likes_chain.append(process_facebook_likes.s(
                        i['id'], like_list, db))
            i = u.filter_dict(i, FACEBOOK_FIELDS)

            # Attribute nodes.
            # Some attributes requires a creation of new nodes (eg. location).
            # Some attributes assume the nodes already exists (eg. gender).
            if 'locale' in i:
                locale = i.pop('locale')
                db.query(u.get_relation_query(
                    node_0_id=id_,
                    node_1=u.get_locale_node(locale, db),
                    label=labels['locale'],
                    rel='has_locale',
                    properties={'name': locale}))
            gender = i.get('gender')
            if gender in gender_nodes.keys():
                gender = i.pop('gender')
                q = 'start x=node(%s),y=node(%s) create (x)-[:%s]->(y)' % (
                    id_,
                    gender_nodes[gender].id,
                    'has_gender')
                db.query(q)

            # Facebook user node.
            db.query(u.get_relation_query(
                node_0_id=id_,
                node_1=friend_node or get_facebook_user_node(i['id'], db),
                label=labels['facebook_user'],
                rel='friend_of',
                properties=i))

    if likes_chain:
        chain(likes_chain).delay()


@celery_app.task
def process_twitter_followers(user_id, list_, db):
    print 'processing twitter followers...'
    id_ = get_twitter_user_node(user_id, db).id
    with db.transaction(for_query=True) as _:
        for i in list_:
            i = u.filter_dict(i, TWITTER_FIELDS)
            db.query(u.get_relation_query(
                node_0_id=id_,
                node_1=get_twitter_user_node(i['id'], db),
                label=labels['twitter_user'],
                rel='follows',
                properties=i,
                dir='rl'))


@celery_app.task
def process_twitter_following(user_id, list_, db):
    print 'processing twitter followings'
    id_ = get_twitter_user_node(user_id, db).id
    with db.transaction(for_query=True) as _:
        for i in list_:
            i = u.filter_dict(i, TWITTER_FIELDS)
            db.query(u.get_relation_query(
                node_0_id=id_,
                node_1=get_twitter_user_node(i['id'], db),
                label=labels['twitter_user'],
                rel='follows',
                properties=i))


class FacebookProcess(RequestHandler):

    def post(self):
        body = json.loads(self.request.body)
        friend_list = body.get('friend_list', None)
        if friend_list:
            process_facebook_friends.delay(
                body['id'], friend_list, self.application.db)
        like_list = body.get('like_list', None)
        if like_list:
            process_facebook_likes.delay(
                body['id'], like_list, self.application.db)
        self.set_status(204)
        self.finish()


class TwitterProcess(RequestHandler):

    def post(self):
        body = json.loads(self.request.body)
        follower_list = body.get('follower_list', None)
        if follower_list:
            process_twitter_followers.delay(
                body['id'], follower_list, self.application.db)
        following_list = body.get('following_list', None)
        if following_list:
            process_twitter_following.delay(
                body['id'], following_list, self.application.db)
        self.set_status(204)
        self.finish()
