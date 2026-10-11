# Markdown Editor --- Documentazione (Italiano)

[🇬🇧 Read in English](README.md)

Un editor Markdown desktop scritto in Python con interfaccia Tkinter,
editor e anteprima HTML affiancati, aggiornamento automatico durante la
digitazione e strumenti per scrivere e navigare nei documenti Markdown.

> **Nota sul progetto:** questo software è stato *vibe-coded*:
> sviluppato in modo iterativo con l'assistenza di un'intelligenza
> artificiale, attraverso istruzioni in linguaggio naturale, prove e
> modifiche successive.

## Origine e obiettivo del progetto

Il progetto nasce da un'esigenza concreta: un professore universitario
chiedeva che gli esercizi del suo corso fossero scritti e consegnati in
formato Markdown (`.md`). È emerso però un problema pratico: molti
editor Markdown non funzionavano su Windows 7 e gli strumenti
disponibili non offrivano tutti la stessa semplicità d'uso o le stesse
possibilità di modifica e anteprima.

L'obiettivo è offrire un editor desktop semplice e immediato, con il
testo Markdown e l'anteprima formattata affiancati, così da poter
scrivere, modificare e controllare i file in un'unica applicazione.

## Funzionalità

-   Aprire, modificare e salvare file `.md` e `.markdown`.
-   Aprire un file Markdown direttamente con l'applicazione, passando il
    percorso all'avvio o associando l'estensione `.md` all'app in
    Windows.
-   Modificare il testo sorgente e vedere l'anteprima HTML affiancata.
-   Aggiornare automaticamente l'anteprima dopo una breve pausa durante
    la digitazione.
-   Sincronizzare lo scorrimento dell'editor e dell'anteprima.
-   Usare la barra degli strumenti nella parte superiore della finestra
    per applicare la formattazione Markdown.
-   Cercare testo nel documento tramite una finestra di ricerca, con
    evidenziazione delle corrispondenze.
-   Cambiare la lingua dell'interfaccia tra italiano e inglese.
-   Usare un sistema di traduzioni centralizzato predisposto per
    facilitare l'aggiunta di altre lingue.
-   Supportare elementi Markdown come titoli, grassetto, corsivo,
    citazioni, link, liste, tabelle e blocchi di codice, in base alle
    estensioni configurate.
-   Esportazione dei file Markdown (.md) nei formati PDF e HTML.
-   Visualizzare le emoji nell'anteprima come immagini, se è abilitato
    Twemoji. È necessaria una connessione Internet per caricare le
    immagini remote.

## Requisiti

Per eseguire il programma dal codice sorgente:

-   Python 3 compatibile con il sistema operativo in uso.
-   I pacchetti elencati in `requirements.txt`.
-   Tkinter, normalmente incluso nelle distribuzioni Python per Windows.
-   Connessione Internet per le immagini emoji remote, se abilitate.

La compatibilità dipende dalle versioni di Python e delle librerie
installate. Windows 7 è un sistema operativo fuori supporto: versioni
recenti di Python o delle dipendenze potrebbero non essere compatibili.
Usa versioni compatibili con il tuo sistema e scaricale solo da fonti
affidabili.

## Installazione e avvio

Puoi utilizzare Markdown Editor in due modi.

### Opzione 1 --- Versione eseguibile

Apri la sezione
[Releases](https://github.com/arcomipiaceilseno/markdown-win7/releases)
del repository e scarica uno dei pacchetti disponibili per la release
desiderata:

-   **`markdown-win7-installer.exe`** --- versione con installer.
-   **`markdown-win7-portable.exe`** --- versione portable, pensata per
    essere avviata senza una procedura di installazione tradizionale.

La disponibilità dei pacchetti dipende dagli allegati pubblicati nella
release.

### Opzione 2 --- Avvio dal codice sorgente

1.  Scarica o clona il repository.

2.  Apri un terminale nella cartella del progetto, dove si trova
    `main.py`.

3.  Installa le dipendenze, se non sono già installate:

    ``` bash
    py -m pip install -r requirements.txt
    ```

4.  Avvia l'applicazione:

    ``` bash
    py main.py
    ```

    Se il comando `py` non è disponibile, prova:

    ``` bash
    python main.py
    ```

Per aprire direttamente un documento Markdown passando il percorso al
programma:

``` bash
py main.py "C:\percorso\del\documento.md"
```

Sostituisci il percorso di esempio con quello effettivo. L'apertura con
doppio clic da Esplora file richiede che Windows sia configurato per
associare i file `.md` all'applicazione.

## Utilizzo

1.  Avvia il programma oppure apri un file `.md` direttamente con
    l'applicazione.
2.  Per aprire un documento dall'interno del programma, seleziona **File
    → Apri file .md...**.
3.  Scrivi o modifica il Markdown nel pannello dell'editor.
4.  Consulta il risultato nel pannello di anteprima: si aggiorna
    automaticamente dopo una breve pausa.
5.  Usa la barra degli strumenti in alto per inserire la sintassi
    Markdown supportata.
6.  Usa la ricerca per trovare testo nel documento.
7.  Seleziona italiano o inglese dal menu della lingua.
8.  Seleziona **File → Salva** per salvare le modifiche. Per un nuovo
    documento, scegli il percorso quando richiesto.

## Esempio Markdown

``` markdown
# Il mio documento

Questo è un testo **in grassetto** e questo è *in corsivo*.

> Una citazione.

`codice inline`
```

## Emoji e Windows 7

Windows 7 non include il supporto nativo per molte emoji moderne. Nelle
versioni che convertono le emoji in immagini Twemoji, queste possono
apparire nell'anteprima anche se il font di sistema non le supporta. Il
caricamento delle immagini remote richiede una connessione Internet.
Nell'editor del testo sorgente, la resa delle emoji dipende dai font
disponibili.

## Note tecniche e limiti

-   L'anteprima HTML è generata a partire dal Markdown con `markdown2` e
    visualizzata tramite `tkinterweb`.
-   Il ritardo nell'aggiornamento evita di ricostruire l'anteprima a
    ogni singolo tasto.
-   La sincronizzazione dello scorrimento dipende anche dalle
    funzionalità offerte dalla versione installata di `tkinterweb`.
-   La resa di alcune funzionalità Markdown può variare in base alle
    estensioni abilitate e alla versione delle librerie.
-   L'apertura diretta dei file dipende dal percorso passato all'avvio o
    dall'associazione dei file configurata in Windows.
-   La compatibilità con Windows 7 deve essere verificata con le
    versioni specifiche dell'applicazione, di Python e delle dipendenze.
-   Prima di usare il programma con documenti importanti, conserva una
    copia di backup.

## Lingua della documentazione

Sono disponibili `README.it.md` (italiano) e `README.md` (inglese). Il
collegamento in cima a ciascun documento permette di passare all'altra
lingua.

## Contributi

Segnalazioni, correzioni e miglioramenti sono benvenuti. Prima di
proporre modifiche, verifica il funzionamento su una copia del documento
e indica sistema operativo e versioni di Python e dipendenze usate.

## Licenza

MIT License

Copyright (c) 2026 Andrea Scarano

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
