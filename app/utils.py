import json
import re


def filter_dict(d, fields):
    return dict((k, v) for k, v in d.items() if k in fields)


def dict_to_neo4j_str(d):
    return re.sub(r'\"(.*?)\":', r'\1:', json.dumps(d))
