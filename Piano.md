# Piano: adeguamento alla Circolare MEF n. 18/2026

## Riferimento normativo

Documento completo: [Doc/ITA_circolare_mef_18_2026.pdf](Doc/ITA_circolare_mef_18_2026.pdf)

## Contesto

La Circolare MEF n. 18/2026 (decorrenza 01/01/2026) sostituisce la Circolare n. 41/2024 e introduce:

1. **Sezione 2** — Nuovi massimali giornalieri e plafond mensile
2. **Sezione 3** — Nuova categoria: indennità per lavoro agile (home office)
3. **Sezione 4** — Riduzione progressiva per trasferte estere > 5 giorni
4. **Sezione 5** — Regola di incompatibilità lavoro agile / trasferta
5. **Sezione 7** — Regime transitorio: spese ≤ 31/12/2025 usano i massimali previgenti

Il file `data/richieste.json` non viene toccato.

---

## Sezione 2 — Massimali aggiornati e plafond mensile

### Tabella dei massimali

| Categoria | fino al 31/12/2025 | dal 01/01/2026 |
|---|---|---|
| Trasferta Italia | 46,48 €/giorno | 50,00 €/giorno |
| Trasferta Estero | 77,47 €/giorno | 85,00 €/giorno |
| Rimborso pasto | 8,00 €/giorno | 10,00 €/giorno |
| Rimborso chilometrico | 0,42 €/km | 0,45 €/km |
| Rimborso alloggio | 150,00 €/notte | 170,00 €/notte |
| Indennità lavoro agile | non prevista | 3,50 €/giorno |
| **Plafond mensile** | **1.200,00 €** | **1.400,00 €** |

### Modifiche a `src/rules.py`

- Rinominare le costanti attuali aggiungendo il suffisso `_2025`
- Aggiungere le varianti `_2026` con i nuovi valori
- Mantenere gli alias senza suffisso (es. `MASSIMALI_GIORNALIERI`) puntati ai valori 2025 per compatibilità
- Aggiungere la funzione `parametri_per_data(data_iso)` che seleziona il set corretto in base all'anno della data
- Aggiornare `RIFERIMENTO_NORMATIVO = "Circolare MEF n. 18/2026"`

### Modifiche a `src/calculator.py`

- `massimale_teorico(richiesta)` chiama `rules.parametri_per_data()` per ottenere i massimali corretti
- `calcola(richiesta, esente_gia_riconosciuta)` usa il plafond corretto restituito dalla stessa funzione
- Le firme non cambiano: nessun impatto su `app.py` e `storage.py`

---

## Sezione 3 — Indennità per lavoro agile

### Regole

- Esente fino a **3,50 €/giorno** per giornata di lavoro agile effettivamente svolta
- Massimo **12 giornate per mese di calendario**; le giornate eccedenti sono interamente imponibili
- Le giornate già rimborsate nel mese con richieste valide contano ai fini del limite
- La quota esente concorre al plafond mensile complessivo

### Calcolo

```
giornate_ammesse = min(giorni_richiesti, max(12 - agile_già_rimborsate_nel_mese, 0))
massimale_teorico = 3,50 × giornate_ammesse
```
Poi si applicano i punti 2, 3 e 4 della Sezione 2 (quota esente teorica, capienza plafond, imponibile).

### Modifiche a `src/rules.py`

- Aggiungere `"lavoro_agile"` a `MASSIMALI_GIORNALIERI_2026` con valore `3.50`
- Aggiungere `MASSIMO_GIORNATE_LAVORO_AGILE = 12`
- Aggiungere `"lavoro_agile"` a `CATEGORIE` e a `CATEGORIE_A_GIORNATE`

### Modifiche a `src/storage.py`

- Aggiungere `giornate_agile_riconosciute_nel_mese(richieste, dipendente, mese_riferimento)` che somma i `giorni` delle richieste valide di categoria `lavoro_agile` del dipendente nel mese

### Modifiche a `src/calculator.py`

- `massimale_teorico(richiesta)` per categoria `lavoro_agile`: richiede il parametro aggiuntivo `giornate_agile_gia_rimborsate`; calcola `giornate_ammesse` e moltiplica per 3,50
- Alternativa (preferita): passare `giornate_ammesse` già calcolate da `app.py` prima di chiamare `calcola`

### Modifiche a `src/app.py`

- Prima di chiamare `calculator.calcola`, recuperare da `storage` le giornate agile già rimborsate nel mese e passarle al calcolo

---

## Sezione 4 — Riduzione progressiva trasferte estere > 5 giorni

### Regole (solo per date ≥ 01/01/2026)

```
G1 = min(G, 5)              → G1 × 85,00  (massimale pieno)
G2 = min(max(G - 5, 0), 5)  → G2 × 76,50  (riduzione 10%)
G3 = max(G - 10, 0)         → G3 × 68,00  (riduzione 20%)
massimale_teorico = G1×85 + G2×76,50 + G3×68
```

La riduzione **non si applica** alle trasferte nazionali né alle trasferte con data di inizio ≤ 31/12/2025.

### Modifiche a `src/calculator.py`

