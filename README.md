
# NameEntityRecognizerAPI
## Name entity recognizer API in Flask and Streamlit

# <a href="http://ec2-35-154-121-148.ap-south-1.compute.amazonaws.com:8501/" title="Application Preview">Click here for Application Preview! </a>   
# <a href="http://nerflaskapi-env.eba-qbyevvcg.ap-south-1.elasticbeanstalk.com/" title="API Endpoint"> Click here for API Endpoint!</a>


## Requirements :- 
Python3, Flask, JWT, Streamlit etc.

## Steps to run the app :- 
1) Install all python packages from "requirements.txt" file using pip by cmd "pip3 install -r requirement.txt".
2) Run app.py simply using cmd "python3 application.py" it will launch flask based API on port http://127.0.0.1:5000/ for name entity recognizer.
3) Token based authentication technique is applied to secure API endpoints.
4) Make sure application.py is still runnung on port http://127.0.0.1:5000/.
5) Now next step is to run streamlit.py using cmd "streamlit run streamlit.py" it will host port http://localhost:8502/.
6) Now simply typ your search topic inside the input box and hit enter.  
8) It will display annotated text in Streamlit App and also display the occurrence of each label in a text in Bar graph form.
9) Sharing screenshots for clear understanding!


# application.py (NER API using flask) 

#### Import necessary libraries 
```python
from flask import Flask, jsonify, request, make_response,redirect
import jwt
import datetime as dt
import wikipedia as wiki
import spacy
import pandas as pd
from  functools import wraps 
```
#### Creating a Flask app 
```python
application = Flask(__name__) 
```
#### Secret key decleration for Token Based Authentication  
```python
application.config['SECRET_KEY'] = 'thisissecretkey' 
```

#### Convert HTML so it can be rendered :
```python
def get_html(html: str):  
    WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem; margin-bottom: 2.5rem">{}</div>"""
    # Newlines seem to mess with the rendering
    html = html.replace("\n", " ")
    return WRAPPER.format(html)
```
#### Function for generating token using HS256 algorithm  
```python
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message':'Token is missing!'}), 403
        try:
            data = jwt.decode(token, application.config['SECRET_KEY'],algorithms=["HS256"])
        except:
            return jsonify({'message':'Token is invalid!','token':data}), 403
        return f(*args, **kwargs)
    return decorated
```
#### Home Route
```python    
@application.route('/', methods = ['GET', 'POST']) 
def home(): 
    if(request.method == 'GET'): 
        data = "Welcome To NER API By: Shreyas Chim"
        return jsonify({'data': data}) 
```  
#### Login function, Username:"username", Password:"password" for now. 
```python
@application.route('/login') 
def login():
    auth = request.authorization 
    if auth and auth.username == 'username' and auth.password == 'password':
        token = jwt.encode({'user': auth.username, 'exp': dt.datetime.utcnow() + dt.timedelta(minutes=30)}, application.config['SECRET_KEY'])
        return  jsonify({'token' : token})
    return make_response('Could not verify!', 401, {'www-Authenticate': 'Basic real = "Login Required"'})
```    

#### Text pre-processing and Named Entity Recognition 
```python
@application.route('/ner/<string:search>', methods = ['GET']) 
@token_required
def ner(search): 

    try:
        article = wiki.summary(search)
        model = spacy.load('en_core_web_sm')
        doc = model(article) 
        doc=[token for token in doc if not token.is_stop and not token.is_punct]
        doc = ' '.join([str(ele) for ele in doc])
        results = model(doc)
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
```
  
#### Driver Function 

```python
if __name__ == '__main__': 
  
    application.run(debug = True) 
``` 

## Entire Code (application.py)

