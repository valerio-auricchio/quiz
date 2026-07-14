# Come mettere online il tuo simulatore (gratis) e sincronizzarlo tra Mac, iPad e iPhone

Obiettivo: aprire l'app da un link su qualsiasi dispositivo, con i progressi (domanda corrente, corrette, sbagliate) **sincronizzati** ovunque.

Tutto quello che segue è **gratuito**. Serve circa mezz'ora la prima volta. Non serve saper programmare: è quasi tutto copia-incolla e clic.

I pezzi sono tre:
1. **GitHub** — dove metti i file dell'app (è come un "Drive per codice").
2. **Streamlit Community Cloud** — dove l'app viene eseguita e diventa un link.
3. **Supabase** — il "cassetto in cloud" dove vengono salvati i progressi, uguale per tutti i dispositivi.

---

## Passo 1 — Crea un account GitHub e carica i file

1. Vai su https://github.com e crea un account gratuito (se non ce l'hai).
2. In alto a destra: **+ → New repository**.
   - Nome a piacere, es. `databricks-quiz`.
   - Lascialo **Public** (per il piano gratuito di Streamlit va bene).
   - Clic **Create repository**.
3. Nella pagina del repository vuoto, clic su **"uploading an existing file"** (link al centro).
4. Trascina questi 4 file (te li ho preparati):
   - `app.py`
   - `requirements.txt`
   - `database_domande.json`
   - `progresso.json`  *(facoltativo — serve solo come riserva locale)*
5. In fondo, clic **Commit changes**.

Fatto: i tuoi file sono online.

---

## Passo 2 — Crea il "cassetto in cloud" su Supabase

1. Vai su https://supabase.com → **Start your project** → accedi (puoi usare l'account GitHub).
2. **New project**:
   - Nome a piacere (es. `quiz`).
   - Imposta una password del database (salvala da qualche parte, ma non ti servirà per l'app).
   - Regione: scegline una in Europa (es. Frankfurt).
   - Clic **Create new project** e aspetta ~1 minuto che si avvii.
3. Crea la tabella dei progressi. Nel menù a sinistra apri **SQL Editor**, incolla questo e premi **Run**:

   ```sql
   create table progresso (
     profilo text primary key,
     current_idx int default 0,
     correct int default 0,
     wrong int default 0
   );
   ```

4. Prendi le due chiavi che servono all'app. Menù a sinistra: **Project Settings** (icona ingranaggio) → **API**. Copia e tieni da parte:
   - **Project URL** (una cosa tipo `https://xxxxx.supabase.co`)
   - **anon public** key (una stringa lunga, sotto "Project API keys")

   > Nota: la chiave `anon public` è quella giusta da usare qui. Non condividere online la chiave `service_role`.

---

## Passo 3 — Pubblica l'app su Streamlit Community Cloud

1. Vai su https://share.streamlit.io e accedi con **GitHub** (autorizza l'accesso quando te lo chiede).
2. Clic **Create app** → **Deploy a public app from GitHub**.
3. Compila:
   - **Repository**: scegli `databricks-quiz` (quello del Passo 1).
   - **Branch**: `main`.
   - **Main file path**: `app.py`.
4. Prima di premere Deploy, apri **Advanced settings** e nella casella **Secrets** incolla (sostituendo con i tuoi due valori del Passo 2):

   ```toml
   SUPABASE_URL = "https://xxxxx.supabase.co"
   SUPABASE_KEY = "la-tua-anon-public-key"
   ```

5. Clic **Deploy**. Aspetta 1-2 minuti la prima installazione.

Al termine avrai un link tipo `https://tuo-nome-quiz.streamlit.app`. Nella sidebar dell'app comparirà **"☁️ Sincronizzato nel cloud"**: vuol dire che i progressi ora vanno su Supabase.

---

## Passo 4 — Usala su iPhone e iPad come se fosse un'app

1. Apri il link in **Safari** su iPhone/iPad.
2. Tocca l'icona **Condividi** (quadrato con freccia) → **Aggiungi alla schermata Home**.
3. Ora hai un'icona in home: si apre a schermo intero, sembra un'app vera.

Fai lo stesso sul Mac (Safari → Condividi → Aggiungi al Dock) se vuoi.

Da questo momento: rispondi a una domanda sul Mac, riprendi dall'iPhone e ritrovi lo stesso punto. La sincronizzazione avviene tramite Supabase.

---

## Come cambiare le domande in futuro

Le domande stanno nel file `database_domande.json` dentro GitHub. Per modificarle: apri il file su GitHub → icona matita (Edit) → modifica → **Commit changes**. Streamlit rimette online la versione aggiornata da solo in un minuto.

---

## Se qualcosa non torna

- **Nella sidebar vedo "💾 Salvataggio locale" invece di "☁️ Sincronizzato"** → i secrets non sono stati letti. Su Streamlit: **Manage app → Settings → Secrets**, verifica che `SUPABASE_URL` e `SUPABASE_KEY` siano scritti esattamente come sopra, poi **Reboot** dell'app.
- **Errore rosso all'avvio** → controlla che nel repo ci siano `app.py`, `requirements.txt` e `database_domande.json`.
- **I progressi non si aggiornano tra dispositivi** → assicurati che la tabella `progresso` esista su Supabase (Passo 2.3) e che tutti i dispositivi usino lo stesso link `.streamlit.app`.

---

## Costi

Tutto rientra nei piani gratuiti: GitHub (repo pubblici illimitati), Streamlit Community Cloud (app pubbliche gratis), Supabase (piano free ampiamente sufficiente per uso personale). Nessuna carta di credito richiesta.
