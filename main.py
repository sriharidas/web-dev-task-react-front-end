from flask import  Flask, jsonify
from flask_cors import CORS, cross_origin
import imdb
import pandas as pd

app = Flask(__name__)
cors = CORS(app)

movies_dataset = pd.read_csv("C:/Users/srihari/Desktop/Haridas/College/Datasets/movie/IMDb movies.csv/IMDb movies.csv")
field_list = list(movies_dataset.columns)
last_indx = field_list.index('budget')
movies_df = pd.DataFrame(movies_dataset[field_list[:last_indx+1]])
movies_df.dropna(inplace=True)
movies_df.reset_index(drop=True, inplace=True)
sorted_movies = movies_df.sort_values(by="votes", ascending=False).reset_index(drop=True)

@app.route('/search/movies/<field>/<name>/<num>', methods=['GET'])
def search_movie_by_field(field, name, num):
    idb = imdb.IMDb()
    result_data_list= []
    counts = 0
    columns = sorted_movies.columns
    try:
        for rowIndx in range(sorted_movies.shape[0]):
            movie_data = {
                'details': {}
            }
            if counts >= int(num):
                break
            if type(sorted_movies[field][rowIndx])== str:
                if name.lower() in sorted_movies[field][rowIndx].lower():
                    # movie = idb.search_movie(sorted_movies['title'][rowIndx])[0]
                    # print(movie, movie[movie.keys()[0]])
                    # for prop in movie.keys():
                    #     movie_data['details'][prop] = str(movie[prop])
                    for col in columns:
                        movie_data[col] = str(sorted_movies[col][rowIndx])
                    result_data_list.append(movie_data)
                    counts+=1
            else:
                if sorted_movies[field][rowIndx] >= float(name):
                    # movie = idb.search_movie(sorted_movies['title'][rowIndx])[0]
                    # for prop in movie.keys():
                    #     movie_data['details'][prop] = str(movie[prop])
                    for col in columns:
                        movie_data[col] = str(sorted_movies[col][rowIndx])
                    result_data_list.append(movie_data)
                    counts+=1
    except KeyError:
        print("Key not found")
    print(len(result_data_list))
    # print(result_data_list[0])
    return jsonify(result_data_list[::-1])
@app.route('/get/movie/data/<name>', methods=['GET'])
@cross_origin()
def get_movie_details(name):
    idb =imdb.IMDb()
    movie_details = {}
    movie = idb.search_movie(name)[0]
    for i in movie.keys():
        movie_details[i] = movie[i]
    return jsonify(movie_details)
@app.route('/search/movie/<name>', methods=['POST', 'GET'])
@cross_origin()
def search_movie(name):
    idb = imdb.IMDb()
    result = {}
    movie_details = idb.search_movie(name)[0]
    for field in movie_details.keys():
        result[field] = movie_details[field]
    return jsonify(result)

@app.route('/movie/info/<name>', methods=['GET','POST'])
@cross_origin()
def movie_info(name):
    idb = imdb.IMDb()
    data_movie = {}
    search_result = idb.search_movie(name)
    movie = search_result[0]
    getMovie = idb.get_movie(movie.movieID)
    idb.update(getMovie, ['reviews'])
    idb.update(getMovie, ['video clips'])
    print(movie)
    for i in getMovie.keys():
        if type(getMovie[i])==list:
            sub_list = []
            for item in getMovie[i]:
                if type(item) == str or type(item) == int or type(item) == float :
                    sub_list.append(item)
                else:
                    temp = {}
                    try:
                        if type(item) == tuple:
                            sub_list.append(list(item))
                        else:
                            sub_list.append(item['name'])
                    except KeyError:
                        for props in item.keys():
                            temp[props] = item[props]
                        sub_list.append(temp)
                        print("key not found")
                data_movie[i] = sub_list
            print(i, len(sub_list))
        else:
            data_movie[i] = getMovie[i]
    return jsonify(data_movie)

@app.route('/person/info/<name>', methods=['GET'])
@cross_origin()
def searchPerson(name):
    idb = imdb.IMDb()
    person = idb.get_person(idb.search_person(name)[0].personID)
    person_data = {}
    for prop in person.keys():
        if type(person[prop]) == list:
            sub_list = []
            for i in person[prop]:
                # print(i)
                if type(i) == str or type(i) == int or type(i) == float:
                    sub_list.append(i)
                elif type(i)==dict:
                    print(i)
                    for j in person[prop][i].keys():
                        print(j)
                        sub_list.append(dict(j))
            person_data[prop] = sub_list
        elif type(person[prop]) == dict:
            sub_list = []
            for k in person[prop].keys():
                if type(person[prop][k]) == list:
                    for i in person[prop][k]:
                        sub_list.append(dict(i)['title'])
            person_data[prop]  = sub_list
        else:
            person_data[prop] = person[prop]
    print(person_data['filmography'])
    return jsonify(person_data)

@app.route('/get/top/<num>/<type>')
def trending(num,type):
    idb = imdb.IMDb()
    if type=="movie":
       return jsonify({ 'lists': [ i['title'] for i in idb.get_top250_movies()[:int(num)] ]})
    else:
        return jsonify( {'lists': [ i['title'] for i in idb.get_top250_tv()[:int(num)] ]})
        
if __name__ == '__main__':
    app.run(debug=True)
