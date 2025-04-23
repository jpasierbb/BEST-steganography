# BEST-steganography
BEST steganography project

# Koncepcja
Transaction ID (TXID) - W każdym zapytaniu DNS, klient losuje 16-bitowy numer identyfikacyjny, czyli TXID. Służy on do dopasowania odpowiedzi do zapytania. Można odpowiednio zakodować w tej części dane.

[Klient] —(zapytanie DNS z zakodowanym TXID)→ [Serwer DNS]


1. Klient koduje dane jako bity i osadza je w polu TXID.
2. Serwer odbiera zapytania, odczytuje TXID i rekonstruuje dane.
3. DNS może odpowiedzieć, żeby zamaskować podejrzany ruch.

Nasza domena to będzie coś w stylu **rnicrosoft.pl**, żeby się zlewało i zapytanie do DNS pod **teams.rnicrosoft.pl**

Nawet jak ofiara korzysta z DNS google'a 8.8.8.8, to on i tak odwoła się do naszego DNS jeśli to będzie nasza podsieć i wtedy mamy pełną kontrolę nad odpowiedzią.

## Step-by-step
1. Dane tekstowe są konwertowane do postaci binarnej.
2. Binarne dane są dzielone na 16-bitowe bloki.
3. Każdy blok jest zamieniany na liczbę całkowitą i wstawiany jako TXID zapytania DNS.
4. Serwer DNS odbiera zapytanie i odczytuje TXID jako dane.
5. Po odebraniu wszystkich fragmentów, bity są łączone i zamieniane z powrotem na tekst.

Przykład wiadomość: "hi"

1. h → 01101000, i → 01101001
2. Połączone bity: 0110100001101001
3. TXID = 26729 (czyli 0b0110100001101001)
4. Klient tworzy zapytanie DNS z ID 26729
5. Serwer odbiera zapytanie, odczytuje TXID = 26729
6. Zamienia to na bity → 0110100001101001


## Rozszerzenie - jak utrudnić/ulepszyć
1. Znak końca transmisji: np. 0xFFFF jako specjalny TXID.
2. TTL jako znacznik numeru fragmentu.
3. Losowy padding między zapytaniami (by nie wyglądało podejrzanie).
4. Szyfrowanie danych przed konwersją do bitów.