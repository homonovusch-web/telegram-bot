from flask import Flask, request
import os

# ================== CONFIG ==================
TOKEN = "8458591477:AAGqIzFaYe-3DtWc45r24-hQPYyH4P4SIzY"
ADMIN_ID = 5749973037
DB_PATH = "utenti.db"
MEDIA_DIR = "media"
PAGE_SIZE = 5

os.makedirs(MEDIA_DIR, exist_ok=True)

# Inizializza Flask per mantenere attivo il bot
app = Flask(__name__)
WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost')}/{TOKEN}"

@app.route('/')
def home():
    return "Il bot Telegram è attivo e funzionante!"

# Route che riceve gli update da Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    if update:
        application.update_queue.put_nowait(Update.de_json(update, application.bot))
    return "ok"

# ========== IL TUO CODICE ESISTENTE INIZIA QUI SOTTO ==========
import csv
import sqlite3
from io import StringIO, BytesIO
from datetime import datetime
from typing import Optional, Tuple

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputFile,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)


# ================== STATI CONVERSAZIONE ==================
TERMINI, LINGUA, DOMANDA1, DOMANDA2, DOMANDA3, DOMANDA4, DOMANDA5, DOMANDA6, DOMANDA7, DOMANDA8, DOMANDA9, DOMANDA10, DOMANDA11, DOMANDA12, DOMANDA13, DOMANDA14, DOMANDA15, DOMANDA16, DOMANDA17, DOMANDA18, DOMANDA19, DOMANDA20, DOMANDA21, DOMANDA22, DOMANDA23, DOMANDA24 = range(26)

