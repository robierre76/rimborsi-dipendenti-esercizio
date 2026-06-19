from src import calculator


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


class TestMassimaleTeorico:
    def test_trasferta_italia(self):
        r = richiesta(categoria="trasferta_italia", giorni=4)
        assert calculator.massimale_teorico(r) == 185.92

    def test_trasferta_estero(self):
        r = richiesta(categoria="trasferta_estero", giorni=3)
        assert calculator.massimale_teorico(r) == 232.41

    def test_pasto(self):
        r = richiesta(categoria="pasto", giorni=5)
        assert calculator.massimale_teorico(r) == 40.0

    def test_chilometrico(self):
        r = richiesta(categoria="chilometrico", km=250)
        assert calculator.massimale_teorico(r) == 105.0

    def test_alloggio(self):
        r = richiesta(categoria="alloggio", notti=2)
        assert calculator.massimale_teorico(r) == 300.0


class TestCalcola:
    def test_importo_sotto_massimale_tutto_esente(self):
        r = richiesta(categoria="pasto", giorni=5, importo=35.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
        assert esente == 35.0
        assert imponibile == 0.0

    def test_importo_sopra_massimale_eccedenza_imponibile(self):
        r = richiesta(categoria="trasferta_italia", giorni=2, importo=120.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
        assert esente == 92.96
        assert imponibile == 27.04

    def test_plafond_incapiente_limita_la_quota_esente(self):
        r = richiesta(categoria="alloggio", notti=2, importo=300.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1100.0)
        assert esente == 100.0
        assert imponibile == 200.0

    def test_plafond_esaurito_tutto_imponibile(self):
        r = richiesta(categoria="pasto", giorni=1, importo=8.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1200.0)
        assert esente == 0.0
        assert imponibile == 8.0

    def test_dettaglio_del_calcolo(self):
        r = richiesta(categoria="trasferta_estero", giorni=2, importo=200.0)
        _, _, dettaglio = calculator.calcola(r, esente_gia_riconosciuta=1100.0)
        assert dettaglio == {
            "massimale_teorico": 154.94,
            "esente_teorica": 154.94,
            "capienza_plafond": 100.0,
        }


def richiesta_2026(**campi):
    base = {
        "dipendente": "Maria Rossi",
        "data": "2026-03-10",
        "categoria": "pasto",
        "importo": 10.0,
        "giorni": 1,
        "km": None,
        "notti": None,
    }
    base.update(campi)
    return base


class TestMassimaleTeorico2026:
    def test_trasferta_italia_2026(self):
        r = richiesta_2026(categoria="trasferta_italia", giorni=4)
        assert calculator.massimale_teorico(r) == 200.00

    def test_trasferta_estero_2026(self):
        r = richiesta_2026(categoria="trasferta_estero", giorni=3)
        assert calculator.massimale_teorico(r) == 255.00

    def test_pasto_2026(self):
        r = richiesta_2026(categoria="pasto", giorni=5)
        assert calculator.massimale_teorico(r) == 50.00

    def test_chilometrico_2026(self):
        r = richiesta_2026(categoria="chilometrico", km=250)
        assert calculator.massimale_teorico(r) == 112.50

    def test_alloggio_2026(self):
        r = richiesta_2026(categoria="alloggio", notti=2)
        assert calculator.massimale_teorico(r) == 340.00

    def test_trasferta_estero_5gg_esatte_no_riduzione(self):
        # 5 giornate: riduzione non si applica → 5 × 85.00
        r = richiesta_2026(categoria="trasferta_estero", giorni=5)
        assert calculator.massimale_teorico(r) == 425.00

    def test_trasferta_estero_6gg_riduzione_parziale(self):
        # (5×85) + (1×76.50) = 501.50
        r = richiesta_2026(categoria="trasferta_estero", giorni=6)
        assert calculator.massimale_teorico(r) == 501.50

    def test_trasferta_estero_12gg_riduzione_progressiva(self):
        # (5×85) + (5×76.50) + (2×68) = 425 + 382.50 + 136 = 943.50
        r = richiesta_2026(categoria="trasferta_estero", giorni=12)
        assert calculator.massimale_teorico(r) == 943.50

    def test_trasferta_estero_2025_no_riduzione(self):
        # data 2025: massimale costante 77.47 × 8 = 619.76
        r = richiesta_2026(data="2025-06-01", categoria="trasferta_estero", giorni=8)
        assert calculator.massimale_teorico(r) == 619.76


class TestCalcola2026:
    def test_plafond_2026_esaurito(self):
        r = richiesta_2026(categoria="pasto", giorni=1, importo=10.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1400.0)
        assert esente == 0.0
        assert imponibile == 10.0

    def test_plafond_2026_incapiente(self):
        r = richiesta_2026(categoria="pasto", giorni=5, importo=50.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1350.0)
        assert esente == 50.0
        assert imponibile == 0.0

    def test_lavoro_agile_entro_limite(self):
        r = richiesta_2026(categoria="lavoro_agile", giorni=6, importo=21.00)
        # 8 giornate già rimborsate → ammesse min(6, 12-8) = 4 → massimale 14.00
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0, giornate_agile_gia_rimborsate=8)
        assert esente == 14.00
        assert imponibile == 7.00

    def test_lavoro_agile_oltre_limite_mensile(self):
        r = richiesta_2026(categoria="lavoro_agile", giorni=15, importo=52.50)
        # nessuna giornata precedente → ammesse min(15, 12) = 12 → massimale 42.00
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0, giornate_agile_gia_rimborsate=0)
        assert esente == 42.00
        assert imponibile == 10.50

    def test_transitorio_data_2025_usa_vecchi_massimali(self):
        r = richiesta_2026(data="2025-12-31", categoria="pasto", giorni=1, importo=8.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1200.0)
        assert esente == 0.0
        assert imponibile == 8.0
