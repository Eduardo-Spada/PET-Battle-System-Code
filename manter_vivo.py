from flask import Flask
from threading import Thread
import requests
import time

app = Flask('')

@app.route('/')
def home():
    return "O bot tá vivo, Felipe!"

def ping_self():
    while True:
        try:
            # Substitua pela URL do Render quando o deploy estiver pronto
            requests.get("https://SEU-APP.onrender.com")
        except:
            pass
        time.sleep(600)  # A cada 10 minutos

def manter_vivo():
    t1 = Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8080})
    t2 = Thread(target=ping_self)
    t1.start()
    t2.start()
