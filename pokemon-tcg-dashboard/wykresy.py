"""
Funkcje rysujace wykresy dla dashboardu.

Kazdy wykres to osobna funkcja df -> go.Figure (tak jak cwiczylismy na
zajeciach 4) - dzieki temu app.py jest tylko orkiestratorem.

Typy wykresow w projekcie (wymagane min. 5):
liniowy, slupkowy, histogram, boxplot, scatter, heatmapa, treemap.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

SZABLON = "plotly_white"

# kolory typow zblizone do tych z gry - latwiej sie czyta wykresy
KOLORY_TYPOW = {
    "Grass": "#7AC74C", "Fire": "#EE8130", "Water": "#6390F0",
    "Lightning": "#E8C11C", "Psychic": "#A33EA1", "Fighting": "#C22E28",
    "Darkness": "#5A5366", "Metal": "#9BA0AA", "Fairy": "#D685AD",
    "Dragon": "#6F35FC", "Colorless": "#B8B5A1",
}


def tylko_pokemony(df: pd.DataFrame) -> pd.DataFrame:
    """Trainer i Energy nie maja HP ani atakow, wiec do analiz sily
    bierzemy tylko karty Pokemonow."""
    return df[df["kategoria"] == "Pokémon"]


def wykres_sila_w_czasie(df: pd.DataFrame) -> go.Figure:
    """LINIOWY: srednie HP i srednie maks. obrazenia wg roku wydania.

    Dwa trace'y w graph_objects, bo express nie sklada tego naturalnie.
    """
    pkm = tylko_pokemony(df)
    wg_roku = pkm.groupby("rok").agg(
        srednie_hp=("hp", "mean"),
        srednie_obrazenia=("max_obrazenia", "mean"),
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=wg_roku["rok"], y=wg_roku["srednie_hp"],
        name="Średnie HP", mode="lines+markers",
        line=dict(color="#C22E28", width=3),
    ))
    fig.add_trace(go.Scatter(
        x=wg_roku["rok"], y=wg_roku["srednie_obrazenia"],
        name="Średnie maks. obrażenia", mode="lines+markers",
        line=dict(color="#6390F0", width=3),
    ))
    fig.update_layout(
        title="Power creep: jak rosła siła kart w czasie",
        xaxis_title="Rok wydania", yaxis_title="Średnia wartość",
        template=SZABLON, hovermode="x unified",
        legend=dict(orientation="h", y=1.1),
    )
    return fig


def wykres_top_pokemony(df: pd.DataFrame, ile: int = 15) -> go.Figure:
    """SLUPKOWY (poziomy): najczesciej drukowane Pokemony.

    Z nazw zdejmuje dopiski mechanik (ex, GX, VMAX...), zeby "Pikachu"
    i "Pikachu ex" liczyly sie jako ten sam Pokemon.
    """
    pkm = tylko_pokemony(df).copy()
    pkm["nazwa_bazowa"] = (
        pkm["nazwa"]
        .str.replace(r"\b(ex|EX|GX|V|VMAX|VSTAR|BREAK|LV\.X)\b", "", regex=True)
        .str.replace(r"^(Dark|Light|Shining|Radiant)\s+", "", regex=True)
        .str.strip()
    )
    top = pkm["nazwa_bazowa"].value_counts().head(ile).sort_values()

    fig = px.bar(
        x=top.values, y=top.index, orientation="h",
        title=f"Top {ile} najczęściej drukowanych Pokémonów",
        labels={"x": "Liczba kart", "y": ""},
        template=SZABLON,
    )
    fig.update_traces(marker_color="#E8C11C",
                      hovertemplate="<b>%{y}</b><br>Kart: %{x}<extra></extra>")
    return fig


def wykres_histogram_hp(df: pd.DataFrame) -> go.Figure:
    """HISTOGRAM: rozklad HP wszystkich Pokemonow."""
    pkm = tylko_pokemony(df)
    fig = px.histogram(
        pkm, x="hp", nbins=35,
        title="Rozkład HP kart Pokémon",
        labels={"hp": "HP", "count": "Liczba kart"},
        template=SZABLON,
    )
    fig.update_traces(marker_color="#7AC74C")
    fig.update_layout(yaxis_title="Liczba kart", bargap=0.05)
    return fig


def wykres_hp_wg_serii(df: pd.DataFrame) -> go.Figure:
    """BOXPLOT: rozklad HP w kolejnych seriach (chronologicznie).

    Boxplot pokazuje nie tylko wzrost mediany, ale tez rozjezdzanie sie
    rozkladu - roznica miedzy zwykla karta a "toplinerem" rosnie.
    """
    pkm = tylko_pokemony(df)
    fig = px.box(
        pkm, x="seria", y="hp",
        title="Rozkład HP w kolejnych seriach",
        labels={"seria": "", "hp": "HP"},
        template=SZABLON,
    )
    fig.update_traces(marker_color="#A33EA1")
    fig.update_xaxes(tickangle=35)
    return fig


def wykres_hp_vs_obrazenia(df: pd.DataFrame) -> go.Figure:
    """SCATTER: HP vs maks. obrazenia, kolor = typ Pokemona.

    render_mode="webgl", bo punktow potrafi byc kilkanascie tysiecy.
    """
    pkm = tylko_pokemony(df).dropna(subset=["hp", "max_obrazenia"])
    fig = px.scatter(
        pkm, x="hp", y="max_obrazenia", color="typ",
        color_discrete_map=KOLORY_TYPOW,
        hover_name="nazwa", hover_data={"set": True, "rok": True,
                                        "hp": False, "max_obrazenia": False,
                                        "typ": False},
        opacity=0.4, render_mode="webgl",
        title="HP vs maksymalne obrażenia (każdy punkt = jedna karta)",
        labels={"hp": "HP", "max_obrazenia": "Maks. obrażenia", "typ": "Typ"},
        template=SZABLON,
    )
    return fig


def wykres_heatmapa_typow(df: pd.DataFrame) -> go.Figure:
    """HEATMAPA: procentowy udzial typow Pokemonow w kazdej serii.

    Procenty zamiast liczb, bo serie maja bardzo rozna wielkosc -
    inaczej Scarlet & Violet zdominowaloby caly wykres.
    """
    pkm = tylko_pokemony(df).dropna(subset=["typ"])
    pivot = pd.crosstab(pkm["typ"], pkm["seria"], normalize="columns") * 100
    # kolejnosc typow jak w slowniku kolorow, dla spojnosci
    pivot = pivot.reindex([t for t in KOLORY_TYPOW if t in pivot.index])

    fig = px.imshow(
        pivot.round(1),
        color_continuous_scale="YlGnBu",
        aspect="auto",
        title="Udział typów w seriach [% kart]",
        labels={"x": "", "y": "", "color": "% kart"},
        template=SZABLON,
    )
    fig.update_xaxes(tickangle=35)
    return fig


def wykres_treemap_setow(df: pd.DataFrame) -> go.Figure:
    """TREEMAP: struktura zbioru - serie i sety wg liczby kart."""
    licznik = (
        df.groupby(["seria", "set"], observed=True)
        .size().reset_index(name="liczba_kart")
    )
    licznik = licznik[licznik["liczba_kart"] > 0]
    licznik["seria"] = licznik["seria"].astype(str)  # treemap nie lubi Categorical

    fig = px.treemap(
        licznik, path=["seria", "set"], values="liczba_kart",
        color="liczba_kart", color_continuous_scale="Blues",
        title="Struktura zbioru: serie → sety (wielkość = liczba kart)",
        template=SZABLON,
    )
    fig.update_traces(hovertemplate="<b>%{label}</b><br>Kart: %{value}<extra></extra>")
    return fig
