"""
Pokemon TCG w liczbach - dashboard zaliczeniowy.

app.py to tylko orkiestrator: layout, filtry i skladanie calosci.
Logika siedzi w osobnych modulach:
- pobierz_dane.py   -> pobranie danych ze zrodla (uruchamiane raz, offline)
- przygotowanie.py  -> czyszczenie i przygotowanie danych
- wykresy.py        -> funkcje rysujace wykresy

Uruchomienie lokalne:  streamlit run app.py
"""

import pandas as pd
import streamlit as st

import wykresy as w
from przygotowanie import wczytaj_i_przygotuj

st.set_page_config(
    page_title="Pokémon TCG w liczbach",
    page_icon="🎴",
    layout="wide",
)


# ---------- dane ----------

@st.cache_data
def zaladuj_dane() -> pd.DataFrame:
    """Wczytanie + czyszczenie opakowane w cache - liczy sie raz,
    a nie przy kazdym ruchu suwakiem."""
    return wczytaj_i_przygotuj()


def liczba_pl(n) -> str:
    """Formatowanie liczb po polsku: 20324 -> '20 324'."""
    return f"{n:,.0f}".replace(",", " ")


df = zaladuj_dane()

# ---------- naglowek ----------

st.title("🎴 Pokémon TCG w liczbach")
st.markdown(
    "Analiza **wszystkich anglojęzycznych kart Pokémon TCG** wydanych od "
    "Base Set (1999) do dziś — ponad 20 tys. kart ze 170+ setów. "
    "Główne pytanie: **jak przez ćwierć wieku zmieniała się siła i struktura gry?** "
    "Dane pochodzą z oficjalnego repozytorium API pokemontcg.io."
)

# ---------- filtry (sidebar) ----------

with st.sidebar:
    st.header("🔍 Filtry")

    serie = st.multiselect(
        "Seria",
        options=list(df["seria"].cat.categories),
        default=list(df["seria"].cat.categories),
        help="Serie ułożone chronologicznie, od Base do Mega Evolution",
    )

    rok_min, rok_max = int(df["rok"].min()), int(df["rok"].max())
    zakres_lat = st.slider("Lata wydania", rok_min, rok_max, (rok_min, rok_max))

    typy = ["Wszystkie"] + sorted(df["typ"].dropna().unique())
    wybrany_typ = st.selectbox("Typ Pokémona", typy)

    szukana_nazwa = st.text_input(
        "Szukaj po nazwie", placeholder="np. Pikachu, Charizard...",
    )

    st.divider()
    st.caption(
        "**Źródło danych:** [pokemontcg.io](https://pokemontcg.io) — "
        "oficjalne repo `PokemonTCG/pokemon-tcg-data` (snapshot: lipiec 2026). "
        "Kod pobierania: `pobierz_dane.py`."
    )

# filtrowanie - wszystkie wykresy, KPI i tabela liczone z df_f
df_f = df[
    df["seria"].isin(serie)
    & df["rok"].between(*zakres_lat)
]
if wybrany_typ != "Wszystkie":
    df_f = df_f[df_f["typ"] == wybrany_typ]
if szukana_nazwa:
    df_f = df_f[df_f["nazwa"].str.contains(szukana_nazwa, case=False, na=False)]

if df_f.empty:
    st.warning("Brak kart spełniających wybrane filtry — poluzuj kryteria w panelu bocznym.")
    st.stop()

pokemony_f = df_f[df_f["kategoria"] == "Pokémon"]

# ---------- KPI ----------

k1, k2, k3, k4 = st.columns(4)
k1.metric("Karty", liczba_pl(len(df_f)))
k2.metric("Sety", liczba_pl(df_f["set"].nunique()))
k3.metric(
    "Średnie HP Pokémona",
    liczba_pl(pokemony_f["hp"].mean()) if len(pokemony_f) else "—",
)
k4.metric(
    "Rodzaje rzadkości",
    liczba_pl(df_f["rzadkosc"].nunique()),
    help="Przesuń suwak lat na 1999, a potem na 2025 — liczba rzadkości "
         "mówi dużo o tym, jak zmienił się model wydawniczy gry.",
)

# ---------- zakladki ----------

tab_creep, tab_struktura, tab_zaleznosci, tab_dane = st.tabs(
    ["📈 Power creep", "🧩 Struktura zbioru", "🔗 Zależności", "📋 Dane"]
)

