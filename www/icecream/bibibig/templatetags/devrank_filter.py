from json import dumps
from django import template
from sqlalchemy.orm import class_mapper

register = template.Library()

@register.filter(name = 'jsonify')
def jsonify(values):
    json = {}
    for value in values:
        columns = [c.key for c in class_mapper(value.__class__).columns]
        d = dict((c, str(getattr(value, c))) for c in columns)
        d['etag']=d['etag'].replace('"','')
        json.update({d['login']:d})
    return dumps(json)
