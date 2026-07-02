# 🎴 Pokémon TCG w liczbach

Interaktywny dashboard w Streamlit analizujący **wszystkie anglojęzyczne karty
Pokémon TCG** wydane od Base Set (1999) do dziś — ponad 20 tysięcy kart ze 170+
setów. Główny wątek analizy: **power creep**, czyli jak przez ~27 lat rosła
siła kart (HP, obrażenia), oraz jak zmieniała się struktura gry (rzadkości,
typy, tempo wydawnicze).

**🔗 Działająca aplikacja:** https://TWOJ-LINK.streamlit.app *(TODO: podmień po deployu)*

## Skąd są dane

Dane pochodzą z oficjalnego repozytorium danych API [pokemontcg.io](https://pokemontcg.io):
[`PokemonTCG/pokemon-tcg-data`](https://github.com/PokemonTCG/pokemon-tcg-data)
(licencja MIT). Skrypt `pobierz_dane.py` ściąga archiwum repo, spłaszcza
zagnieżdżone JSON-y (karty + sety) do jednego CSV i zapisuje go w
`dane/karty_surowe.csv`.

W repo trzymam **snapshot danych** (~2,4 MB) zamiast odpytywać API na żywo —
samo API bywa ostatnio zawodne, a dzięki snapshotowi aplikacja zawsze wstaje
i działa tak samo. Odświeżenie danych to jedno polecenie:

```bash
python pobierz_dane.py
```

## Jak uruchomić lokalnie

```bash
git clone https://github.com/TWOJ-LOGIN/pokemon-tcg-dashboard.git
cd pokemon-tcg-dashboard
pip install -r requirements.txt
streamlit run app.py
```

Albo przez `uv`:

```bash
uv venv && uv pip install -r requirements.txt
uv run streamlit run app.py
```

Aplikacja otworzy się pod `http://localhost:8501`.

## Struktura projektu

```
├── app.py              # orkiestrator: layout, filtry, KPI, zakładki
├── przygotowanie.py    # czyszczenie i przygotowanie danych
├── wykresy.py          # funkcje wykresów (każdy wykres = osobna funkcja)
├── pobierz_dane.py     # pobranie danych ze źródła (uruchamiane raz)
├── dane/
│   └── karty_surowe.csv
└── requirements.txt
```

## Czyszczenie i przygotowanie danych

Surowy CSV celowo zostaje "brudny" — pełne czyszczenie dzieje się w
`przygotowanie.py`, żeby cały krok był widoczny w kodzie:

- konwersja daty wydania (string `1999/01/09` → `datetime`) + kolumna `rok`,
- `hp` → liczba; braki **zostają**, bo niosą informację (karty Trainer
  i Energy z definicji nie mają HP — to nie jest błąd danych),
- brak rzadkości → jawna kategoria `"Brak danych"` (stare sety i promosy),
- obrażenia ataków to stringi typu `"120+"`, `"30×"` — regex wyciąga liczby
  i liczy kolumnę pochodną `max_obrazenia`,
- z listy typów (`Fire|Water`) brany jest typ główny,
- deduplikacja po `id` + sanity check po merge kart z setami,
- serie dostają porządek chronologiczny (`pd.Categorical`), żeby wykresy
  układały się od Base do Mega Evolution, a nie alfabetycznie.

## Co pokazuje dashboard

Filtry (seria, lata, typ, wyszukiwarka nazw) przeliczają na żywo wszystkie
KPI, wykresy i tabelę. 7 typów wykresów: liniowy, słupkowy, histogram,
boxplot, scatter, heatmapa, treemap.

Najciekawsze wnioski:

1. średnie HP karty wzrosło z ~63 (1999) do ~148 (2026) — siła kart
   podwoiła się w ćwierć wieku,
2. liczba rodzajów rzadkości urosła z kilku do kilkudziesięciu — widać
   zmianę modelu wydawniczego pod kolekcjonerów,
3. typy mają swoją oś czasu: Dragon dochodzi w 2011, Fairy istnieje tylko
   w latach 2013–2021,
4. HP i maksymalne obrażenia są mocno skorelowane (r ≈ 0,78), a odstępstwa
   to świadome role kart: tanki i szklane armaty.