with tab_creep:
    st.plotly_chart(w.wykres_sila_w_czasie(df_f), width="stretch")
    st.caption(
        "Średnie HP karty wzrosło z ok. 63 w 1999 r. do prawie 150 w erze "
        "Mega Evolution — czyli ponad dwukrotnie. Obrażenia rosły podobnym "
        "tempem. To klasyczny *power creep*: nowe karty muszą być mocniejsze "
        "od starych, żeby dawać graczom powód do zakupów."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(w.wykres_hp_wg_serii(df_f), width="stretch")
        st.caption(
            "Rośnie nie tylko mediana — rozjeżdża się cały rozkład. "
            "W erach Sword & Shield i Mega Evolution różnica między zwykłą "
            "kartą a topowym Pokémonem (VMAX / Mega ex, 300+ HP) jest "
            "największa w historii gry."
        )
    with col_b:
        st.plotly_chart(w.wykres_histogram_hp(df_f), width="stretch")
        st.caption(
            "HP skacze co 10, stąd „grzebień” na histogramie. Większość kart "
            "wciąż mieści się w przedziale 60–130 HP — giganty z 300+ HP to "
            "wąska, ale rosnąca grupa."
        )

with tab_struktura:
    st.plotly_chart(w.wykres_treemap_setow(df_f), width="stretch")
    st.caption(
        "Serie Scarlet & Violet i Sword & Shield to najwięksi giganci — "
        "kilka tysięcy kart każda. Dla porównania cała era Base z lat "
        "1999–2000 zmieściłaby się w jednym współczesnym secie. "
        "Kliknij serię, żeby zajrzeć do jej setów."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(w.wykres_top_pokemony(df_f), width="stretch")
        st.caption(
            "Pikachu bezkonkurencyjnie — maskotka serii ma najwięcej "
            "wydanych kart w historii. Wysoko też Eevee i Charizard, czyli "
            "ulubieńcy kolekcjonerów."
        )
    with col_b:
        st.plotly_chart(w.wykres_heatmapa_typow(df_f), width="stretch")
        st.caption(
            "Heatmapa zdradza historię mechanik: typ **Dragon** pojawia się "
            "dopiero w Black & White (2011), a **Fairy** istnieje tylko "
            "w erach XY i Sun & Moon (2013–2021) — potem został wycofany "
            "z gry karcianej."
        )

with tab_zaleznosci:
    st.plotly_chart(w.wykres_hp_vs_obrazenia(df_f), width="stretch")

    korelacja = pokemony_f["hp"].corr(pokemony_f["max_obrazenia"])
    if pd.notna(korelacja):
        st.metric("Korelacja Pearsona: HP ↔ maks. obrażenia", f"{korelacja:.2f}")
    st.caption(
        "Wyraźna dodatnia zależność (r ≈ 0,78 dla pełnego zbioru): karty "
        "z dużym HP zwykle też mocno biją. Ciekawsze są odstępstwa — punkty "
        "nisko po prawej to „tanki” (dużo HP, słabe ataki), a wysoko po "
        "lewej szklane armaty w stylu starych kart Zapdosa."
    )

with tab_dane:
    st.markdown(
        f"Podgląd danych po filtrach i czyszczeniu "
        f"(**{liczba_pl(len(df_f))}** wierszy). Pełny opis kroków "
        f"przygotowania danych jest w `przygotowanie.py` i README."
    )
    kolumny_widok = [
        "nazwa", "kategoria", "typ", "hp", "max_obrazenia", "rzadkosc",
        "set", "seria", "rok", "artysta",
    ]
    st.dataframe(df_f[kolumny_widok], width="stretch", height=420)
    st.download_button(
        "⬇️ Pobierz przefiltrowane dane (CSV)",
        data=df_f.to_csv(index=False).encode("utf-8"),
        file_name="pokemon_tcg_filtr.csv",
        mime="text/csv",
    )

# ---------- wnioski ----------

with st.expander("💡 Najważniejsze wnioski z analizy"):
    st.markdown(
        """
1. **Power creep jest mierzalny** — średnie HP wzrosło z ~63 (1999) do ~148
   (2026), a średnie maksymalne obrażenia z ~30 do ~80. Siła kart podwoiła
   się mniej więcej w 25 lat.
2. **Gra wydaje coraz więcej kart** — w 1999 r. wyszło niecałe 300 kart,
   w 2023 r. już ponad 1600. Rekordowe są serie Sword & Shield
   i Scarlet & Violet.
3. **Eksplozja rzadkości** — z 5–6 rodzajów rzadkości w erze Base zrobiło
   się ich dziś kilkadziesiąt. To celowa strategia pod kolekcjonerów:
   więcej wariantów tej samej karty = więcej powodów do otwierania boosterów.
4. **Typy mają swoją historię** — Dragon dochodzi w 2011, Fairy żyje tylko
   8 lat (2013–2021). Heatmapa typów to w praktyce oś czasu zmian zasad gry.
5. **HP i obrażenia idą w parze** (r ≈ 0,78), ale wyjątki — tanki i szklane
   armaty — pokazują, że projektanci świadomie różnicują role kart.
        """
    )

st.caption(
    "Projekt zaliczeniowy — aplikacja analityczna w Streamlit · "
    "dane: pokemontcg.io · kod: patrz repozytorium (README)"
)
