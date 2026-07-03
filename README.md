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
