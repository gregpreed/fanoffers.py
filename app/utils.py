import json
import re
from app.neo4j_namespace import labels


def filter_dict(d, fields):
    return dict((k, v) for k, v in d.items() if k in fields)


def dict_to_neo4j_str(d):
    return re.sub(r'\"(.*?)\":', r'\1:', json.dumps(d))


def get_relation_query(node_0_id, node_1, rel, label, properties, d='lr'):
    """
    Returns a cypher query that relates node_0 and node_1. If node_1 is None,
    this will be created as well as the relationship, if node_1 is a node just
    the relationship will be created.
    rel: relationship name
    label: node label name
    properties: dict with node_1 properties in case node_1 is None
    dir: relationship direction (lr: left to right)
    """
    try:
        assert(d in ['lr', 'rl'])
    except AssertionError:
        raise Exception('Paramenter "d" must be either "lr" or "rl"')

    if node_1:
        print 'node already exists'
        if d == 'lr':
            q = 'start x=node(%s), y=node(%s) create (x)-[:%s]->(y)' % (
                node_0_id,
                node_1.id,
                rel)
        else:
            q = 'start x=node(%s), y=node(%s) create (x)<-[:%s]-(y)' % (
                node_0_id,
                node_1.id,
                rel)
    else:
        print 'creating new node'
        if d == 'lr':
            q = 'start x=node(%s) create (x)-[:%s]->(y:%s %s)' % (
                node_0_id,
                rel,
                label,
                dict_to_neo4j_str(properties))
        else:
            q = 'start x=node(%s) create (x)<-[:%s]-(y:%s %s)' % (
                node_0_id,
                rel,
                label,
                dict_to_neo4j_str(properties))
    print q
    return q


def get_node(id_, db, label=None):
    """
    Returns a neo4j node from a id properties (not node id!).
    Faster results if label is provided.
    """
    try:
        if label:
            return db.labels[label].get(id=id_)[0]
        else:
            return db.get(id=id_)[0]
    except:
        return None


def get_gender_nodes(db):
    return dict((i['name'], i) for i in db.labels[labels['gender']].get())


def get_locale_node(name, db):
    try:
        return db.labels[labels['locale']].get(name=name)[0]
    except:
        return None
