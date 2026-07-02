"""
Wczytanie i czyszczenie danych o kartach Pokemon TCG.

Wejscie:  dane/karty_surowe.csv (wynik pobierz_dane.py - splaszczony,
          ale nieoczyszczony zrzut z oficjalnego repo pokemontcg.io)
Wyjscie:  czysty DataFrame gotowy pod dashboard

Co tu sie dzieje (i dlaczego):
1. zmiana nazw kolumn na polskie - latwiej sie czyta w reszcie kodu
2. konwersja daty wydania (string "1999/01/09" -> datetime) + kolumna rok
3. hp -> liczba; braki HP zostawiam, bo NIOSA informacje
   (Trainer i Energy z definicji nie maja HP - to nie jest blad danych)
4. brak rzadkosci -> "Brak danych" (stare sety i promosy czesto jej nie maja)
5. z listy typow biore pierwszy jako typ glowny (w TCG >99% kart ma 1 typ)
6. obrazenia atakow to stringi typu "120+", "30x" - regexem wyciagam
   liczby i licze maksymalne obrazenia karty
7. usuwam duplikaty po id (sanity check)
8. serie dostaja porzadek chronologiczny (Categorical), zeby na wykresach
   ukladaly sie od Base do Mega Evolution, a nie alfabetycznie
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd

SCIEZKA_CSV = Path(__file__).parent / "dane" / "karty_surowe.csv"


def max_obrazenia(damage_str) -> float:
    """Wyciaga najwyzsze obrazenia karty ze stringa typu "20|120+".

    Ataki maja obrazenia zapisane jako tekst: "50", "120+", "30x", albo
    pusty string (ataki bez obrazen, np. statusy). Biore wszystkie liczby
    i zwracam najwieksza. Brak liczb -> NaN.
    """
    if pd.isna(damage_str):
        return np.nan
    liczby = [int(x) for x in re.findall(r"\d+", str(damage_str))]
    return max(liczby) if liczby else np.nan


def wczytaj_i_przygotuj(sciezka: Path = SCIEZKA_CSV) -> pd.DataFrame:
    """Pelny pipeline: surowy CSV -> czysty DataFrame."""
    df = pd.read_csv(sciezka)

    # 1. polskie nazwy kolumn
    df = df.rename(columns={
        "name": "nazwa",
        "supertype": "kategoria",       # Pokemon / Trainer / Energy
        "subtypes": "podtypy",
        "types": "typy",
        "rarity": "rzadkosc",
        "artist": "artysta",
        "attacks_count": "liczba_atakow",
        "attacks_damage": "obrazenia_raw",
        "converted_retreat_cost": "koszt_odwrotu",
        "set_name": "set",
        "series": "seria",
        "release_date": "data_wydania",
        "set_total": "kart_w_secie",
    })

    # 2. daty: string "1999/01/09" -> datetime, do tego rok wydania
    df["data_wydania"] = pd.to_datetime(
        df["data_wydania"], format="%Y/%m/%d", errors="coerce"
    )
    df = df.dropna(subset=["data_wydania"])  # bez daty karta jest bezuzyteczna
    df["rok"] = df["data_wydania"].dt.year

    # 3. hp na liczbe; NaN zostaje dla Trainer/Energy - to nie blad
    df["hp"] = pd.to_numeric(df["hp"], errors="coerce")

    # 4. braki rzadkosci -> jawna kategoria zamiast NaN
    df["rzadkosc"] = df["rzadkosc"].fillna("Brak danych")

    # 5. typ glowny = pierwszy z listy "Fire|Water" -> "Fire"
    df["typ"] = df["typy"].str.split("|").str[0]

    # 6. maksymalne obrazenia karty (regex, patrz max_obrazenia)
    df["max_obrazenia"] = df["obrazenia_raw"].apply(max_obrazenia)

    # 7. duplikaty po id nie powinny istniec, ale wolimy sprawdzic
    df = df.drop_duplicates(subset=["id"])

    # 8. chronologiczny porzadek serii wg daty pierwszego setu w serii
    kolejnosc_serii = (
        df.groupby("seria")["data_wydania"].min().sort_values().index.tolist()
    )
    df["seria"] = pd.Categorical(df["seria"], categories=kolejnosc_serii, ordered=True)

    # kolumny robocze juz niepotrzebne
    df = df.drop(columns=["typy", "obrazenia_raw"])

    return df
