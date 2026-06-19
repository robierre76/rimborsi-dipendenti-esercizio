# Piano: aggiornamento massimali e plafond mensile (Sezione 2, dal 01/01/2026)

## Contesto

La Circolare MEF n. 18/2026 ridetermina, con decorrenza 01/01/2026, i massimali giornalieri di esenzione
e il plafond mensile complessivo per i rimborsi spese dei dipendenti. Le spese con data di sostenimento
fino al 31/12/2025 restano assoggettate ai valori previgenti (Circolare n. 41/2024). Questa modifica
riguarda solo la Sezione 2 della circolare; le altre novità (lavoro agile, riduzione progressiva estero,
incompatibilità) sono escluse dal presente intervento. Il file `data/richieste.json` non viene toccato.

---

## File da modificare

### 1. `src/rules.py`

Introdurre due dizionari distinti per i massimali e due costanti separate per km, notte e plafond:

```python
# Valori previgenti — spese fino al 31/12/2025
MASSIMALI_GIORNALIERI_2025 = {
    "trasferta_italia": 46.48,
    "trasferta_estero": 77.47,
    "pasto": 8.00,
}
MASSIMALE_KM_2025    = 0.42
MASSIMALE_NOTTE_2025 = 150.00
PLAFOND_MENSILE_2025 = 1200.00

# Valori aggiornati — spese dal 01/01/2026
MASSIMALI_GIORNALIERI_2026 = {
    "trasferta_italia": 50.00,
    "trasferta_estero": 85.00,
    "pasto": 10.00,
}
MASSIMALE_KM_2026    = 0.45
MASSIMALE_NOTTE_2026 = 170.00
PLAFOND_MENSILE_2026 = 1400.00
```

Aggiungere una funzione helper che restituisce il set corretto in base all'anno della data:

```python
def parametri_per_data(data_iso: str) -> dict:
    """Restituisce massimali e plafond vigenti alla data indicata."""
    anno = int(data_iso[:4])
    if anno >= 2026:
        return dict(
            massimali_giornalieri=MASSIMALI_GIORNALIERI_2026,
            massimale_km=MASSIMALE_KM_2026,
            massimale_notte=MASSIMALE_NOTTE_2026,
            plafond_mensile=PLAFOND_MENSILE_2026,
        )
    return dict(
        massimali_giornalieri=MASSIMALI_GIORNALIERI_2025,
        massimale_km=MASSIMALE_KM_2025,
        massimale_notte=MASSIMALE_NOTTE_2025,
        plafond_mensile=PLAFOND_MENSILE_2025,
    )
```

Mantenere `MASSIMALI_GIORNALIERI`, `MASSIMALE_KM`, `MASSIMALE_NOTTE`, `PLAFOND_MENSILE` come
alias ai valori 2025 per non rompere eventuali riferimenti esterni non coperti dai test.
Aggiornare `RIFERIMENTO_NORMATIVO = "Circolare MEF n. 18/2026"`.

---

### 2. `src/calculator.py`

`massimale_teorico(richiesta)` e `calcola(richiesta, esente_gia_riconosciuta)` leggono la data
dalla richiesta e delegano la selezione dei parametri a `rules.parametri_per_data()`.
Le firme non cambiano; i chiamanti in `app.py` e `storage.py` non sono impattati.

```python
def massimale_teorico(richiesta):
    p = rules.parametri_per_data(richiesta["data"])
    categoria = richiesta["categoria"]
    if categoria in rules.CATEGORIE_A_GIORNATE:
        return round(p["massimali_giornalieri"][categoria] * richiesta["giorni"], 2)
    if categoria == "chilometrico":
        return round(p["massimale_km"] * richiesta["km"], 2)
    if categoria == "alloggio":
        return round(p["massimale_notte"] * richiesta["notti"], 2)
    raise ValueError(f"categoria non gestita: {categoria}")


def calcola(richiesta, esente_gia_riconosciuta):
    p = rules.parametri_per_data(richiesta["data"])
    importo = richiesta["importo"]
    teorico = massimale_teorico(richiesta)
    esente_teorica = min(importo, teorico)
    capienza = max(p["plafond_mensile"] - esente_gia_riconosciuta, 0.0)
    esente = round(min(esente_teorica, capienza), 2)
    imponibile = round(importo - esente, 2)
    dettaglio = {
        "massimale_teorico": teorico,
        "esente_teorica": round(esente_teorica, 2),
        "capienza_plafond": round(capienza, 2),
    }
    return esente, imponibile, dettaglio
```

---

### 3. `src/templates/normativa.html` *(minore)*

Aggiornare i valori visualizzati nella pagina normativa per riflettere i nuovi massimali 2026.
Non è necessario mostrare entrambe le colonne; basta aggiornare i valori correnti.

---

## Impatto sui test esistenti

Tutti i test esistenti usano `"data": "2025-10-06"` → selezionano i massimali 2025 → **nessun test si rompe**.
Diventano la suite di regressione per il regime transitorio.

---

## Nuovi test da aggiungere in `tests/test_calculator.py`

Aggiungere un fixture `richiesta_2026()` con `"data": "2026-03-10"` e due nuove classi:

### `TestMassimaleTeorico2026`
| Test | Calcolo | Atteso |
|---|---|---|
| `test_trasferta_italia_2026` | 4 × 50,00 | 200,00 |
| `test_trasferta_estero_2026` | 3 × 85,00 | 255,00 |
| `test_pasto_2026` | 5 × 10,00 | 50,00 |
| `test_chilometrico_2026` | 250 × 0,45 | 112,50 |
| `test_alloggio_2026` | 2 × 170,00 | 340,00 |

### `TestCalcola2026`
| Test | Scenario | Atteso |
|---|---|---|
| `test_plafond_2026_esaurito` | `esente_gia_riconosciuta=1400.0`, pasto 1 giorno | esente=0,0 imponibile=10,0 |
| `test_plafond_2026_incapiente` | `esente_gia_riconosciuta=1350.0`, pasto 5 giorni importo 50,00 | esente=50,0 imponibile=0,0 (capienza=50,0) |
| `test_transitorio_data_2025` | data 2025-12-31, `esente_gia_riconosciuta=1200.0`, pasto 1 giorno | esente=0,0 (plafond 2025 esaurito) |

---

## Verifica

```bash
pytest          # tutti i test devono passare (vecchi + nuovi)
pytest -v       # dettaglio per classe
```

Avviare anche l'app (`flask --app src.app run --debug`) e verificare la pagina `/normativa`
per controllare che i valori visualizzati siano aggiornati.
