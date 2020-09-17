from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

def link_entity(entity, entity_type):
    sparql.setQuery(
        """
        SELECT distinct *
        
        WHERE { 
        
        ?entity rdfs:label ?name
        FILTER (contains(?name, "%s"))
        
        }
        
        LIMIT 100
        """ % (entity)
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