# ================== DOMANDE MULTILINGUA ==================
DOMANDE = {
    "it": [
        "Parlaci di te, come ti definiresti?",
        "Qual è il tuo genere?",
        "Qual è la tua nazionalità?",
        "In quale città ti trovi attualmente?",
        "Quanti anni hai?",
        "Qual è la tua altezza?",
        "Qual è il tuo peso?",
        "A chi sono rivolti i tuoi incontri?",
        "Di che colore sono i tuoi occhi?",
        "Di che colore sono i tuoi capelli?",
        "Qual è la misura del tuo seno? (se trovi che la domanda non sia pertinente per te, rispondi con -)",
        "Aspetto dei peli pubici?",
        "Come definiresti il tuo orientamento sessuale?",
        "Quali tipi di pagamento accetti?",
        "Sei disponibile a ricevere clienti nel tuo appartamento?",
        "Offri servizi a domicilio?",
        "Sei disponibile a offrire servizi in hotel?",
        "Quali lingue parli? Indica per ciascuna il livello da 1 a 3 stelle (dove 3 è il livello massimo)",
        "Ti chiediamo di elencare tutti i servizi che offri.",
        "Per favore, indica la fascia oraria e i giorni in cui sei disponibile a lavorare.",
        "Lascia un contatto WhatsApp dove i clienti potranno scriverti direttamente.",
        "Se hai Telegram, lascia il tuo username (se non vuoi rispondere, scrivi -)",
        "C'è un sito online dove sono già presenti alcune informazioni su di te? (se sì, scrivicelo; se no, rispondi con - )",
        "Grazie! Abbiamo ricevuto tutte le informazioni. Ora ti chiediamo gentilmente di inviarci delle foto di te, che verranno pubblicate sul nostro sito."
    ],
    "en": [
        "Tell us about yourself, how would you describe yourself?",
        "What is your gender?",
        "What is your nationality?",
        "In which city are you currently located?",
        "How old are you?",
        "What is your height?",
        "What is your weight?",
        "Who are your meetings aimed at?",
        "What color are your eyes?",
        "What color is your hair?",
        "What is your bust size? (if you find the question not relevant for you, answer with -)",
        "Appearance of pubic hair?",
        "How would you define your sexual orientation?",
        "What types of payment do you accept?",
        "Are you available to receive clients in your apartment?",
        "Do you offer services at home?",
        "Are you available to offer services in hotels?",
        "What languages do you speak? Indicate for each the level from 1 to 3 stars (where 3 is the maximum level)",
        "We ask you to list all the services you offer.",
        "Please indicate the time slot and days you are available to work.",
        "Leave a WhatsApp contact where clients can contact you directly.",
        "If you have Telegram, leave your username (if you don't want to answer, write -)",
        "Is there a website where some information about you is already present? (If yes, write it; if not, answer with -)",
        "Thank you! We have received all the information. Now we kindly ask you to send us some photos of yourself, which will be published on our website."
    ],
    "de": [
        "Erzähl uns von dir, wie würdest du dich beschreiben?",
        "Was ist dein Geschlecht?",
        "Was ist deine Nationalität?",
        "In welcher Stadt befindest du dich derzeit?",
        "Wie alt bist du?",
        "Wie groß bist du?",
        "Wie viel wiegst du?",
        "An wen richten sich deine Treffen?",
        "Welche Farbe haben deine Augen?",
        "Welche Farbe haben deine Haare?",
        "Was ist deine Büstengröße? (wenn du die Frage für nicht relevant hältst, antworte mit -)",
        "Erscheinungsbild der Schambehaarung?",
        "Wie würdest du deine sexuelle Orientierung definieren?",
        "Welche Zahlungsarten akzeptierst du?",
        "Bist du verfügbar, um Kunden in deiner Wohnung zu empfangen?",
        "Bietest du Dienstleistungen zu Hause an?",
        "Bist du verfügbar, um Dienstleistungen in Hotels anzubieten?",
        "Welche Sprachen sprichst du? Gib für jede das Niveau von 1 bis 3 Sternen an (wobei 3 das maximale Niveau ist)",
        "Wir bitten dich, alle Dienstleistungen aufzulisten, die du anbietest.",
        "Bitte gib den Zeitraum und die Tage an, an denen du verfügbar bist.",
        "Hinterlasse eine WhatsApp-Kontakt, unter der dich Kunden direkt errehen können.",
        "Wenn du Telegram hast, hinterlasse deinen Benutzernamen (wenn du nicht antworten möchtest, schreibe -)",
        "Gibt es eine Website, auf der bereits einige Informationen über dich vorhanden sind? (Wenn ja, schreibe sie; wenn nicht, antworte mit -)",
        "Danke! Wir haben alle Informationen erhalten. Nun bitten wir dich freundlich, uns einige Fotos von dir zu senden, die auf unserer Website veröffentlicht werden."
    ],
    "fr": [
        "Parlez-nous de vous, comment vous décririez-vous ?",
        "Quel est votre genre ?",
        "Quelle est votre nationalité ?",
        "Dans quelle ville vous trouvez-vous actuellement ?",
        "Quel âge avez-vous ?",
        "Quelle est votre taille ?",
        "Quel est votre poids ?",
        "À qui s'adressent vos rencontres ?",
        "De quelle couleur sont vos yeux ?",
        "De quelle couleur sont vos cheveux ?",
        "Quelle est votre taille de poitrine ? (si vous trouvez que la question n'est pas pertinente pour vous, répondez par -)",
        "Apparence des poils pubiens ?",
        "Comment définiriez-vous votre orientation sexuelle ?",
        "Quels types de paiement acceptez-vous ?",
        "Êtes-vous disponible pour recevoir des clients dans votre appartement ?",
        "Offrez-vous des services à domicile ?",
        "Êtes-vous disponible pour offrir des services en hôtel ?",
        "Quelles langues parlez-vous ? Indiquez pour chacune le niveau de 1 à 3 étoiles (où 3 est le niveau maximum)",
        "Nous vous demandons de lister tous les services que vous offrez.",
        "Veuillez indiquer la plage horaire et les jours où vous êtes disponible pour travailler.",
        "Laissez un contact WhatsApp où les clients pourront vous contacter directement.",
        "Si vous avez Telegram, laissez votre nom d'utilisateur (si vous ne voulez pas répondre, écrivez -)",
        "Y a-t-il un site en ligne où des informations sur vous sont déjà présentes ? (Si oui, écrivez-le ; si non, répondez par -)",
        "Merci ! Nous avons reçu toutes les informations. Maintenant, nous vous demandons aimablement de nous envoyer des photos de vous, qui seront publiées sur notre site."
    ]
}

