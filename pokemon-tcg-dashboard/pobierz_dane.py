"""
Skrypt pobierajacy dane o kartach Pokemon TCG.

Zrodlo: oficjalne repozytorium danych API pokemontcg.io
https://github.com/PokemonTCG/pokemon-tcg-data

Sciagam cale repo jako archiwum tar.gz (jeden request zamiast 173),
wyciagam sety + karty i splaszczam wszystko do jednego pliku CSV.
CSV jest celowo "surowy" - czyszczenie robie dopiero w aplikacji
(przygotowanie.py), zeby caly krok przygotowania danych byl widoczny.

Uruchomienie:  python pobierz_dane.py
Wynik:         dane/karty_surowe.csv
"""

import io
import json
import tarfile
from pathlib import Path

import pandas as pd
import requests

URL = "https://github.com/PokemonTCG/pokemon-tcg-data/archive/refs/heads/master.tar.gz"
FOLDER_DANE = Path(__file__).parent / "dane"


def pobierz_archiwum(url: str) -> tarfile.TarFile:
    """Sciaga archiwum repo do pamieci (ok. 3 MB)."""
    print("Pobieram archiwum z GitHuba...")
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz")


def wczytaj_json(archiwum: tarfile.TarFile, sciezka: str):
    """Wyciaga pojedynczy plik JSON z archiwum bez rozpakowywania na dysk."""
    plik = archiwum.extractfile(sciezka)
    return json.load(plik)


def splaszcz_karte(karta: dict, set_id: str) -> dict:
    """Zamienia zagniezdzony JSON karty na plaski slownik pod DataFrame.

    Listy (typy, podtypy, obrazenia atakow) skladam w stringi z '|',
    zeby dalo sie je trzymac w CSV. Rozbijanie z powrotem robie
    przy czyszczeniu.
    """
    ataki = karta.get("attacks", [])
    return {
        "id": karta.get("id"),
        "name": karta.get("name"),
        "supertype": karta.get("supertype"),
        "subtypes": "|".join(karta.get("subtypes", [])),
        "hp": karta.get("hp"),                      # uwaga: to string, nie liczba
        "types": "|".join(karta.get("types", [])),
        "rarity": karta.get("rarity"),              # w starych setach czesto brak
        "artist": karta.get("artist"),
        "attacks_count": len(ataki),
        "attacks_damage": "|".join(a.get("damage", "") for a in ataki),
        "converted_retreat_cost": karta.get("convertedRetreatCost"),
        "set_id": set_id,
    }


def main():
    archiwum = pobierz_archiwum(URL)

    # katalog glowny w archiwum, np. "pokemon-tcg-data-master"
    root = archiwum.getnames()[0].split("/")[0]

    # --- sety ---
    sety = wczytaj_json(archiwum, f"{root}/sets/en.json")
    df_sety = pd.DataFrame(sety)[["id", "name", "series", "releaseDate", "total"]]
    df_sety = df_sety.rename(columns={
        "id": "set_id",
        "name": "set_name",
        "releaseDate": "release_date",
        "total": "set_total",
    })
    print(f"Wczytano {len(df_sety)} setow")

    # --- karty (jeden plik JSON na set) ---
    wiersze = []
    pliki_kart = [n for n in archiwum.getnames()
                  if n.startswith(f"{root}/cards/en/") and n.endswith(".json")]
    for sciezka in sorted(pliki_kart):
        set_id = Path(sciezka).stem
        for karta in wczytaj_json(archiwum, sciezka):
            wiersze.append(splaszcz_karte(karta, set_id))
    df_karty = pd.DataFrame(wiersze)
    print(f"Wczytano {len(df_karty)} kart z {len(pliki_kart)} plikow")

    # --- laczenie kart z informacja o secie (LEFT JOIN po set_id) ---
    df = df_karty.merge(df_sety, on="set_id", how="left")

    # sanity check po merge - liczba wierszy nie powinna sie zmienic
    assert len(df) == len(df_karty), "Merge zduplikowal wiersze!"

    FOLDER_DANE.mkdir(exist_ok=True)
    sciezka_csv = FOLDER_DANE / "karty_surowe.csv"
    df.to_csv(sciezka_csv, index=False)
    rozmiar_mb = sciezka_csv.stat().st_size / 1024 / 1024
    print(f"Zapisano {sciezka_csv} ({len(df)} wierszy, {rozmiar_mb:.1f} MB)")


if __name__ == "__main__":
    main()
