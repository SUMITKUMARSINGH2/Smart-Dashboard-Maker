# Loading all streamlit animations here to use it in the app.

#importing all the necessary libraries
import json
import requests
from streamlit_lottie import st_lottie

# Function to load lottie files and urls
def load_lottiefile(filepath:str):
    with open (filepath, 'r',encoding='utf-8') as f:
        return json.load(f)
def load_lottieurl(url:str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Loading all lottie animations

Dataoverview_lo = load_lottiefile("./lotti/Dataoverview.json")
Filepre_lo = load_lottiefile("./lotti/Filepre.json")
Home_lo = load_lottiefile("./lotti/Home.json")