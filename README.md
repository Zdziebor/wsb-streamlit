# 🎴 Pokémon TCG w liczbach

Interaktywny dashboard w aplikacji Streamlit analizujący wszystkie anglojęzyczne karty Pokémon TCG wydane od **Base Set (1999)** do dziś - to baza obejmująca ponad **20 tysięcy kart ze 170+ setów**.

Głównym wątkiem analizy jest **power creep**, czyli badanie, jak przez ~27 lat rosła siła kart (HP, obrażenia) oraz jak zmieniała się struktura samej gry (rzadkości, typy kart, tempo wydawnicze).

🔗 **Działająca aplikacja:** https://wsb-app-spfb7ev43jyunbpg89eujq.streamlit.app

---

## 📊 Co pokazuje dashboard
Wbudowane filtry (seria, lata, typ, wyszukiwarka nazw) przeliczają na żywo wszystkie wskaźniki KPI, wykresy oraz tabelę danych. Dashboard zawiera **7 typów wykresów**: liniowy, słupkowy, histogram, boxplot, scatter plot, heatmapę oraz treemap.

### 💡 Najciekawsze wnioski z analizy:
* **Wzrost siły (Power Creep):** Średnie HP karty wzrosło z `~63` (1999 rok) do `~148` (2026 rok) - siła kart podwoiła się w ciągu ćwierć wieku.
* **Ewolucja rzadkości:** Liczba rodzajów rzadkości urosła z zaledwie kilku do kilkudziesięciu, co wyraźnie pokazuje zmianę modelu wydawniczego pod kątem kolekcjonerów.
* **Oś czasu typów:** Nowe typy pojawiały się i znikały na przestrzeni lat, np. typ *Dragon* dołączył w 2011 roku, a typ *Fairy* istniał tylko w latach 2013–2021.
* **Korelacja statystyk:** Punkty HP i maksymalne obrażenia są ze sobą mocno skorelowane ($r \approx 0.78$). Wyraźne odstępstwa od tej reguły reprezentują świadomie zaprojektowane role kart: "tanki" oraz "szklane armaty".

## 🗂️ Skąd są dane

Dane pochodzą z oficjalnego repozytorium danych API [pokemontcg.io](https://pokemontcg.io) —
[`PokemonTCG/pokemon-tcg-data`](https://github.com/PokemonTCG/pokemon-tcg-data) (licencja MIT).

Skrypt `pobierz_dane.py` ściąga całe repo jako archiwum `.tar.gz`, spłaszcza
zagnieżdżone JSON-y (karty + sety) do jednej tabeli i zapisuje snapshot w
`dane/karty_surowe.csv` (~2,4 MB). W repo trzymam snapshot zamiast odpytywać
API na żywo — dzięki temu aplikacja startuje szybko i zawsze działa tak samo,
niezależnie od dostępności API. Odświeżenie danych to jedno polecenie:

```bash
python pobierz_dane.py
```

## 📁 Struktura projektu

```
├── app.py              # orkiestrator: layout, filtry, KPI, zakładki
├── przygotowanie.py    # czyszczenie i przygotowanie danych
├── wykresy.py          # funkcje wykresów (każdy wykres = osobna funkcja)
├── pobierz_dane.py     # pobranie danych ze źródła (uruchamiane raz)
├── dane/
│   └── karty_surowe.csv
└── requirements.txt
```

## 🧹 Czyszczenie i przygotowanie danych

Surowy CSV celowo zostaje „brudny" — pełne czyszczenie dzieje się w
`przygotowanie.py`, żeby cały krok był widoczny w kodzie:

* konwersja daty wydania (string `1999/01/09` → `datetime`) + kolumna pochodna `rok`,
* `hp` → liczba; braki **zostają**, bo niosą informację (karty Trainer i Energy
  z definicji nie mają HP — to nie jest błąd danych),
* brak rzadkości → jawna kategoria `"Brak danych"` (stare sety i promosy),
* obrażenia ataków to stringi typu `"120+"`, `"30×"` — regex wyciąga liczby
  i tworzy kolumnę pochodną `max_obrazenia`,
* z listy typów (`Fire|Water`) brany jest typ główny,
* deduplikacja
