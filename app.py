
# Using flask to make an api 
# import necessary libraries and functions 
from flask import Flask, jsonify, request, make_response,redirect
import jwt
import datetime as dt
import wikipedia as wiki
import spacy
import pandas as pd
from  functools import wraps
  
# creating a Flask app 
app = Flask(__name__) 
app.config['SECRET_KEY'] = 'thisissecretkey' 


def get_html(html: str):
    """Convert HTML so it can be rendered."""
    WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem; margin-bottom: 2.5rem">{}</div>"""
    # Newlines seem to mess with the rendering
    html = html.replace("\n", " ")
    return WRAPPER.format(html)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message':'Token is missing!'}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=["HS256"])
        except:
            return jsonify({'message':'Token is invalid!','token':data}), 403
        return f(*args, **kwargs)
    return decorated

 
@app.route('/', methods = ['GET', 'POST']) 
def home(): 
    if(request.method == 'GET'): 
  
        data = "Welcome To NER API By: Shreyas Chim"
        return jsonify({'data': data}) 
  

@app.route('/login') 
def login():
    auth = request.authorization 
    if auth and auth.username == 'username' and auth.password == 'password':
        token = jwt.encode({'user': auth.username, 'exp': dt.datetime.utcnow() + dt.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return  jsonify({'token' : token})

    return make_response('Could not verify!', 401, {'www-Authenticate': 'Basic real = "Login Required"'})
    


@app.route('/ner/<string:search>', methods = ['GET']) 
@token_required
def ner(search): 

    try:
        article = wiki.summary(search)
        model = spacy.load("en_core_web_md")
        results = model(article)


        labels = []
        for element in results.ents:
            labels.append(element.label_)

        data = []
        for i in set(labels):
            data.append([labels.count(i),str(i)])
    
        df = pd.DataFrame(data,columns=('Occurance','Labels'))
        df = df.rename(columns={'Labels':'index'}).set_index('index')
        df = df.to_json()

        html = spacy.displacy.render(results, style="ent")
        style = "<style> { display: inline-block }</style>"
        page = f"{style}{get_html(html)}"

        return jsonify({'link': page, 'data' : df, 'status': "success", 'message': "Article processed!"}) 

    except:
        return jsonify({'status': "failed",'message': "Article not found!"}) 
    
    return ner

  
# driver function 
if __name__ == '__main__': 
  
    app.run(debug = True) 
