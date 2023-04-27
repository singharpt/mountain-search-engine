import re
import numpy as np
from nltk.corpus import stopwords
from getSolrData import get_results_from_solr, parse_solr_results

def tokenize_doc(doc_text, stop_words):
    # doc_text = doc_text.replace('\n', ' ')
    # doc_text = " ".join(re.findall('[a-zA-Z]+', doc_text))
    # tokens = doc_text.split(' ')
    tokens = []
    text = doc_text
    text = re.sub(r'[\n]', ' ', text)
    text = re.sub(r'[,-]', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub('[0-9]', '', text)
    text = text.lower()
    tkns = text.split(' ')
    tokens = [token for token in tkns if token not in stop_words and token != '' and not token.isnumeric()]
    return tokens

def build_association(id_token_map, vocab, query):
    association_list = []
    for i, voc in enumerate(vocab):
        for word in query.split(' '):
            c1, c2, c3 = 0, 0, 0
            for doc_id, tokens_this_doc in id_token_map.items():
                count0 = tokens_this_doc.count(voc)
                count1 = tokens_this_doc.count(word)
                c1 += count0 * count1
                c2 += count0 * count0
                c3 += count1 * count1
            c1 /= (c1 + c2 + c3)
            if c1 != 0:
                association_list.append((voc, word, c1))

    return association_list

def association_main(query, solr_results):
    stop_words = set(stopwords.words('english'))
    tokens = []
    token_counts = {}
    tokens_map = {}
    document_ids = []

    for result in solr_results:
        tokens_this_document = tokenize_doc(result['content'], stop_words)
        tokens_map[result['rank']] = tokens_this_document
        tokens.append(tokens_this_document)

    vocab = set([token for tokens_this_doc in tokens for token in tokens_this_doc])
    association_list = build_association(tokens_map, vocab, query)
    association_list.sort(key = lambda x: x[2],reverse=True)

    i=1;
    while(i<5):
        query += ' '+str(association_list[i][0])
        i +=1
    return query

def get_documents(solr_results):
    documents = []
    for doc in solr_results:
        if "content" in doc:
            documents.append(doc)
    return documents

#Function start
query = "green moutains"
solr_query_format = "content:({})".format(query)
solr_results = get_results_from_solr(solr_query_format, 500)
solr_results = parse_solr_results(solr_results)
documents = get_documents(solr_results)
expanded_query = association_main(query, documents)
print(expanded_query)