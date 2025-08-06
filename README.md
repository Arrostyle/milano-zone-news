# Milano News Monitor - San Carlo Zones

🍟 **Web app per monitoraggio notizie delle zone di lavoro San Carlo a Milano**

Monitora automaticamente le notizie di 9 zone specifiche di Milano con aggiornamenti orari, filtri avanzati, sistema di preferiti e oltre 125 variazioni sinonimiche per massima copertura.

## 🎯 Zone Monitorate

1. **Navigli** - Con 14 variazioni (navigli, naviglio grande, zona navigli, aperitivo navigli, etc.)
2. **Darsena** - Con 11 variazioni (darsena milano, piazza xxiv maggio, ponte porta ticinese, etc.)
3. **Porta Ticinese** - Con 11 variazioni (ticinese, colonne san lorenzo, basilica san lorenzo, etc.)
4. **Via Tortona** - Con 13 variazioni (design district tortona, fuorisalone tortona, mudec, etc.)
5. **Via Cassala** - Con 11 variazioni (naviglio pavese cassala, fermata cassala, etc.)
6. **Via Bligny** - Con 10 variazioni (corso lodi bligny, san gottardo bligny, etc.)
7. **Piazza Napoli** - Con 12 variazioni (fermata napoli, metro napoli, etc.)
8. **Corso San Gottardo** - Con 13 variazioni (san gottardo, ticinese san gottardo, etc.)
9. **Via Giuseppe Meda** - Con 14 variazioni (meda, corso lodi meda, romana meda, etc.)

## ✨ Funzionalità

- **Aggiornamento automatico orario** delle notizie
- **Filtro per zona** - Visualizza notizie di zone specifiche
- **Filtro per data** - Organizzazione giorno per giorno
- **Sistema preferiti** - Salva notizie importanti
- **Link cliccabili** - Accesso diretto agli articoli originali
- **Design responsive** - Ottimizzato per mobile e desktop
- **125+ sinonimi** - Massima copertura delle notizie rilevanti
- **Statistiche in tempo reale** - Contatori e metriche

## 🚀 Guida Deployment su Railway (Passo-Passo)

### Step 1: Ottieni API Key da NewsData.io

1. Vai su [NewsData.io](https://newsdata.io)
2. Registrati o effettua login
3. Vai alla sezione "API Keys" nel tuo dashboard
4. Copia la tua API key (inizia con `pub_`)

### Step 2: Download dei File

1. **Scarica tutti i file** dalla cartella `milano_news_deploy`:
   - `app.py` - Server Flask principale
   - `milano_news_backend.py` - Backend con 125+ sinonimi
   - `requirements.txt` - Dipendenze Python
   - `Procfile` - Configurazione Railway
   - `railway.json` - Configurazione Railway
   - `.env.example` - Template variabili ambiente
   - `templates/index.html` - Frontend responsivo

### Step 3: Caricamento su Railway

1. **Vai su [Railway.app](https://railway.app)**
2. **Login** con il tuo account
3. **Clicca "New Project"**
4. **Seleziona "Empty Project"**
5. **Clicca sul servizio creato**
6. **Vai alla tab "Settings"**
7. **Nella sezione "Service"**, clicca **"Connect Repo"**
8. **Seleziona "Deploy from GitHub repo"** o **"Upload files"**

#### Opzione A: Upload Manuale Files
1. **Clicca "Deploy from GitHub repo"**
2. **Seleziona "Create repo from template"**
3. **Carica i file uno per uno** usando l'interfaccia web
4. **Mantieni la struttura delle cartelle**: 
   - File nella root: `app.py`, `milano_news_backend.py`, etc.
   - File HTML in: `templates/index.html`

#### Opzione B: GitHub Repository (Consigliato)
1. **Crea un repository su GitHub**
2. **Carica tutti i file** mantenendo la struttura:
```
repository/
├── app.py
├── milano_news_backend.py
├── requirements.txt
├── Procfile
├── railway.json
├── .env.example
└── templates/
    └── index.html
```
3. **Su Railway, connetti il repository**

### Step 4: Configurazione Environment Variables

1. **Nel tuo progetto Railway**, vai alla tab **"Variables"**
2. **Clicca "Add Variable"**
3. **Aggiungi questa variabile**:
   - **Name**: `NEWSDATA_API_KEY`
   - **Value**: La tua API key da NewsData.io (es: `pub_12345abcdefg...`)
4. **Clicca "Save"**

### Step 5: Deploy e Test

1. **Il deploy partirà automaticamente** dopo il caricamento
2. **Attendi il completamento** (circa 2-3 minuti)
3. **Clicca "View Logs"** per monitorare il processo
4. **Una volta completato**, clicca sull'URL generato
5. **Testa l'applicazione**:
   - Verifica che carichi le notizie
   - Prova i filtri per zona
   - Testa il sistema preferiti
   - Verifica l'aggiornamento manuale

### Step 6: Verifica Funzionalità

✅ **Checklist di test**:
- [ ] App si carica correttamente
- [ ] Le notizie vengono recuperate
- [ ] I filtri per zona funzionano
- [ ] Il sistema preferiti funziona
- [ ] I link alle notizie sono cliccabili
- [ ] L'aggiornamento manuale funziona
- [ ] Il design è responsive su mobile

## 🛠️ Risoluzione Problemi

### Errore "NEWSDATA_API_KEY not found"
- Verifica di aver aggiunto la variabile ambiente su Railway
- Controlla che il nome sia esattamente `NEWSDATA_API_KEY`
- Riavvia il servizio dopo aver aggiunto la variabile

### Errore di deployment
- Verifica che tutti i file siano presenti
- Controlla i logs su Railway per errori specifici
- Assicurati che la struttura delle cartelle sia corretta

### Nessuna notizia visualizzata
- Controlla che la API key sia valida su NewsData.io
- Verifica il limite di richieste della tua API key
- Controlla i logs per errori API

### App lenta o non responsiva
- Normal durante il primo caricamento (cold start)
- Le successive richieste saranno più veloci
- Railway potrebbe mettere l'app in "sleep" se inattiva

## 📁 Struttura Files

```
milano_news_deploy/
├── app.py                    # Flask server con API endpoints
├── milano_news_backend.py    # Core backend con 125+ sinonimi
├── templates/
│   └── index.html           # Frontend HTML responsive
├── requirements.txt          # Dipendenze Python
├── Procfile                 # Comando avvio Railway
├── railway.json             # Configurazione Railway
└── .env.example            # Template variabili ambiente
```

## 🔧 Tecnologie Utilizzate

- **Backend**: Flask + SQLite
- **Frontend**: HTML5 + CSS3 + JavaScript vanilla
- **API**: NewsData.io per recupero notizie
- **Deploy**: Railway.app
- **Server**: Gunicorn WSGI

## 📊 Performance

- **Aggiornamenti**: Ogni ora automaticamente
- **Sinonimi**: 125+ variazioni per massima copertura
- **Database**: SQLite locale con cleanup automatico
- **Retention**: Notizie conservate per 30 giorni
- **Responsive**: Ottimizzato per tutti i dispositivi

## 🆘 Supporto

Per problemi o domande:
1. Controlla i logs su Railway
2. Verifica la configurazione API key
3. Testa la connessione a NewsData.io
4. Controlla la struttura dei file caricati

**Buona fortuna con il tuo lavoro a Milano! 🍟🇮🇹**
