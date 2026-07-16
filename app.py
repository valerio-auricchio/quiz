import streamlit as st
import json
import os

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Databricks Professional Prep", layout="wide")

DB_FILE = "database_domande.json"
STATE_FILE = "progresso.json"  # usato solo come fallback locale se Supabase non è configurato

# Identificativo del profilo: se un giorno volessi più profili, cambia qui o
# aggiungi un campo. Per uso personale va benissimo lasciarlo così.
PROFILE_ID = "default"

# Stili CSS per rendere l'interfaccia pulita
st.markdown("""
    <style>
    .stButton button { width: 100%; border-radius: 5px; height: 3em; }
    .question-card { background-color: white; padding: 25px; border-radius: 15px; border: 1px solid #e0e0e0; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)


# --- CONNESSIONE A SUPABASE (opzionale) ---
# Se in Streamlit trovi i "secrets" SUPABASE_URL e SUPABASE_KEY, l'app salva i
# progressi nel cloud (sincronizzati tra Mac, iPad e iPhone). Altrimenti usa il
# vecchio file locale progresso.json, così puoi comunque provarla sul tuo Mac.
@st.cache_resource
def get_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        return None
    try:
        from supabase import create_client
        return create_client(url, key)
    except Exception as e:
        st.warning(f"Supabase configurato ma non raggiungibile: {e}. Uso il salvataggio locale.")
        return None


supabase = get_supabase()
USING_CLOUD = supabase is not None


# --- CARICAMENTO DOMANDE ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


# --- GESTIONE STATO (cloud o locale) ---
def default_state():
    return {"current_idx": 0, "correct": 0, "wrong": 0, "wrong_ids": []}


def load_state():
    if USING_CLOUD:
        try:
            res = supabase.table("progresso").select("*").eq("profilo", PROFILE_ID).execute()
            if res.data:
                row = res.data[0]
                return {
                    "current_idx": row.get("current_idx", 0),
                    "correct": row.get("correct", 0),
                    "wrong": row.get("wrong", 0),
                    "wrong_ids": row.get("wrong_ids") or [],
                }
            # Nessuna riga ancora: la creiamo
            new_state = default_state()
            supabase.table("progresso").insert({"profilo": PROFILE_ID, **new_state}).execute()
            return new_state
        except Exception as e:
            st.warning(f"Impossibile leggere i progressi dal cloud: {e}. Uso il salvataggio locale.")
    # Fallback locale
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            saved = json.load(f)
            merged = default_state()
            merged.update(saved)
            return merged
    return default_state()


def save_state(idx, correct, wrong, wrong_ids):
    payload = {"current_idx": idx, "correct": correct, "wrong": wrong, "wrong_ids": wrong_ids}
    if USING_CLOUD:
        try:
            supabase.table("progresso").update(payload).eq("profilo", PROFILE_ID).execute()
            return
        except Exception as e:
            st.warning(f"Impossibile salvare i progressi nel cloud: {e}. Salvo in locale.")
    # Fallback locale
    with open(STATE_FILE, 'w') as f:
        json.dump(payload, f)


def reset_state():
    if USING_CLOUD:
        try:
            supabase.table("progresso").update(
                {"current_idx": 0, "correct": 0, "wrong": 0, "wrong_ids": []}
            ).eq("profilo", PROFILE_ID).execute()
            return
        except Exception as e:
            st.warning(f"Impossibile resettare nel cloud: {e}.")
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)


data = load_data()
state = load_state()

if not data:
    st.error("File 'database_domande.json' non trovato o vuoto. Incolla i dati nel file per iniziare!")
    st.stop()

# Inizializzazione Session State
if 'idx' not in st.session_state:
    st.session_state.idx = state["current_idx"]
    st.session_state.correct = state["correct"]
    st.session_state.wrong = state["wrong"]
    st.session_state.wrong_ids = state["wrong_ids"]
    st.session_state.answered = False
    st.session_state.mode = "normal"
    st.session_state.review_idx = 0

# Sidebar
with st.sidebar:
    st.title("📊 Progressi")
    if USING_CLOUD:
        st.caption("☁️ Sincronizzato nel cloud")
    else:
        st.caption("💾 Salvataggio locale")
    st.metric("Corrette ✅", st.session_state.correct)
    st.metric("Sbagliate ❌", st.session_state.wrong)

    n_wrong = len(st.session_state.wrong_ids)
    st.markdown("---")
    if st.session_state.mode == "review":
        if st.button("🔁 Torna al quiz principale"):
            st.session_state.mode = "normal"
            st.session_state.answered = False
            st.rerun()
    else:
        if st.button(f"📝 Rivedi errori ({n_wrong})", disabled=n_wrong == 0):
            st.session_state.mode = "review"
            st.session_state.review_idx = 0
            st.session_state.answered = False
            st.rerun()

    st.markdown("---")
    if st.button("Reset Totale"):
        reset_state()
        st.session_state.idx = 0
        st.session_state.correct = 0
        st.session_state.wrong = 0
        st.session_state.wrong_ids = []
        st.session_state.answered = False
        st.session_state.mode = "normal"
        st.session_state.review_idx = 0
        st.rerun()

# Layout Principale
st.title("🎓 Databricks Professional Simulator")

if st.session_state.mode == "review":
    queue = [item for item in data if item['id'] in st.session_state.wrong_ids]
    if not queue:
        st.success("Hai rivisto e risolto tutti gli errori! 🎉")
        st.session_state.mode = "normal"
        st.rerun()
    st.session_state.review_idx = st.session_state.review_idx % len(queue)
    q = queue[st.session_state.review_idx]
    st.caption("📝 Modalità ripasso errori")
    st.progress((st.session_state.review_idx + 1) / len(queue))
    widget_key = f"review_{q['id']}"
else:
    st.progress((st.session_state.idx + 1) / len(data))
    q = data[st.session_state.idx]
    widget_key = f"in_{st.session_state.idx}"

st.markdown(f"<div class='question-card'>", unsafe_allow_html=True)
if st.session_state.mode == "review":
    st.write(f"**Ripasso {st.session_state.review_idx + 1} di {len(queue)}** (ID: #{q['id']})")
else:
    st.write(f"**Domanda {st.session_state.idx + 1} di {len(data)}** (ID: #{q['id']})")
st.markdown(f"### {q['question']}")

# Mostra le opzioni se presenti nel JSON
if "options" in q:
    for opt in q["options"]:
        st.write(opt)

user_input = st.text_input("La tua risposta (es: A, B, C, D):", key=widget_key).upper().strip()

if st.button("Conferma"):
    st.session_state.answered = True
    if user_input == q['answer'].upper():
        st.success("✅ Esatto!")
        st.session_state.correct += 1
        if q['id'] in st.session_state.wrong_ids:
            st.session_state.wrong_ids.remove(q['id'])
    else:
        st.error(f"❌ Errato. La risposta corretta è: {q['answer']}")
        st.session_state.wrong += 1
        if q['id'] not in st.session_state.wrong_ids:
            st.session_state.wrong_ids.append(q['id'])
    save_state(st.session_state.idx, st.session_state.correct, st.session_state.wrong, st.session_state.wrong_ids)

if st.session_state.answered:
    st.markdown("---")
    st.markdown("##### 💡 Spiegazione")
    st.info(q['explanation'])
    if st.button("Prossima domanda ➡️"):
        if st.session_state.mode == "review":
            st.session_state.review_idx += 1
        else:
            st.session_state.idx += 1
        st.session_state.answered = False
        save_state(st.session_state.idx, st.session_state.correct, st.session_state.wrong, st.session_state.wrong_ids)
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
