"""Regole di validazione delle richieste di rimborso."""

from datetime import date

from src import rules, storage

CATEGORIE_TRASFERTA = {"trasferta_italia", "trasferta_estero"}


def valida(richiesta, richieste_esistenti=None):
    """Restituisce (True, "") se la richiesta è valida, altrimenti (False, motivazione)."""
    if not richiesta.get("dipendente"):
        return False, "dipendente mancante"

    categoria = richiesta.get("categoria")
    if categoria not in rules.CATEGORIE:
        return False, "categoria non riconosciuta"

    data = richiesta.get("data") or ""
    if categoria == "lavoro_agile" and data[:4] < "2026":
        return False, "categoria non riconosciuta"

    importo = richiesta.get("importo")
    if importo is None or importo <= 0:
        return False, "importo non positivo"

    try:
        date.fromisoformat(richiesta.get("data") or "")
    except ValueError:
        return False, "data mancante o non valida"

    if categoria in rules.CATEGORIE_A_GIORNATE:
        giorni = richiesta.get("giorni")
        if not giorni or giorni <= 0:
            return False, "numero di giornate non valido"

    if categoria == "chilometrico":
        km = richiesta.get("km")
        if not km or km <= 0:
            return False, "numero di chilometri non valido"

    if categoria == "alloggio":
        notti = richiesta.get("notti")
        if not notti or notti <= 0:
            return False, "numero di notti non valido"

    # Incompatibilità lavoro agile / trasferta (solo per date >= 2026)
    if data[:4] >= "2026" and richieste_esistenti is not None:
        if categoria == "lavoro_agile" or categoria in CATEGORIE_TRASFERTA:
            if _incompatibile(richiesta, richieste_esistenti):
                return False, "incompatibilità lavoro agile / trasferta"

    return True, ""


def _incompatibile(richiesta, richieste_esistenti):
    """True se la richiesta si sovrappone a una richiesta valida di categoria incompatibile."""
    categoria = richiesta["categoria"]
    dipendente = richiesta["dipendente"]
    giornate_nuova = storage.giornate_coperte(richiesta)

    if categoria == "lavoro_agile":
        categorie_opposte = CATEGORIE_TRASFERTA
    else:
        categorie_opposte = {"lavoro_agile"}

    for r in richieste_esistenti:
        if r["stato"] != "valida":
            continue
        if r["dipendente"] != dipendente:
            continue
        if r["categoria"] not in categorie_opposte:
            continue
        if giornate_nuova & storage.giornate_coperte(r):
            return True
    return False
