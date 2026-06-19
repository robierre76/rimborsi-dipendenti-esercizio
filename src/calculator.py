"""Calcolo della quota esente e della quota imponibile di una richiesta."""

from src import rules


def massimale_teorico(richiesta, giornate_agile_gia_rimborsate=0):
    """Massimale di esenzione applicabile alla richiesta, in base alla categoria e alla data."""
    p = rules.parametri_per_data(richiesta["data"])
    categoria = richiesta["categoria"]
    if categoria == "lavoro_agile":
        giornate_ammesse = min(
            richiesta["giorni"],
            max(rules.MASSIMO_GIORNATE_LAVORO_AGILE - giornate_agile_gia_rimborsate, 0),
        )
        return round(p["massimali_giornalieri"]["lavoro_agile"] * giornate_ammesse, 2)
    if categoria in rules.CATEGORIE_A_GIORNATE:
        return round(p["massimali_giornalieri"][categoria] * richiesta["giorni"], 2)
    if categoria == "chilometrico":
        return round(p["massimale_km"] * richiesta["km"], 2)
    if categoria == "alloggio":
        return round(p["massimale_notte"] * richiesta["notti"], 2)
    raise ValueError(f"categoria non gestita: {categoria}")


def calcola(richiesta, esente_gia_riconosciuta, giornate_agile_gia_rimborsate=0):
    """Restituisce (quota_esente, quota_imponibile, dettaglio).

    `esente_gia_riconosciuta` è la quota esente già riconosciuta al dipendente
    nel mese della richiesta, ai fini del plafond mensile.
    `giornate_agile_gia_rimborsate` è il numero di giornate di lavoro agile già
    rimborsate al dipendente nel mese, ai fini del limite di 12 giornate.
    """
    p = rules.parametri_per_data(richiesta["data"])
    importo = richiesta["importo"]
    teorico = massimale_teorico(richiesta, giornate_agile_gia_rimborsate)
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
