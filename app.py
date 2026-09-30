import os, asyncio, sqlite3
from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
from telegram import Bot
from checker import check_product

load_dotenv()
app = Flask(__name__)
DB = "stock_alerts.db"
CHAT_ID_DEFAULT = "7538903918"

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.execute("""CREATE TABLE IF NOT EXISTS alerts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        chat_id TEXT NOT NULL,
        in_stock INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1,
        last_status TEXT DEFAULT 'Unknown'
    )""")
    con.commit(); con.close()

async def send_telegram(text):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    await Bot(token).send_message(chat_id=CHAT_ID_DEFAULT, text=text)

@app.route("/")
def home():
    con = db()
    rows = con.execute("SELECT * FROM alerts WHERE active=1 ORDER BY id DESC").fetchall()
    con.close()
    return render_template("index.html", alerts=rows, chat_id=CHAT_ID_DEFAULT)

@app.post("/add")
def add():
    url = request.form["url"].strip()
    chat_id = request.form.get("chat_id", CHAT_ID_DEFAULT).strip() or CHAT_ID_DEFAULT
    if not any(x in url.lower() for x in ["amazon.", "flipkart.", "croma.", "reliancedigital.", "jiomart."]):
        return jsonify(ok=False, error="Supported stores: Amazon, Flipkart, Croma, Reliance Digital, JioMart"), 400
    con = db()
    con.execute("INSERT INTO alerts(url,chat_id) VALUES(?,?)", (url, chat_id))
    con.commit(); con.close()
    return jsonify(ok=True)

@app.post("/delete/<int:alert_id>")
def delete(alert_id):
    con = db()
    con.execute("UPDATE alerts SET active=0 WHERE id=?", (alert_id,))
    con.commit(); con.close()
    return jsonify(ok=True)

def worker():
    import time
    while True:
        con = db()
        rows = con.execute("SELECT * FROM alerts WHERE active=1").fetchall()
        con.close()
        for r in rows:
            try:
                status = check_product(r["url"])
                old = bool(r["in_stock"])
                new = status == "IN_STOCK"
                con = db()
                con.execute("UPDATE alerts SET in_stock=?, last_status=? WHERE id=?", (int(new), status, r["id"]))
                con.commit(); con.close()
                if new and not old:
                    asyncio.run(send_telegram("🟢 IN STOCK!\n\nBuy now:\n" + r["url"]))
            except Exception as e:
                con = db()
                con.execute("UPDATE alerts SET last_status=? WHERE id=?", ("ERROR: "+str(e)[:180], r["id"]))
                con.commit(); con.close()
        time.sleep(int(os.getenv("CHECK_SECONDS", "300")))

if __name__ == "__main__":
    init_db()
    import threading
    threading.Thread(target=worker, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