```python

from flask import Flask, jsonify, request, make_response,redirect
import jwt
import datetime as dt
import wikipedia as wiki
import spacy
import pandas as pd
from  functools import wraps
  
application = Flask(__name__) 
application.config['SECRET_KEY'] = 'thisissecretkey' 

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
            data = jwt.decode(token, application.config['SECRET_KEY'],algorithms=["HS256"])
        except:
            return jsonify({'message':'Token is invalid!','token':data}), 403
        return f(*args, **kwargs)
    return decorated
 
@application.route('/', methods = ['GET', 'POST']) 
def home(): 
    if(request.method == 'GET'): 
        data = "Welcome To NER API By: Shreyas Chim"
        return jsonify({'data': data}) 
  
@application.route('/login') 
def login():
    auth = request.authorization 
    if auth and auth.username == 'username' and auth.password == 'password':
        token = jwt.encode({'user': auth.username, 'exp': dt.datetime.utcnow() + dt.timedelta(minutes=30)}, application.config['SECRET_KEY'])
        return  jsonify({'token' : token})
    return make_response('Could not verify!', 401, {'www-Authenticate': 'Basic real = "Login Required"'})

@application.route('/ner/<string:search>', methods = ['GET']) 
@token_required
def ner(search): 
    try:
        article = wiki.summary(search)
        model = spacy.load('en_core_web_sm')
        doc = model(article) 
        doc=[token for token in doc if not token.is_stop and not token.is_punct]
        doc = ' '.join([str(ele) for ele in doc])
        results = model(doc)
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

if __name__ == '__main__': 
    application.run(debug = True) 

```

# streamlit.py (Interface, accessing API using Streamlit)

```python
import streamlit as st
import requests
import json
```

#### Generating API Request 

```python
def ner_api(search):
    r = requests.get("http://nerflaskapi-env.eba-qbyevvcg.ap-south-1.elasticbeanstalk.com/login",auth=('username','password'))
    rj = r.json()
    token = rj['token']
    url = f"http://nerflaskapi-env.eba-qbyevvcg.ap-south-1.elasticbeanstalk.com/ner/{search}?token={token}"
    ner = requests.get(url)
 ```   
#### Building App 

```python
if __name__ == '__main__':

    st.title("Wikipedia API to perform NER")
    st.header("by- Shreyas R. Chim")

    search = st.text_input("Enter Search Name", "Type here...")
    ner = ner_api(search)
    ner_json = ner.json()
    if ner_json['status'] == 'failed':
        st.write(f"Record not found!")
        
    if ner_json['status'] == 'success':
        page = ner_json['link']
        data = json.loads(ner_json['data'])
        st.write("Article processed!")
        st.write(page, unsafe_allow_html=True)
        st.bar_chart(data)
    else:
        st.write(f"System Faceing issue !")

    
    st.text(f"NLP Assignment by- Shreyas R. Chim")

``` 
#### Entire Code (streamlit.py)

```python
import streamlit as st
import requests
import json

def ner_api(search):
    r = requests.get("http://nerflaskapi-env.eba-qbyevvcg.ap-south-1.elasticbeanstalk.com/login",auth=('username','password'))
    rj = r.json()
    token = rj['token']
    url = f"http://nerflaskapi-env.eba-qbyevvcg.ap-south-1.elasticbeanstalk.com/ner/{search}?token={token}"
    ner = requests.get(url)

    return ner

if __name__ == '__main__':

    st.title("Wikipedia API to perform NER")
    st.header("by- Shreyas R. Chim")

    search = st.text_input("Enter Search Name", "Type here...")
    ner = ner_api(search)
    ner_json = ner.json()
    if ner_json['status'] == 'failed':
        st.write(f"Record not found!")
        
    if ner_json['status'] == 'success':
        page = ner_json['link']
        data = json.loads(ner_json['data'])
        st.write("Article processed!")
        st.write(page, unsafe_allow_html=True)
        st.bar_chart(data)
    else:
        st.write(f"System Faceing issue !") 
    st.text(f"NLP Assignment by- Shreyas R. Chim")
   ```
   
# Application Screenshots
![Screenshot from 2021-03-08 20-29-58](https://user-images.githubusercontent.com/33173746/110338773-64635280-804d-11eb-94af-291ed49345ae.png)
![Screenshot from 2021-03-08 20-30-06](https://user-images.githubusercontent.com/33173746/110338788-69c09d00-804d-11eb-949f-61206f124bdc.png)
![Screenshot from 2021-03-08 20-31-08](https://user-images.githubusercontent.com/33173746/110338797-6cbb8d80-804d-11eb-9b62-83a873940c64.png)
![Screenshot from 2021-03-08 20-31-14](https://user-images.githubusercontent.com/33173746/110338801-6e855100-804d-11eb-86e3-80bc020381ec.png)

 # References
 1) https://streamlit.io/
 2) https://flask.palletsprojects.com/en/1.1.x/api/
 3) https://pythonhosted.org/Flask-JWT/
