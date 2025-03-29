# Nume:  Antonescu Albert

# Grupă:  333CD

# Tema 1 - Le Stats Sportif (ASC)

---

## Organizare

### Explicație pentru soluția aleasă:

Aplicația este un **server Flask concurent** care procesează cereri de tip API pe baza unui fișier `.csv` cu date statistice despre nutriție și obezitate în SUA între anii 2011–2022.

Modelul urmat este **client-server asincron**, în care cererile nu sunt procesate imediat, ci transformate în **joburi**. Aceste joburi sunt plasate într-o **coadă de taskuri** și preluate de un **ThreadPool**. Fiecare job este rulat de un thread, rezultatul fiind salvat pe disc în folderul `results/`.

Folosesc o clasă `ThreadPool` care pornește un număr configurabil de threaduri (`TP_NUM_OF_THREADS`) și un obiect `Queue()` thread-safe pentru a gestiona joburile.

Pentru sincronizare:
- Am folosit un `Lock()` pentru protejarea accesului la variabilele partajate: `job_counter` și `job_status`.
- Lock-ul este utilizat în toate locurile în care se modifică aceste variabile, pentru a evita race conditions.
- În `graceful_shutdown`, folosesc un `Event()` care semnalează oprirea sistemului de procesare.

Logging-ul este implementat folosind `RotatingFileHandler`, cu timestamp UTC (via `gmtime`) și este activ pe toate rutele importante.

---

### Consideri că tema este utilă?

Da, este o temă extrem de practică și apropiată de cerințele reale ale dezvoltării de API-uri scalabile și asincrone.

---

### Consideri implementarea naivă, eficientă, se putea mai bine?

Implementarea este eficientă, modulară și scalabilă. Se pot adăuga ușor noi endpointuri sau surse de date. Lock-urile sunt folosite strict unde trebuie, iar logarea detaliată ajută la debugging și testare.

---

### Cazuri speciale tratate:

- Dacă serverul este în shutdown mode (`graceful_shutdown`), orice cerere nouă de calcul statistic primește răspuns `"error" : "shutting down"`.
- `get_results` tratează toate cele 3 stări: job invalid, în lucru, finalizat.
- În cazul în care un job generează eroare internă, statusul este marcat `"error"` și logat corespunzător.

---

## Implementare

- ✅ Întregul enunț al temei este **complet implementat**.
- ✅ Toate cele **12 endpointuri** specificate în cerință sunt prezente și funcționale.
- ✅ Implementarea este complet **concurentă**, asincronă și sigură la acces concurent.
- ✅ Este folosit un `ThreadPool` cu coadă `Queue()` și un `Lock()` pentru sincronizarea accesului la `job_counter` și `job_status`.

---

### Funcționalități suplimentare:

Deși nu sunt verificate de checker, următoarele funcționalități au fost implementate complet și testate:

- `/api/graceful_shutdown`: permite oprirea controlată a serverului.
- `/api/get_results/<job_id>`: permite polling-ul statusului unui job.
- `/api/jobs`: listare completă a joburilor cu statusul lor.
- `/api/num_jobs`: verificarea numărului de joburi rămase în coadă.
- `Logging`: toate rutinele importante au mesaje logate folosind un `RotatingFileHandler` în format UTC.

Toate aceste componente au fost testate printr-o **suită extinsă de unittests**, situată în directorul `unittests/`.

---

### Unittests

Am adăugat teste unitare pentru:

- `DataIngestor`: validarea încărcării datelor și a metodelor de procesare.
- `ThreadPool`: testarea execuției corecte a joburilor și salvarea rezultatelor.
- `graceful_shutdown`, `get_results`, `jobs`, `num_jobs`: testate izolat.
- `Logger`: verificarea conținutului logului la accesarea endpointurilor.
- Teste funcționale end-to-end pentru toate celelalte endpointuri (cu polling pentru rezultat).

---

### Dificultăți întâmpinate:

- Gestionarea corectă a sincronizării între multiple threaduri accesând `job_counter` și `job_status` — am rezolvat folosind `threading.Lock()`.
- Înțelegerea clară a cerinței privind `graceful_shutdown` și ce se întâmplă cu cererile primite după activarea sa.
- Menținerea codului modular și lizibil, în timp ce asigur logare, procesare asincronă și tratare completă a erorilor.

### Lucruri interesante descoperite:

- Cum să folosesc `threading.Event` ca mecanism de semnalare și sincronizare între componente ale aplicației.
- Utilitatea unui `ThreadPool` real în Python, chiar și în contextul Flask (care este single-threaded by default).
- Cum pot folosi `RotatingFileHandler` pentru a implementa logging scalabil în aplicații web.

---

## Resurse utilizate

- Documentația oficială Flask și Python
- Laboratoarele de ASC
- Flask Mega Tutorial
- StackOverflow pentru mici clarificări (folosire Lock, json dump în fișier, etc.)
- ChatGPT pentru debug și feedback sincronizare

---

## Git

Repo-ul este privat: https://github.com/AlbertArt10/Le-Stats-Sportif

---

