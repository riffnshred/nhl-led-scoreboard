import fastjsonschema
import os
import json

def validateConf(confpath,schemapath):

    # Validate a JSON config file (config.json) with JSON scema (config.schema.json).
    conf = {}
    schema = {}
    
    if os.path.isfile(confpath) and os.path.isfile(schemapath):
        try:
            conf = json.load(open(confpath))
            schema = json.load(open(schemapath))
        except json.decoder.JSONDecodeError as e:
            return False,"invalid json error: {0}".format(e)

    else:
        return False,"unable to load {0} or {1}".format(confpath,schemapath)

    validator = fastjsonschema.compile(schema)
    try:
        validator(conf)
    except fastjsonschema.JsonSchemaException as e:
        msg = e.message
        return False, msg
    else:
        return True, "validate %s pass" % confpath