# ================== DB INIT ==================
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON")
    c.execute("""
        CREATE TABLE IF NOT EXISTS utenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            lingua TEXT,
            risposta1 TEXT,
            risposta2 TEXT,
            risposta3 TEXT,
            risposta4 TEXT,
            risposta5 TEXT,
            risposta6 TEXT,
            risposta7 TEXT,
            risposta8 TEXT,
            risposta9 TEXT,
            risposta10 TEXT,
            risposta11 TEXT,
            risposta12 TEXT,
            risposta13 TEXT,
            risposta14 TEXT,
            risposta15 TEXT,
            risposta16 TEXT,
            risposta17 TEXT,
            risposta18 TEXT,
            risposta19 TEXT,
            risposta20 TEXT,
            risposta21 TEXT,
            risposta22 TEXT,
            risposta23 TEXT,
            risposta24 TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS foto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_id TEXT NOT NULL,
            file_path_local TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES utenti(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

# ================== UTILS ==================
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def upsert_user(user_id_tg: int) -> int:
    conn = db()
    c = conn.cursor()
    c.execute("SELECT id FROM utenti WHERE user_id = ?", (user_id_tg,))
    row = c.fetchone()
    if row:
        uid = row["id"]
    else:
        c.execute("INSERT INTO utenti (user_id) VALUES (?)", (user_id_tg,))
        conn.commit()
        uid = c.lastrowid
    conn.close()
    return uid

def set_user_field(user_id_db: int, field: str, value: Optional[str]):
    conn = db()
    c = conn.cursor()
    c.execute(f"UPDATE utenti SET {field} = ? WHERE id = ?", (value, user_id_db))
    conn.commit()
    conn.close()

def count_photos(user_id_db: int) -> int:
    conn = db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM foto WHERE user_id = ?", (user_id_db,))
    n = c.fetchone()[0]
    conn.close()
    return n

def get_users(offset=0, limit=PAGE_SIZE, search: Optional[str] = None) -> Tuple[list, int]:
    conn = db()
    c = conn.cursor()
    if search:
        try:
            tg_id = int(search.strip())
            c.execute("SELECT * FROM utenti WHERE user_id = ? ORDER BY id DESC LIMIT ? OFFSET ?", (tg_id, limit, offset))
        except ValueError:
            like = f"%{search}%"
            c.execute("""
                SELECT * FROM utenti
                WHERE lingua LIKE ? OR IFNULL(risposta1,'') LIKE ? OR IFNULL(risposta2,'') LIKE ? OR IFNULL(risposta3,'') LIKE ? OR IFNULL(risposta4,'') LIKE ? OR IFNULL(risposta5,'') LIKE ? OR IFNULL(risposta6,'') LIKE ? OR IFNULL(risposta7,'') LIKE ? OR IFNULL(risposta8,'') LIKE ? OR IFNULL(risposta9,'') LIKE ? OR IFNULL(risposta10,'') LIKE ? OR IFNULL(risposta11,'') LIKE ? OR IFNULL(risposta12,'') LIKE ? OR IFNULL(risposta13,'') LIKE ? OR IFNULL(risposta14,'') LIKE ? OR IFNULL(risposta15,'') LIKE ? OR IFNULL(risposta16,'') LIKE ? OR IFNULL(risposta17,'') LIKE ? OR IFNULL(risposta18,'') LIKE ? OR IFNULL(risposta19,'') LIKE ? OR IFNULL(risposta20,'') LIKE ? OR IFNULL(risposta21,'') LIKE ? OR IFNULL(risposta22,'') LIKE ? OR IFNULL(risposta23,'') LIKE ? OR IFNULL(risposta24,'') LIKE ?
                ORDER BY id DESC LIMIT ? OFFSET ?
            """, (like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, limit, offset))
    else:
        c.execute("SELECT * FROM utenti ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))
    rows = c.fetchall()
    # total
    if search:
        try:
            tg_id = int(search.strip())
            c.execute("SELECT COUNT(*) FROM utenti WHERE user_id = ?", (tg_id,))
        except ValueError:
            like = f"%{search}%"
            c.execute("""
                SELECT COUNT(*) FROM utenti
                WHERE lingua LIKE ? OR IFNULL(risposta1,'') LIKE ? OR IFNULL(risposta2,'') LIKE ? OR IFNULL(risposta3,'') LIKE ? OR IFNULL(risposta4,'') LIKE ? OR IFNULL(risposta5,'') LIKE ? OR IFNULL(risposta6,'') LIKE ? OR IFNULL(risposta7,'') LIKE ? OR IFNULL(risposta8,'') LIKE ? OR IFNULL(risposta9,'') LIKE ? OR IFNULL(risposta10,'') LIKE ? OR IFNULL(risposta11,'') LIKE ? OR IFNULL(risposta12,'') LIKE ? OR IFNULL(risposta13,'') LIKE ? OR IFNULL(risposta14,'') LIKE ? OR IFNULL(risposta15,'') LIKE ? OR IFNULL(risposta16,'') LIKE ? OR IFNULL(risposta17,'') LIKE ? OR IFNULL(risposta18,'') LIKE ? OR IFNULL(risposta19,'') LIKE ? OR IFNULL(risposta20,'') LIKE ? OR IFNULL(risposta21,'') LIKE ? OR IFNULL(risposta22,'') LIKE ? OR IFNULL(risposta23,'') LIKE ? OR IFNULL(risposta24,'') LIKE ?
            """, (like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like, like))
    else:
        c.execute("SELECT COUNT(*) FROM utenti")
    total = c.fetchone()[0]
    conn.close()
    return rows, total

def get_user(user_id_db: int):
    conn = db()
    c = conn.cursor()
    c.execute("SELECT * FROM utenti WHERE id = ?", (user_id_db,))
    row = c.fetchone()
    conn.close()
    return row

def get_user_photos(user_id_db: int) -> list:
    conn = db()
    c = conn.cursor()
    c.execute("SELECT file_id, file_path_local, created_at FROM foto WHERE user_id = ? ORDER BY created_at DESC", (user_id_db,))
    photos = c.fetchall()
    conn.close()
    return photos

def delete_user(user_id_db: int):
    conn = db()
    c = conn.cursor()
    c.execute("SELECT file_path_local FROM foto WHERE user_id = ?", (user_id_db,))
    for (path,) in c.fetchall():
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass
    c.execute("DELETE FROM foto WHERE user_id = ?", (user_id_db,))
    c.execute("DELETE FROM utenti WHERE id = ?", (user_id_db,))
    conn.commit()
    conn.close()

def export_csv_bytes() -> bytes:
    conn = db()
    c = conn.cursor()
    c.execute("SELECT * FROM utenti ORDER BY id DESC")
    rows = c.fetchall()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID_DB", "Telegram_ID", "Lingua", "Risposta1", "Risposta2", "Risposta3", "Risposta4", "Risposta5", "Risposta6", "Risposta7", "Risposta8", "Risposta9", "Risposta10", "Risposta11", "Risposta12", "Risposta13", "Risposta14", "Risposta15", "Risposta16", "Risposta17", "Risposta18", "Risposta19", "Risposta20", "Risposta21", "Risposta22", "Risposta23", "Risposta24", "Foto_Count"])
    for r in rows:
        photos = count_photos(r["id"])
        writer.writerow([r["id"], r["user_id"], r["lingua"] or "", r["risposta1"] or "", r["risposta2"] or "", r["risposta3"] or "", r["risposta4"] or "", r["risposta5"] or "", r["risposta6"] or "", r["risposta7"] or "", r["risposta8"] or "", r["risposta9"] or "", r["risposta10"] or "", r["risposta11"] or "", r["risposta12"] or "", r["risposta13"] or "", r["risposta14"] or "", r["risposta15"] or "", r["risposta16"] or "", r["risposta17"] or "", r["risposta18"] or "", r["risposta19"] or "", r["risposta20"] or "", r["risposta21"] or "", r["risposta22"] or "", r["risposta23"] or "", r["risposta24"] or "", photos])
    output.seek(0)
    return output.read().encode("utf-8")

# ================== ADMIN PANEL ==================
def admin_keyboard(page: int, total: int, search: Optional[str], users):
    kb = []
    for u in users:
        uid = u["id"]
        lingua = u["lingua"] or "-"
        photos = count_photos(uid)
        kb.append([
            InlineKeyboardButton(f"👤 {uid} ({lingua}) • 📷 {photos}", callback_data=f"det_{uid}"),
            InlineKeyboardButton("🗑", callback_data=f"delask_{uid}")
        ])
    kb.append([InlineKeyboardButton("📤 Esporta CSV", callback_data="export_csv")])
    max_page = (total - 1) // PAGE_SIZE if total > 0 else 0
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"page_{page-1}"))
    nav.append(InlineKeyboardButton(f"{page+1}/{max_page+1}", callback_data="noop"))
    if page < max_page:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"page_{page+1}"))
    if nav:
        kb.append(nav)
    return InlineKeyboardMarkup(kb)

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Accesso negato.")
        return
    page = 0
    users, total = get_users(offset=0, limit=PAGE_SIZE)
    if total == 0:
        await update.message.reply_text("📂 Nessun utente.")
        return
    await update.message.reply_text("📋 Lista utenti", reply_markup=admin_keyboard(page, total, None, users))

async def admin_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.callback_query.answer("❌ Accesso negato.", show_alert=True)
        return
    q = update.callback_query
    data = q.data

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        users, total = get_users(offset=page*PAGE_SIZE, limit=PAGE_SIZE)
        try:
            await q.message.edit_reply_markup(reply_markup=admin_keyboard(page, total, None, users))
        except Exception:
            await q.message.reply_text("📋 Lista utenti", reply_markup=admin_keyboard(page, total, None, users))
        await q.answer()
        return

    if data.startswith("det_"):
        user_id_db = int(data.split("_")[1])
        u = get_user(user_id_db)
        if not u:
            await q.answer("Utente non trovato.", show_alert=True)
            return
        
        photos = get_user_photos(user_id_db)
        n = len(photos)
        
        text = (
            f"🆔 ID DB: {u['id']}\n"
            f"👤 Telegram ID: {u['user_id']}\n"
            f"🌐 Lingua: {u['lingua'] or '-'}\n"
            f"1️⃣ {u['risposta1'] or '-'}\n"
            f"2️⃣ {u['risposta2'] or '-'}\n"
            f"3️⃣ {u['risposta3'] or '-'}\n"
            f"4️⃣ {u['risposta4'] or '-'}\n"
            f"5️⃣ {u['risposta5'] or '-'}\n"
            f"6️⃣ {u['risposta6'] or '-'}\n"
            f"7️⃣ {u['risposta7'] or '-'}\n"
            f"8️⃣ {u['risposta8'] or '-'}\n"
            f"9️⃣ {u['risposta9'] or '-'}\n"
            f"🔟 {u['risposta10'] or '-'}\n"
            f"1️⃣1️⃣ {u['risposta11'] or '-'}\n"
            f"1️⃣2️⃣ {u['risposta12'] or '-'}\n"
            f"1️⃣3️⃣ {u['risposta13'] or '-'}\n"
            f"1️⃣4️⃣ {u['risposta14'] or '-'}\n"
            f"1️⃣5️⃣ {u['risposta15'] or '-'}\n"
            f"1️⃣6️⃣ {u['risposta16'] or '-'}\n"
            f"1️⃣7️⃣ {u['risposta17'] or '-'}\n"
            f"1️⃣8️⃣ {u['risposta18'] or '-'}\n"
            f"1️⃣9️⃣ {u['risposta19'] or '-'}\n"
            f"2️⃣0️⃣ {u['risposta20'] or '-'}\n"
            f"2️⃣1️⃣ {u['risposta21'] or '-'}\n"
            f"2️⃣2️⃣ {u['risposta22'] or '-'}\n"
            f"2️⃣3️⃣ {u['risposta23'] or '-'}\n"
            f"2️⃣4️⃣ {u['risposta24'] or '-'}\n"
            f"📷 Foto: {n}"
        )
        
        kb = []
        if photos:
            kb.append([InlineKeyboardButton("📸 Vedi Foto", callback_data=f"photos_{user_id_db}")])
        kb.append([InlineKeyboardButton("🗑 Elimina", callback_data=f"delask_{user_id_db}")])
        kb.append([InlineKeyboardButton("🔙 Indietro", callback_data="page_0")])
        
        await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
        await q.answer()
        return

    if data.startswith("photos_"):
        user_id_db = int(data.split("_")[1])
        photos = get_user_photos(user_id_db)
        
        if not photos:
            await q.answer("Nessuna foto trovata per questo utente.", show_alert=True)
            return
        
        await q.answer("Invio foto in corso...")
        
        for i, photo in enumerate(photos):
            file_id, file_path, created_at = photo
            try:
                await q.message.reply_photo(
                    photo=file_id,
                    caption=f"Foto {i+1}/{len(photos)} - {created_at[:10]}"
                )
            except Exception:
                try:
                    if file_path and os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            await q.message.reply_photo(
                                photo=f,
                                caption=f"Foto {i+1}/{len(photos)} - {created_at[:10]}"
                            )
                except Exception as e:
                    await q.message.reply_text(f"❌ Errore nell'inviare la foto {i+1}: {str(e)}")
        
        kb = [
            [InlineKeyboardButton("📥 Scarica tutte le foto", callback_data=f"zip_{user_id_db}")],
            [InlineKeyboardButton("🔙 Torna all'utente", callback_data=f"det_{user_id_db}")]
        ]
        await q.message.reply_text(
            f"✅ Invio foto completato! {len(photos)} foto inviate.",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return

    if data.startswith("zip_"):
        user_id_db = int(data.split("_")[1])
        photos = get_user_photos(user_id_db)
        
        if not photos:
            await q.answer("Nessuna foto da scaricare.", show_alert=True)
            return
        
        await q.answer("Creazione archivio in corso...")
        
        try:
            import zipfile
            from datetime import datetime
            
            zip_filename = f"foto_utente_{user_id_db}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            zip_path = os.path.join(MEDIA_DIR, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for i, photo in enumerate(photos):
                    file_id, file_path, created_at = photo
                    if file_path and os.path.exists(file_path):
                        arcname = f"foto_{i+1}_{created_at[:10]}.jpg"
                        zipf.write(file_path, arcname)
            
            with open(zip_path, 'rb') as f:
                await q.message.reply_document(
                    document=InputFile(f, filename=zip_filename),
                    caption=f"📦 Archivio con {len(photos)} foto dell'utente {user_id_db}"
                )
            
            os.remove(zip_path)
            
        except Exception as e:
            await q.message.reply_text(f"❌ Errore nella creazione dell'archivio: {str(e)}")
        
        await q.answer()
        return

    if data.startswith("delask_"):
        user_id_db = int(data.split("_")[1])
        u = get_user(user_id_db)
        if not u:
            await q.answer("Utente non trovato.", show_alert=True)
            return
        kb = [
            [
                InlineKeyboardButton("✅ Conferma", callback_data=f"del_{user_id_db}"),
                InlineKeyboardButton("❌ Annulla", callback_data="cancel_del")
            ]
        ]
        await q.message.reply_text(f"⚠️ Eliminare definitivamente l'utente {user_id_db}?", reply_markup=InlineKeyboardMarkup(kb))
        await q.answer()
        return

    if data.startswith("del_"):
        user_id_db = int(data.split("_")[1])
        delete_user(user_id_db)
        await q.message.reply_text(f"✅ Utente {user_id_db} eliminato.")
        await q.answer()
        return

    if data == "cancel_del":
        await q.answer("Operazione annullata.")
        return

    if data == "export_csv":
        csv_bytes = export_csv_bytes()
        await q.message.reply_document(
            document=InputFile(BytesIO(csv_bytes), filename="utenti.csv"),
            caption="📤 CSV esportato."
        )
        await q.answer()
        return

    if data == "noop":
        await q.answer()
        return

# ================== GESTIONE FOTO ==================
async def handle_user_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return
    user_id_db = upsert_user(update.effective_user.id)
    photo = update.message.photo[-1]
    file_id = photo.file_id
    file = await context.bot.get_file(file_id)
    filename = f"{user_id_db}_{datetime.utcnow().isoformat(timespec='seconds').replace(':','-')}.jpg"
    local_path = os.path.join(MEDIA_DIR, filename)
    await file.download_to_drive(local_path)
    conn = db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO foto (user_id, file_id, file_path_local, created_at) VALUES (?, ?, ?, ?)",
        (user_id_db, file_id, local_path, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()
    await update.message.reply_text("📸 Foto salvata.")

# ================== FLUSSO UTENTE (/start) ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("✅ Accetto", callback_data="accetto")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Prima di continuare, devi accettare i Termini e Condizioni:\n"
        "• Regolamento: https://rednight.ch/regolamento/\n"
        "• Privacy Policy: https://rednight.ch/privacy-policy/",
        reply_markup=reply_markup
    )
    return TERMINI

async def accetta_termini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🇮🇹 Italiano", callback_data="lingua_it")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lingua_en")],
        [InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lingua_de")],
        [InlineKeyboardButton("🇫🇷 Français", callback_data="lingua_fr")]
    ]
    await query.edit_message_text("Seleziona la tua lingua:", reply_markup=InlineKeyboardMarkup(keyboard))
    return LINGUA

async def scegli_lingua(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lingua = query.data.replace("lingua_", "")
    context.user_data["lingua"] = lingua
    user_id_db = upsert_user(query.from_user.id)
    set_user_field(user_id_db, "lingua", lingua)
    await query.answer()
    await query.edit_message_text(
        "Benvenuto/a su RedNight.ch!\n"
        "Grazie per averci contattato. Nei prossimi passi ti chiederemo alcune informazioni "
        "per poter procedere alla pubblicazione del tuo annuncio sul nostro sito."
    )
    await query.message.reply_text(DOMANDE[lingua][0])
    return DOMANDA1

# Funzioni per gestire tutte le 24 domande
async def domanda1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta1", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][1])
    return DOMANDA2

async def domanda2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta2", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][2])
    return DOMANDA3

async def domanda3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta3", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][3])
    return DOMANDA4

async def domanda4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta4", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][4])
    return DOMANDA5

async def domanda5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta5", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][5])
    return DOMANDA6

async def domanda6(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta6", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][6])
    return DOMANDA7

async def domanda7(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta7", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][7])
    return DOMANDA8

async def domanda8(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta8", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][8])
    return DOMANDA9

async def domanda9(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta9", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][9])
    return DOMANDA10

async def domanda10(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta10", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][10])
    return DOMANDA11

async def domanda11(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta11", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][11])
    return DOMANDA12

async def domanda12(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta12", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][12])
    return DOMANDA13

async def domanda13(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta13", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][13])
    return DOMANDA14

async def domanda14(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta14", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][14])
    return DOMANDA15

async def domanda15(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta15", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][15])
    return DOMANDA16

async def domanda16(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta16", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][16])
    return DOMANDA17

async def domanda17(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta17", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][17])
    return DOMANDA18

async def domanda18(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta18", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][18])
    return DOMANDA19

async def domanda19(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta19", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][19])
    return DOMANDA20

async def domanda20(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta20", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][20])
    return DOMANDA21

async def domanda21(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta21", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][21])
    return DOMANDA22

async def domanda22(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta22", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][22])
    return DOMANDA23

async def domanda23(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta23", update.message.text)
    lingua = context.user_data.get("lingua", "it")
    await update.message.reply_text(DOMANDE[lingua][23])
    return DOMANDA24

async def domanda24(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_db = upsert_user(update.message.from_user.id)
    set_user_field(user_id_db, "risposta24", update.message.text)
    await update.message.reply_text("✅ Grazie! Abbiamo ricevuto tutte le informazioni.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operazione annullata.")
    return ConversationHandler.END

# ================== MAIN LOOP ==================
# Costruiamo Application direttamente nel blocco __main__
application = Application.builder().token(TOKEN).build()

if __name__ == "__main__":
    init_db()

    # Conversation per /start
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TERMINI: [CallbackQueryHandler(accetta_termini, pattern="^accetto$")],
            LINGUA: [CallbackQueryHandler(scegli_lingua, pattern="^lingua_(it|en|de|fr)$")],
            DOMANDA1: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda1)],
            DOMANDA2: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda2)],
            DOMANDA3: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda3)],
            DOMANDA4: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda4)],
            DOMANDA5: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda5)],
            DOMANDA6: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda6)],
            DOMANDA7: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda7)],
            DOMANDA8: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda8)],
            DOMANDA9: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda9)],
            DOMANDA10: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda10)],
            DOMANDA11: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda11)],
            DOMANDA12: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda12)],
            DOMANDA13: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda13)],
            DOMANDA14: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda14)],
            DOMANDA15: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda15)],
            DOMANDA16: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda16)],
            DOMANDA17: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda17)],
            DOMANDA18: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda18)],
            DOMANDA19: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda19)],
            DOMANDA20: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda20)],
            DOMANDA21: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda21)],
            DOMANDA22: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda22)],
            DOMANDA23: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda23)],
            DOMANDA24: [MessageHandler(filters.TEXT & ~filters.COMMAND, domanda24)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    # Handlers admin e media
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("admin", admin_cmd))
    application.add_handler(CallbackQueryHandler(admin_cb, pattern="^(page_|det_|delask_|del_|cancel_del|export_csv|photos_|zip_|noop)"))
    application.add_handler(MessageHandler(filters.PHOTO, handle_user_photo))

    # imposta il webhook
    import asyncio
    async def set_webhook():
        await application.bot.set_webhook(WEBHOOK_URL)
        print(f"✅ Webhook impostato su {WEBHOOK_URL}")

    asyncio.run(set_webhook())

    # avvia Flask
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
