# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# rimborsi-dipendenti-esercizio

Web app Flask per la gestione dei rimborsi spese dei dipendenti, con calcolo automatico della quota esente IRPEF e del plafond mensile.

## Stack

- **Backend**: Python 3.10+, Flask 3.0+
- **Frontend**: HTML5 (Jinja2), CSS3, vanilla JS
- **Storage**: JSON file (`data/richieste.json`)
- **Test**: pytest 8.0+

## Struttura

```
src/
  app.py          # Flask routes e controller principale
  rules.py        # Parametri normativi (massimali, plafond, categorie)
  calculator.py   # Logica di calcolo quota esente / imponibile
  validator.py    # Validazione richieste
  storage.py      # Persistenza JSON
templates/        # Jinja2 (base, nuova_richiesta, elenco, riepilogo, normativa)
static/           # app.js, style.css
tests/            # test_calculator.py, test_validator.py, test_app.py
data/             # richieste.json
```

## Architettura del calcolo

Il flusso per ogni nuova richiesta è:

1. `validator.valida(richiesta)` → `(ok, motivazione)`
2. Se valida: `storage.esente_riconosciuta_nel_mese(...)` → quota già consumata del plafond
3. `calculator.calcola(richiesta, esente_gia_riconosciuta)` → `(quota_esente, quota_imponibile, dettaglio)`
4. Persistenza su JSON con tutti i campi calcolati

### Categorie supportate (`rules.CATEGORIE`)

| Chiave | Quantità richiesta |
|---|---|
| `trasferta_italia` | `giorni` |
| `trasferta_estero` | `giorni` |
| `pasto` | `giorni` |
| `chilometrico` | `km` |
| `alloggio` | `notti` |

Le categorie in `CATEGORIE_A_GIORNATE` richiedono il campo `giorni` > 0.

### Calcolo quota esente

```
massimale_teorico = massimale_unitario × quantità
esente_teorica    = min(importo, massimale_teorico)
capienza          = max(PLAFOND_MENSILE - esente_già_riconosciuta, 0)
quota_esente      = min(esente_teorica, capienza)
quota_imponibile  = importo - quota_esente
```

## Comandi utili

```bash
# Avvio sviluppo
flask --app src.app run --debug

# Test
pytest

# Test con coverage
pytest --cov=src
```

## Aggiungere un massimale o una categoria

1. Aggiungere il valore in `rules.py`
2. Gestire il caso in `calculator.massimale_teorico()`
3. Aggiungere la validazione in `validator.valida()` se necessario
4. Aggiornare la pagina `normativa.html`
