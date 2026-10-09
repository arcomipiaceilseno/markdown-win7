# Markdown Editor — Documentazione (Italiano)

Un editor Markdown desktop scritto in Python con interfaccia Tkinter, anteprima HTML affiancata e aggiornamento automatico durante la digitazione.

> **Nota sul progetto:** questo software è stato *vibe-coded*: sviluppato in modo iterativo con l'assistenza di un'intelligenza artificiale, attraverso istruzioni in linguaggio naturale, prove e modifiche successive. Il codice può essere adattato, controllato e migliorato liberamente secondo la licenza scelta dal repository.

## Origine e obiettivo del progetto

Il progetto nasce da un'esigenza concreta: un professore universitario chiedeva che gli esercizi del suo corso fossero scritti e consegnati in formato Markdown (`.md`). È emerso però un problema pratico: molti editor Markdown non funzionavano su Windows 7, il sistema utilizzato in alcuni contesti, e gli strumenti disponibili non offrivano tutti la stessa semplicità d'uso o le stesse possibilità di modifica e anteprima.

L'obiettivo di questo progetto è quindi offrire un editor desktop semplice e immediato, con il testo Markdown e l'anteprima formattata affiancati, così da poter scrivere, modificare e controllare i file senza dover imparare a usare strumenti diversi o affidarsi a un editor che potrebbe non essere compatibile con il sistema.

## Funzionalità

- Aprire, modificare e salvare file `.md` e `.markdown`.
- Modificare il testo sorgente e vedere l'anteprima formattata affiancata.
- Aggiornare l'anteprima dopo una breve pausa durante la digitazione.
- Usare i comandi di formattazione Markdown disponibili nella barra degli strumenti.
- Supportare elementi Markdown come titoli, grassetto, corsivo, citazioni, link, liste, tabelle e blocchi di codice, in base alle estensioni configurate.
- Mantenere la posizione di scorrimento dell'anteprima, per quanto consentito dal componente HTML.
- Visualizzare le emoji nell'anteprima come immagini, anche su sistemi con supporto emoji limitato, se la versione configurata usa Twemoji. In questo caso è necessaria una connessione Internet per caricare le immagini.

## Requisiti

- Python 3.
- I pacchetti elencati in `requirements.txt`.
- Tkinter, normalmente incluso nelle distribuzioni Python per Windows.
- Connessione Internet per le immagini emoji remote, se abilitate.

La compatibilità dipende dalle versioni di Python e delle librerie installate. Windows 7 è un sistema operativo fuori supporto: l'installazione di versioni recenti di Python o delle dipendenze potrebbe non essere possibile. Usa versioni compatibili con il tuo sistema e installale solo da fonti affidabili.

## Installazione e avvio

Puoi usare il programma in due modi:

### Opzione 1 — Scaricare l'eseguibile

Apri la sezione **Releases** del repository GitHub e scarica l'eseguibile della versione desiderata, se disponibile. In questo modo puoi avviare l'applicazione senza lanciare manualmente lo script Python. Segui eventuali istruzioni incluse nella release.

### Opzione 2 — Avviare il programma con Python

1. Scarica o clona il repository.
2. Apri un terminale nella cartella del progetto, dove si trova `app.py`.
3. Installa le dipendenze, se non sono già installate:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Avvia l'applicazione:

   ```bash
   py app.py
   ```

   In alternativa, se il comando `py` non è disponibile:

   ```bash
   python app.py
   ```

La disponibilità dell'eseguibile dipende dalle release pubblicate nel repository. Per l'avvio da sorgente, devi avere Python e le dipendenze necessarie installati.

## Utilizzo

1. Avvia il programma.
2. Seleziona **File → Apri file .md...** per aprire un documento esistente.
3. Scrivi o modifica il Markdown nel pannello di sinistra.
4. Consulta il risultato nel pannello di destra: l'anteprima si aggiorna automaticamente dopo una breve pausa.
5. Usa la barra degli strumenti per inserire la sintassi Markdown supportata.
6. Seleziona **File → Salva** per salvare le modifiche. Per un nuovo documento, scegli il percorso quando richiesto.

### Esempio Markdown

```markdown
# Il mio documento

Questo è un testo **in grassetto** e questo è *in corsivo*.

> Una citazione.

`codice inline`

```python
def saluta():
    print("Ciao!")
```

- Primo elemento
- Secondo elemento
```

## Emoji e Windows 7

Windows 7 non include il supporto nativo per molte emoji moderne. Nelle versioni che convertono le emoji in immagini Twemoji, queste possono apparire nell'anteprima anche se il font di sistema non le supporta. Il caricamento delle immagini remote richiede una connessione Internet. Nell'editor del testo sorgente, invece, la resa delle emoji dipende dai font disponibili.

## Note tecniche e limiti

- L'anteprima HTML è generata a partire dal Markdown con `markdown2` e visualizzata tramite `tkinterweb`.
- Il ritardo nell'aggiornamento evita di ricostruire l'anteprima a ogni singolo tasto.
- Il mantenimento dello scroll dipende dalle funzionalità offerte dalla versione installata di `tkinterweb`.
- La resa di alcune funzionalità Markdown può variare in base alle estensioni abilitate e alla versione delle librerie.
- Prima di usare il programma con documenti importanti, conserva una copia di backup.

## Cambiare lingua della documentazione

Sono disponibili due documenti: `README.it.md` (italiano) e `README.md` (inglese). Puoi aprire quello che preferisci, oppure impostare il README inglese come pagina principale di GitHub e aggiungere un collegamento all'edizione italiana in cima, e viceversa.

## Contributi

Segnalazioni, correzioni e miglioramenti sono benvenuti. Prima di proporre modifiche, verifica il funzionamento su una copia del documento e indica sistema operativo e versioni di Python/dipendenze usate.

## Licenza

MIT License

Copyright (c) 2026 Andrea Scarano

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