- In `massimale_teorico`, per categoria `trasferta_estero` e data ≥ 2026: applicare la formula progressiva anziché `giorni × 85,00`

---

## Sezione 5 — Incompatibilità lavoro agile / trasferta

### Regole (solo per date ≥ 01/01/2026)

- Una richiesta di **lavoro agile** è respinta se almeno una delle sue giornate coincide con una giornata coperta da una trasferta valida (nazionale o estera) dello stesso dipendente
- Una richiesta di **trasferta** è respinta se almeno una delle sue giornate coincide con una giornata di lavoro agile valida dello stesso dipendente
- Il rigetto è **integrale** anche se l'incompatibilità riguarda una sola giornata
- Motivazione: `"incompatibilità lavoro agile / trasferta"`
- Contano solo le richieste **valide**; quelle respinte non producono effetti

### Modifiche a `src/validator.py`

- Aggiungere il parametro `richieste_esistenti` a `valida(richiesta, richieste_esistenti)`
- Per date ≥ 2026, aggiungere il controllo di sovrapposizione giornate tra lavoro agile e trasferte

### Modifiche a `src/storage.py`

- Aggiungere helper per calcolare il range di giornate coperte da una richiesta (data inizio + numero giorni), necessario per il controllo di sovrapposizione

### Modifiche a `src/app.py`

- Passare la lista delle richieste esistenti a `validator.valida`

---

## Sezione 7 — Regime transitorio

| Condizione | Regola applicata |
|---|---|
| Data sostenimento ≤ 31/12/2025 | Massimali 2025, plafond 1.200 €, nessuna riduzione progressiva, nessuna incompatibilità, lavoro agile non ammesso |
| Data sostenimento ≥ 01/01/2026 | Massimali 2026, plafond 1.400 €, riduzione progressiva estero, incompatibilità lavoro agile/trasferta |

La data di sostenimento è la **data di inizio** della trasferta (campo `data` della richiesta). Le richieste già liquidate non sono ricalcolate.

---

## Impatto sui test esistenti

Tutti i test esistenti usano `"data": "2025-10-06"` → selezionano i massimali 2025 → **nessun test si rompe**. Diventano la suite di regressione per il regime transitorio.

---

## Nuovi test da aggiungere

### `tests/test_calculator.py` — fixture `richiesta_2026()` con `"data": "2026-03-10"`

**`TestMassimaleTeorico2026`**

| Test | Calcolo | Atteso |
|---|---|---|
| `test_trasferta_italia_2026` | 4 × 50,00 | 200,00 |
| `test_trasferta_estero_2026` | 3 × 85,00 | 255,00 |
| `test_pasto_2026` | 5 × 10,00 | 50,00 |
| `test_chilometrico_2026` | 250 × 0,45 | 112,50 |
| `test_alloggio_2026` | 2 × 170,00 | 340,00 |
| `test_trasferta_estero_progressiva_6gg` | (5×85)+(1×76,50) | 501,50 |
| `test_trasferta_estero_progressiva_12gg` | (5×85)+(5×76,50)+(2×68) | 943,50 |
| `test_lavoro_agile_entro_limite` | 4 gg ammesse × 3,50 | 14,00 |
| `test_lavoro_agile_oltre_limite_mensile` | min(15,12) × 3,50 | 42,00 |

**`TestCalcola2026`**

| Test | Scenario | Atteso |
|---|---|---|
| `test_plafond_2026_esaurito` | `esente_gia_riconosciuta=1400.0`, pasto 1 giorno | esente=0,0 imponibile=10,0 |
| `test_plafond_2026_incapiente` | `esente_gia_riconosciuta=1350.0`, pasto 5 giorni importo 50,00 | esente=50,0 imponibile=0,0 |
| `test_transitorio_data_2025` | data 2025-12-31, `esente_gia_riconosciuta=1200.0`, pasto 1 giorno | esente=0,0 |

### `tests/test_validator.py`

| Test | Scenario | Atteso |
|---|---|---|
| `test_lavoro_agile_incompatibile_con_trasferta` | lavoro agile con giornata sovrapposta a trasferta valida | respinta, motivazione "incompatibilità lavoro agile / trasferta" |
| `test_trasferta_incompatibile_con_lavoro_agile` | trasferta con giornata sovrapposta a lavoro agile valido | respinta, stessa motivazione |
| `test_lavoro_agile_ante_2026_respinto` | data 2025-12-01, categoria lavoro agile | respinta, "categoria non riconosciuta" |

---

## Verifica

```bash
pytest       # tutti i test devono passare (vecchi + nuovi)
pytest -v    # dettaglio per classe
```

Avviare l'app (`flask --app src.app run --debug`) e verificare:
- Pagina `/normativa`: valori aggiornati ai massimali 2026
- Inserimento richiesta lavoro agile per data 2026: calcolo corretto
- Inserimento richiesta lavoro agile per data 2025: respinta con "categoria non riconosciuta"
- Inserimento trasferta estera > 5 giorni: riduzione progressiva applicata
- Inserimento lavoro agile con giornata sovrapposta a trasferta valida: respinta con incompatibilità
