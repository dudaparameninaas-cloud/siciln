# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# JSON yanıtlarında Türkçe karakterleri düzgün göstermek için
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

DB_PATH = "bursasicil.db"  # Render klasörüne koyduğun .db

def normalize(text):
    """Büyük harfe çevir, Türkçe karakterleri koru ve baş/son boşlukları kırp."""
    if not text:
        return ""
    # Önce string'e çevir, sonra strip ve upper uygula
    text = str(text).strip()
    # Türkçe karakterleri koruyarak büyük harfe çevir
    return text.upper()

def query_db(query, params=()):
    """SQLite sorgusu çalıştır ve dict listesi döndür."""
    try:
        conn = sqlite3.connect(DB_PATH)
        # UTF-8 kodlamasını zorla
        conn.text_factory = str  # Python 2 için, Python 3'te varsayılan UTF-8
        conn.row_factory = sqlite3.Row  # dict gibi erişim
        cur = conn.cursor()
        cur.execute(query, params)
        rows = [dict(row) for row in cur.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        print(f"Veritabanı hatası: {e}")
        return []

def json_response(data):
    """UTF-8 ve özel karakterleri düzgün döndür."""
    return jsonify(data)

@app.route("/")
def home():
    return {"status": "ok", "message": "Sicil API aktif - Türkçe karakter desteği var"}

# 1️⃣ Dosya ID ile sorgu
@app.route("/id")
def id_sorgu():
    id_ = request.args.get("id")
    if not id_:
        return {"error": "id parametresi eksik"}, 400
    try:
        sonuc = query_db("SELECT * FROM '150kbursasicil' WHERE ID = ?", (id_,))
        if not sonuc:
            return {"message": "Kayıt bulunamadı", "data": []}
        return json_response(sonuc)
    except Exception as e:
        return {"error": f"Sorgu hatası: {str(e)}"}, 500

# 2️⃣ Ad ile sorgu
@app.route("/ad")
def ad_sorgu():
    ad = request.args.get("ad")
    if not ad:
        return {"error": "ad parametresi eksik"}, 400
    
    ad = normalize(ad)
    try:
        sonuc = query_db("SELECT * FROM '150kbursasicil'")
        # Türkçe karakter duyarlılığı için normalize edilmiş değerlerle karşılaştır
        filtreli_sonuc = [x for x in sonuc if ad in normalize(x.get("KISI_ADI", ""))]
        
        if not filtreli_sonuc:
            return {"message": "Kayıt bulunamadı", "data": []}
        return json_response(filtreli_sonuc)
    except Exception as e:
        return {"error": f"Sorgu hatası: {str(e)}"}, 500

# 3️⃣ Soyad ile sorgu
@app.route("/soyad")
def soyad_sorgu():
    soyad = request.args.get("soyad")
    if not soyad:
        return {"error": "soyad parametresi eksik"}, 400
    
    soyad = normalize(soyad)
    try:
        sonuc = query_db("SELECT * FROM '150kbursasicil'")
        filtreli_sonuc = [x for x in sonuc if soyad in normalize(x.get("KISI_SOYAD", ""))]
        
        if not filtreli_sonuc:
            return {"message": "Kayıt bulunamadı", "data": []}
        return json_response(filtreli_sonuc)
    except Exception as e:
        return {"error": f"Sorgu hatası: {str(e)}"}, 500

# 4️⃣ Ad + Soyad ile sorgu
@app.route("/adsoyad")
def adsoyad_sorgu():
    ad = request.args.get("ad")
    soyad = request.args.get("soyad")
    
    if not ad or not soyad:
        return {"error": "ad ve soyad parametreleri gerekli"}, 400
    
    ad = normalize(ad)
    soyad = normalize(soyad)
    
    try:
        sonuc = query_db("SELECT * FROM '150kbursasicil'")
        filtreli_sonuc = [
            x for x in sonuc
            if ad in normalize(x.get("KISI_ADI", "")) 
            and soyad in normalize(x.get("KISI_SOYAD", ""))
        ]
        
        if not filtreli_sonuc:
            return {"message": "Kayıt bulunamadı", "data": []}
        return json_response(filtreli_sonuc)
    except Exception as e:
        return {"error": f"Sorgu hatası: {str(e)}"}, 500

# 5️⃣ Avukat TC ile sorgu
@app.route("/avukat_tc")
def avukat_tc_sorgu():
    tc = request.args.get("tc")
    if not tc:
        return {"error": "tc parametresi eksik"}, 400
    
    try:
        sonuc = query_db("SELECT * FROM '150kbursasicil' WHERE AVUKAT_TC_KIMLIK_NO = ?", (tc,))
        if not sonuc:
            return {"message": "Kayıt bulunamadı", "data": []}
        return json_response(sonuc)
    except Exception as e:
        return {"error": f"Sorgu hatası: {str(e)}"}, 500

# Hata yakalama
@app.errorhandler(404)
def not_found(error):
    return {"error": "Sayfa bulunamadı"}, 404

@app.errorhandler(500)
def internal_error(error):
    return {"error": "Sunucu hatası"}, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
