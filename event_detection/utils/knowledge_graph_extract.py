import spacy
nlp = spacy.load("en_core_web_sm") #en_core_web_sm
from event_detection.utils import text_utils

def extract_entity_relation_sent(text):
    doc = nlp(text.strip())
    
    objects = set()
    head_entity = ''
    tail_entity = ''
    relation = ''
    
    name_entities = set([str(ent) for ent in doc.ents])
    
    for tok in doc:
        for ent in name_entities:
            if tok.text in ent:
                if 'ubj' in tok.dep_:
                    head_entity = ent
                if 'obj' in tok.dep_:
                    tail_entity = ent
                
        if tok.dep_ == 'ROOT' and tok.pos_ == 'VERB':
            relation = str(tok.text)
    
    if head_entity != '' and tail_entity != '' and relation != '':
        return (head_entity, relation, tail_entity)
    else:
        return None

def extract_entity(text):
    sents = text.split('.')
    triple_list = []
    for sent in sents:
        triple = extract_entity_relation_sent(sent)
        if triple != None:
            triple_list.append(triple)
            
    return triple_list

def extract_triples(tweet_list):
    knowledge_graph_dict = {}
    for tweet in tweet_list:
        text = text_utils.pre_process(tweet.text)
        triple_list = extract_entity(text)
        if len(triple_list) > 0:
            knowledge_graph_dict[tweet.tweet_id] = (tweet.text, triple_list, tweet.created_at.strftime("%Y/%m/%d, %H:%M:%S"))

    return knowledge_graph_dict