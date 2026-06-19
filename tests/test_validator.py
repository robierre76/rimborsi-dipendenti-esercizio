from src import validator


def richiesta(**campi):
    base = {
        "dipendente": "Maria Rossi",
        "data": "2025-10-06",
        "categoria": "pasto",
        "importo": 10.0,
        "giorni": 1,
        "km": None,
        "notti": None,
    }
    base.update(campi)
    return base


def test_richiesta_valida():
    assert validator.valida(richiesta()) == (True, "")


def test_dipendente_mancante():
    ok, motivazione = validator.valida(richiesta(dipendente=""))
    assert not ok
    assert motivazione == "dipendente mancante"


def test_categoria_non_riconosciuta():
    ok, motivazione = validator.valida(richiesta(categoria="parcheggio"))
    assert not ok
    assert motivazione == "categoria non riconosciuta"


def test_importo_zero():
    ok, motivazione = validator.valida(richiesta(importo=0))
    assert not ok
    assert motivazione == "importo non positivo"


def test_importo_negativo():
    ok, motivazione = validator.valida(richiesta(importo=-5.0))
    assert not ok
    assert motivazione == "importo non positivo"


def test_importo_mancante():
    ok, motivazione = validator.valida(richiesta(importo=None))
    assert not ok
    assert motivazione == "importo non positivo"


def test_data_mancante():
    ok, motivazione = validator.valida(richiesta(data=""))
    assert not ok
    assert motivazione == "data mancante o non valida"


def test_data_non_valida():
    ok, motivazione = validator.valida(richiesta(data="06/10/2025"))
    assert not ok
    assert motivazione == "data mancante o non valida"


def test_giornate_mancanti_per_trasferta():
    ok, motivazione = validator.valida(
        richiesta(categoria="trasferta_italia", giorni=None)
    )
    assert not ok
    assert motivazione == "numero di giornate non valido"


def test_giornate_zero_per_pasto():
    ok, motivazione = validator.valida(richiesta(categoria="pasto", giorni=0))
    assert not ok
    assert motivazione == "numero di giornate non valido"


def test_chilometri_non_validi():
    ok, motivazione = validator.valida(
        richiesta(categoria="chilometrico", km=0)
    )
    assert not ok
    assert motivazione == "numero di chilometri non valido"


def test_notti_non_valide():
    ok, motivazione = validator.valida(
        richiesta(categoria="alloggio", notti=None)
    )
    assert not ok
    assert motivazione == "numero di notti non valido"


def test_chilometrico_valido():
    assert validator.valida(
        richiesta(categoria="chilometrico", km=120, giorni=None)
    ) == (True, "")


def test_alloggio_valido():
    assert validator.valida(
        richiesta(categoria="alloggio", notti=3, giorni=None)
    ) == (True, "")


def test_lavoro_agile_valido_2026():
    assert validator.valida(
        richiesta(categoria="lavoro_agile", data="2026-03-10", giorni=5)
    ) == (True, "")


def test_lavoro_agile_ante_2026_respinto():
    ok, motivazione = validator.valida(
        richiesta(categoria="lavoro_agile", data="2025-12-01", giorni=5)
    )
    assert not ok
    assert motivazione == "categoria non riconosciuta"


def _richiesta_valida_esistente(**campi):
    """Richiesta già registrata come valida, usata nei test di incompatibilità."""
    base = {
        "dipendente": "Maria Rossi",
        "data": "2026-03-02",
        "categoria": "trasferta_italia",
        "importo": 100.0,
        "giorni": 5,
        "km": None,
        "notti": None,
        "stato": "valida",
        "quota_esente": 100.0,
    }
    base.update(campi)
    return base


def test_lavoro_agile_incompatibile_con_trasferta():
    # trasferta nazionale 02/03 → 06/03, lavoro agile 06/03 → 08/03: giornata 06 si sovrappone
    trasferta = _richiesta_valida_esistente(
        categoria="trasferta_italia", data="2026-03-02", giorni=5
    )
    nuova = richiesta(categoria="lavoro_agile", data="2026-03-06", giorni=3)
    ok, motivazione = validator.valida(nuova, [trasferta])
    assert not ok
    assert motivazione == "incompatibilità lavoro agile / trasferta"


def test_trasferta_incompatibile_con_lavoro_agile():
    # lavoro agile 10/03 → 12/03, trasferta estera 12/03: giornata 12 si sovrappone
    agile = _richiesta_valida_esistente(
        categoria="lavoro_agile", data="2026-03-10", giorni=3
    )
    nuova = richiesta(categoria="trasferta_estero", data="2026-03-12", giorni=2)
    ok, motivazione = validator.valida(nuova, [agile])
    assert not ok
    assert motivazione == "incompatibilità lavoro agile / trasferta"


def test_incompatibilita_non_si_applica_al_2025():
    # stessa sovrapposizione ma data 2025: nessun controllo incompatibilità
    trasferta = _richiesta_valida_esistente(
        categoria="trasferta_italia", data="2025-03-02", giorni=5
    )
    nuova = richiesta(categoria="pasto", data="2025-03-04", giorni=1)
    assert validator.valida(nuova, [trasferta]) == (True, "")


def test_richiesta_respinta_non_produce_incompatibilita():
    # una richiesta respinta non blocca la nuova
    trasferta_respinta = _richiesta_valida_esistente(
        categoria="trasferta_italia", data="2026-03-02", giorni=5, stato="respinta"
    )
    nuova = richiesta(categoria="lavoro_agile", data="2026-03-04", giorni=1)
    assert validator.valida(nuova, [trasferta_respinta]) == (True, "")
