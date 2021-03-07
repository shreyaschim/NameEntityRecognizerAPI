import streamlit as st
import requests
import json

def ner_api(search):
    r = requests.get("http://127.0.0.1:5000/login",auth=('username','password'))
    rj = r.json()
    token = rj['token']
    url = f"http://127.0.0.1:5000/ner/{search}?token={token}"
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