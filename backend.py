from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_PATH = "bursasicil.db"  # Render klasörüne koyduğun .db dosyası

def normalize(text):
    """Büyük harfe çevir ve baş/son boşlukları kırp."""
    return text.upper().strip() if text else ""

def query_db(query, params=()):
    """SQLite sorgusu çalıştır ve dict listesi döndür."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, params)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

@app.route("/")
def home():
    return {"status": "ok", "message": "Bursa Sicil API aktif"}

# 1️⃣ ID ile sorgu
@app.route("/id")
def id_sorgu():
    id_ = request.args.get("id")
    if not id_:
        return {"error": "id parametresi eksik"}
    sonuc = query_db("SELECT * FROM '150kbursasicil' WHERE ID = ?", (id_,))
    return jsonify(sonuc)

# 2️⃣ Kişi adı ile sorgu
@app.route("/ad")
def ad_sorgu():
    ad = request.args.get("ad")
    if not ad:
        return {"error": "ad parametresi eksik"}
    ad = normalize(ad)
    sonuc = query_db("SELECT * FROM '150kbursasicil'")
    sonuc = [x for x in sonuc if ad in normalize(x["KISI_ADI"])]
    return jsonify(sonuc)

# 3️⃣ Kişi soyadı ile sorgu
@app.route("/soyad")
def soyad_sorgu():
    soyad = request.args.get("soyad")
    if not soyad:
        return {"error": "soyad parametresi eksik"}
    soyad = normalize(soyad)
    sonuc = query_db("SELECT * FROM '150kbursasicil'")
    sonuc = [x for x in sonuc if soyad in normalize(x["KISI_SOYAD"])]
    return jsonify(sonuc)

# 4️⃣ Ad + Soyad ile sorgu
@app.route("/adsoyad")
def adsoyad_sorgu():
    ad = request.args.get("ad")
    soyad = request.args.get("soyad")
    if not ad or not soyad:
        return {"error": "ad ve soyad parametreleri gerekli"}
    ad = normalize(ad)
    soyad = normalize(soyad)
    sonuc = query_db("SELECT * FROM '150kbursasicil'")
    sonuc = [x for x in sonuc if ad in normalize(x["KISI_ADI"]) and soyad in normalize(x["KISI_SOYAD"])]
    return jsonify(sonuc)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
