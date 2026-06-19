"""Parametri normativi vigenti per il calcolo dei rimborsi spese.

Fonte: Circolare MEF n. 18/2026, in vigore per l'anno 2026.
Regime transitorio: le spese fino al 31/12/2025 usano i valori della Circolare n. 41/2024.
"""

# Valori previgenti — spese fino al 31/12/2025 (Circolare n. 41/2024)
MASSIMALI_GIORNALIERI_2025 = {
    "trasferta_italia": 46.48,
    "trasferta_estero": 77.47,
    "pasto": 8.00,
}
MASSIMALE_KM_2025    = 0.42
MASSIMALE_NOTTE_2025 = 150.00
PLAFOND_MENSILE_2025 = 1200.00

# Valori aggiornati — spese dal 01/01/2026 (Circolare MEF n. 18/2026)
MASSIMALI_GIORNALIERI_2026 = {
    "trasferta_italia": 50.00,
    "trasferta_estero": 85.00,
    "pasto": 10.00,
}
MASSIMALE_KM_2026    = 0.45
MASSIMALE_NOTTE_2026 = 170.00
PLAFOND_MENSILE_2026 = 1400.00

# Alias ai valori 2025 per compatibilità con riferimenti esistenti
MASSIMALI_GIORNALIERI = MASSIMALI_GIORNALIERI_2025
MASSIMALE_KM          = MASSIMALE_KM_2025
MASSIMALE_NOTTE       = MASSIMALE_NOTTE_2025
PLAFOND_MENSILE       = PLAFOND_MENSILE_2025


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


CATEGORIE = {
    "trasferta_italia": "Trasferta in Italia",
    "trasferta_estero": "Trasferta all'estero",
    "pasto": "Rimborso pasto",
    "chilometrico": "Rimborso chilometrico",
    "alloggio": "Rimborso alloggio",
}

CATEGORIE_A_GIORNATE = ("trasferta_italia", "trasferta_estero", "pasto")

RIFERIMENTO_NORMATIVO = "Circolare MEF n. 18/2026"
