from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

def link_entity(entity, entity_type, limit=100):
    sparql.setQuery(
        """
        SELECT distinct *
        
        WHERE { 
        
        ?entity rdfs:label ?name
        FILTER (contains(?name, "%s"))
        
        }
        
        LIMIT %d
        """ % (entity, limit)
    )

    d = {}
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            d[result["entity"]["value"]] = result["name"]["value"]
    except Exception as e:
        print(e)

    return d

def entity_relate_object(entity):
    sparql.setQuery(
        """
        SELECT distinct *
        
        WHERE { 
                
        <%s> ?predicate ?object
                
        }
        """ % (entity)
    )

    d = {}
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            object_type = result["object"]["type"]
            object_value = result["object"]["value"]
            if object_type != 'uri' and len(object_value) < 100:
                d[result["predicate"]["value"]] = object_value
    except Exception as e:
        print(e)

    return d
