# import logging, sys
# logging.disable(sys.maxsize)

import lucene
import os
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import MultiFieldQueryParser, QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query, BooleanQuery, BooleanClause
from org.apache.lucene.search.similarities import BM25Similarity

def retrieve(query_str):
    # storedir = '../lucene_code/lucene_index/'
    # storedir = '/home/cs172/lucene_code/lucene_index'
    # lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    if not lucene.getVMEnv():
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    lucene.getVMEnv().attachCurrentThread()
    storedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../lucene_code/lucene_index'))
    # print(os.listdir(storedir))
    # Open the directory and initialize the searcher
    searchDir = NIOFSDirectory(Paths.get(storedir))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))
    
    # Define which fields to search on
    fields = ["Title", "Selftext", "Comments"]
    analyzer = StandardAnalyzer()
    
    # Create a boolean query to combine field queries
    boolean_query = BooleanQuery.Builder()
    for field in fields:
        field_query = QueryParser(field, analyzer).parse(query_str)
        boolean_query.add(field_query, BooleanClause.Occur.SHOULD)
    
    # Perform the search
    max_results = 20
    topDocs = searcher.search(boolean_query.build(), max_results*10).scoreDocs
    unique_posts = set()
    topkdocs = []
    for hit in topDocs:
        doc = searcher.doc(hit.doc)
        post_id = doc.get("ID")
        if post_id not in unique_posts:
            topkdocs.append({
                "Score_Match": hit.score,
                "ID": post_id,
                "Title": doc.get("Title"),
                "Selftext": doc.get("Selftext"),
                "Upvotes": int(doc.get("Score")),
                "URL": doc.get("URL"),
                "Comments": doc.get("Comments"),
                "comments_count": int(doc.get("comments_count")),
                "relevance_score": int(hit.score) + 0.15*int(doc.get("Score")) + 0.05*int(doc.get("comments_count"))
            })
        else:
            continue
        unique_posts.add(post_id)
        if len(unique_posts) >= max_results:
            break
    # print(topkdocs)
    return topkdocs

docs = retrieve('Best thriller movies similar to sixth sense')
# print(docs)