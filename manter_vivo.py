from flask import Flask
from threading import Thread
import requests
import time
import os

app = Flask('')

@app.route('/')
def home():
    return "O bot tá vivo, Felipe!"

@app.route('/healthz')
def health():
    return "OK", 200

def ping_self():
    while True:
        try:
            # Ping na URL do Render para manter o app acordado
            requests.get("https://pet-battle-system-code.onrender.com")
        except:
            pass
        time.sleep(600)  # A cada 10 minutos

def manter_vivo():
    port = int(os.environ.get("PORT", 8080))
    t1 = Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': port})
    t2 = Thread(target=ping_self)
    t1.start()
    t2.start()
