from flask import Blueprint, render_template, request, redirect, url_for
import random
from .retrieve_data import retrieve
# from .get_query_details import get_details
views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query = request.form.get('query')
        sort_by = request.form.get('sort_by')
        # print("query", query, type(query))
        if query.strip() == "":
            return render_template("home.html")
        query_output = retrieve(query)
        if sort_by == "upvotes":
            query_output.sort(key=lambda x: x['Upvotes'], reverse = True)
        elif sort_by == "popularity":
            query_output.sort(key=lambda x: x['comments_count'], reverse = True)
        else:
            query_output.sort(key=lambda x: x['relevance_score'], reverse = True)
        # query_output = get_details(query)
        # rand_query = query_output[random.randint(0, len(query_output)-1)]
        # print(type(rand_query))
        # print(type(query_output))
        # query_output = [rand_query] + query_output
        return render_template("search.html", query = query, results=query_output)
        # flask.redirect(flask.url_for('operation'), code=307)
        # return redirect(url_for('views.search', query = query, results=query_output), code=307)
    else:
        # query_output = ""
        return render_template("home.html")


# @views.route('/search', methods=['GET', 'POST'])
# def search():
#     if request.method == 'POST':
#         query = request.form.get('query')
#         query_output = get_details(query)
#         return render_template("search.html", query = query, results=query_output)
#     else:
#         return redirect(url_for('views.home'))