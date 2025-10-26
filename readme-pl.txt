=================================================
 rcheck - Copyright Checker for Audio Files
=================================================

1. Cel i Przeznaczenie
-----------------------
`rcheck` to zaawansowany skrypt w języku Python, który służy do sprawdzania, czy utwór audio jest objęty prawami autorskimi. Jest to szczególnie przydatne dla twórców treści (np. na YouTube), którzy chcą uniknąć roszczeń dotyczących praw autorskich i blokady swoich filmów.

Skrypt identyfikuje utwory muzyczne, korzystając z kilku wiodących serwisów rozpoznawania audio, i informuje, czy dany utwór został znaleziony w ich bazach danych.

2. Wymagane Zależności i Instalacja
------------------------------------
Aby skrypt działał poprawnie, konieczne jest zainstalowanie kilku zewnętrznych narzędzi i bibliotek Pythona.

### Krok 1: Instalacja FFmpeg
FFmpeg jest niezbędny do przetwarzania plików audio (odczytywania długości, przycinania).
- **Windows**: Pobierz z [oficjalnej strony FFmpeg](https://ffmpeg.org/download.html) i dodaj folder `bin` do systemowej zmiennej środowiskowej `PATH`.
- **Linux (Debian/Ubuntu)**: `sudo apt update && sudo apt install ffmpeg`
- **macOS (Homebrew)**: `brew install ffmpeg`

### Krok 2: Instalacja bibliotek Pythona
Otwórz terminal lub wiersz poleceń i zainstaluj wszystkie wymagane biblioteki za pomocą poniższego polecenia:

```
pip install colorama requests requests-toolbelt pyacoustid acrcloud-sdk-python
```

### Krok 3: Konfiguracja Kluczy API
Otwórz plik `rcheck.py` w edytorze tekstu i uzupełnij swoje klucze API dla serwisów, z których chcesz korzystać. Znajdują się one na początku pliku.

- `ACOUSTID_API_KEY`: Klucz dla serwisu AcoustID.
- `AUDIOTAG_API_KEY`: Klucz dla serwisu audiotag.info.
- `AUDD_API_KEY`: Klucz dla serwisu audd.io.
- `ACRCLOUD_CONFIG`: Uzupełnij `host`, `access_key` i `access_secret` dla serwisu ACRCloud.

3. Dostępne Opcje (Argumenty Linii Poleceń)
---------------------------------------------
Skrypt można konfigurować za pomocą następujących argumentów:

- `-i`, `--input`: Ścieżka do pojedynczego pliku MP3 lub katalogu do przeskanowania.
- `-allmp3`: Przetwarza wszystkie pliki `.mp3` w podanym katalogu.
- `-d`, `--directory`: Określa katalog do skanowania (domyślnie bieżący).
- `--time`: Przytnij audio do analizy. Można podać sekundy (np. `20`) lub procenty (np. `15%`).
- `--audioo`: Użyj serwisu AudD do rozpoznawania.
- `--audiotag`: Użyj serwisu AudioTag do rozpoznawania.
- `--acoustid`: Użyj serwisu AcoustID do rozpoznawania.
- `--acr`: Użyj serwisu ACRCloud do rozpoznawania.
- `--file`, `-f`: Zapisz wyniki do podanego pliku tekstowego.
- `--stat`: Wyświetl statystyki podsumowujące po zakończeniu pracy.
- `--color`: Włącz kolorowy output w terminalu.
- `--fullinfo`: Wyświetl dodatkowe informacje, takie jak pewność dopasowania (działa tylko z `--audiotag`).
- `--debug full`: Włącz tryb debugowania, który pokazuje pełną komunikację z API.
- `--threads`: Liczba wątków do jednoczesnego przetwarzania plików (domyślnie 1).

4. Przykłady Użycia
--------------------

**Przykład 1: Sprawdzenie pojedynczego pliku za pomocą ACRCloud**
Sprawdza jeden plik i wyświetla wynik w kolorze.
```
python rcheck.py -i "sciezka/do/pliku.mp3" --acr --color
```

**Przykład 2: Sprawdzenie wszystkich plików MP3 w bieżącym katalogu za pomocą AcoustID**
Przeskanuje wszystkie pliki `.mp3` i na końcu wyświetli podsumowanie.
```
python rcheck.py -allmp3 --acoustid --stat
```

**Przykład 3: Sprawdzenie pierwszych 30 sekund pliku za pomocą AudD**
Analizuje tylko początkowe 30 sekund utworu, co przyspiesza proces.
```
python rcheck.py -i "inny/plik.mp3" --audioo --time 20
```

**Przykład 4: Sprawdzenie 10% długości utworu za pomocą AudioTag z pełnymi informacjami**
Analizuje początkowe 10% utworu i wyświetla dodatkowe informacje o dopasowaniu.
```
python rcheck.py -i "plik.mp3" --audiotag --time 10% --fullinfo
```

**Przykład 5: Sprawdzenie wszystkich plików w danym katalogu za pomocą wszystkich serwisów i zapisanie wyników do pliku**
Używa wszystkich czterech serwisów do sprawdzenia każdego pliku i zapisuje logi do `wyniki.txt`.
```
python rcheck.py -allmp3 -d "sciezka/do/folderu" --audioo --audiotag --acoustid --acr --file wyniki.txt
```

**Przykład 6: Sprawdzenie pliku z włączonym trybem debugowania**
Przydatne do diagnozowania problemów, pokazuje pełną komunikację z API serwisu.
```
python rcheck.py -i "plik.mp3" --acr --debug full