import logging, sys
logging.disable(sys.maxsize)

import lucene
import os
import json
import time
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity

# sample_json = [{
#     "selftext": "machine learning",
#     "title": "artificial intelligence",
#     "id": "1ciuvqe",
#     "score": 3,
#     "url": "https://www.reddit.com/r/ArtificialInteligence/comments/1ciuvqe/improving_diffusion_models_for_virtual_tryon/",
#     "permalink": "/r/ArtificialInteligence/comments/1ciuvqe/improving_diffusion_models_for_virtual_tryon/",
#     "comments": [
#         {
#             "id": "l2bpsh2",
#             "body": "deep learning",
#             "score": 1,
#             "replies": []
#         },
#         {
#             "id": "l2bqm0e",
#             "body": "reinforcement learning",
#             "score": 1,
#             "replies": []
#         }
#     ]
# }]

def load_data_from_files(file_paths):
    all_data = []
    for file_path in file_paths:
        # print(file_path)
        with open(file_path, 'r') as file:
            data = json.load(file)
            # print(len(data))
            all_data.extend(data)
    # print(len(all_data))
    return all_data

def get_comments(comments_data):
    comments = []
    for comment in comments_data:
        if comment['score'] <= 0:
            continue
        elif 'replies' in comment:
            if comment['replies'] == []:
                pass
            else:
                comments = comments + get_comments(comment['replies'])
            del comment['replies']
        if 'links' in comment:
            del comment['links']
        comments.append(comment)
    return comments

def concat_top_comments(data):
    comments_flattened = get_comments(data['comments'])
    # print('len(comments_flattened)', len(comments_flattened))
    comment_count = len(comments_flattened)
    comments_flattened = sorted(comments_flattened, key=lambda x: x['score'], reverse=True)
    comments_flattened = comments_flattened[0:50]
    comments_concat = ' '.join([comment['body'] for comment in comments_flattened])
    return comments_concat, comment_count

def create_index(dir, tot_data):
    if not os.path.exists(dir):
        os.mkdir(dir)
    store = SimpleFSDirectory(Paths.get(dir))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(store, config)

    metaType = FieldType()
    metaType.setStored(True)
    metaType.setTokenized(False)

    contextType = FieldType()
    contextType.setStored(True)
    contextType.setTokenized(True)
    contextType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    # Index the main post
    for data in tot_data:
        doc = Document()
        # url = data['url']
        # if url.startswith('https://www.reddit.com/r/'):
        # print(type(data))
        if type(data) in [str]:
            # print(data)
            continue
        doc.add(Field('ID', str(data['id']), metaType))
        doc.add(Field('Title', str(data['title']), contextType))
        doc.add(Field('Selftext', str(data['selftext']), contextType))
        doc.add(Field('Score', str(data['score']), metaType))
        doc.add(Field('URL', str(data['url']), metaType))
        comments, comment_count = concat_top_comments(data)
        doc.add(Field('Comments', comments, contextType))
        doc.add(Field('comments_count', comment_count, metaType))
        writer.addDocument(doc)
        # for comment in data['comments']:
        #     comment_doc = Document()
        #     comment_doc.add(Field('ID', str(data['id']), metaType))
        #     comment_doc.add(Field('Title', str(data['title']), metaType))
        #     comment_doc.add(Field('Comment_ID', str(comment['id']), metaType))
        #     comment_doc.add(Field('Comment_Body', str(comment['body']), contextType))
        #     comment_doc.add(Field('Score', str(comment['score']), metaType))
        #     comment_doc.add(Field('URL', str(data['url']), metaType))
        #     writer.addDocument(comment_doc)
    writer.close()

lucene.initVM(vmargs=['-Djava.awt.headless=true'])
data_path = "../reddit_data"
file_paths = os.listdir(data_path)
file_paths = [os.path.join(data_path, file_path) for file_path in file_paths]
all_data = load_data_from_files(file_paths)
start_time = time.time() 
create_index('lucene_index/', all_data)
end_time = time.time()  # End timing
total_time = end_time - start_time
print(f"Total time taken to index data: {total_time:.2f} seconds")