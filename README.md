# BEST-steganography
BEST steganography project

# Koncepcja
Transaction ID (TXID) - W każdym zapytaniu DNS, klient losuje 16-bitowy numer identyfikacyjny, czyli TXID. Służy on do dopasowania odpowiedzi do zapytania. Można odpowiednio zakodować w tej części dane.

[Klient] —(zapytanie DNS z zakodowanym TXID)→ [Serwer DNS]


1. Klient koduje dane jako bity i osadza je w polu TXID w odpowiedni sposób.
2. Serwer odbiera zapytania, odczytuje TXID i rekonstruuje dane.
3. DNS może odpowiedzieć, żeby zamaskować podejrzany ruch.

Nasza domena to będzie coś w stylu **rnicrosoft.pl**, żeby się na pierwszy rzut oka ciężko było rozróżnić i zapytania do DNS bedą do poddomen **teams.rnicrosoft.pl** lub **outlook.rnicrosoft.pl** lub **onedrive.rnicrosoft.pl**.

Nawet jak ofiara korzysta z DNS google'a 8.8.8.8, to on i tak odwoła się do naszego DNS jeśli to będzie nasza poddomena i wtedy mamy pełną kontrolę nad odpowiedzią.

## Step-by-step
1. Dane tekstowe są konwertowane do postaci binarnej.
2. Binarne dane są dzielone na 16-bitowe bloki.
3. Każdy blok jest mieszany w następujący sposób: char1[0:3] + char2[0:3] + char1[4:5] + char2[4:5] + char1[6:7] + char2[6:7]
4. Następnie blok jest zamieniany na liczbę całkowitą i wstawiany jako TXID zapytania DNS.
5. Dodatkowo, jeśli 2 ostatnie bity są podzielne przez 2, to do TXID jest dodawane 1500, jeśli nie 850
6. Serwer DNS odbiera zapytanie i odczytuje TXID jako dane.
7. Po odebraniu wszystkich fragmentów, bity są łączone i zamieniane z powrotem na tekst.
8. Specjalny znak 0x0000 + 1500 jako znak początku i końca transmisji.

Przykład wiadomość: "hi"

0. Początek tarnsmisji 0x0000 + 1500. Od tego momentu serwer wie, że otrzymuje ukryte dane.
1. h → 01101000, i → 01101001
2. Połączone bity: 0110011010100001
3. TXID = 26273 (czyli 0110011010100001)
4. Klient tworzy zapytanie DNS z ID 26273, do którego dodaje 850, bo ostatnie dwa bity: 01 nie są podzielne przez 2
5. Serwer odbiera zapytanie, odczytuje TXID = 27123, odpowiednio odejmuje 850 lub 1500 i zapisuje do listy.
6. Interpretuje znak końca transmisji ukrytych danych 0x0000 + 1500 i zamienia całą listę na tekst, który zapisuje do pliku.

**UWAGA:** Jeśli klient ma tylko jeden znak do przesłania, to drugi tworzy jako same zera. 


## TODO - Rozszerzenie projektu
1. Klient odpytuje się losowo lub na bazie jakiegoś wzoru do jednej z trzech domen: **teams.rnicrosoft.pl** lub **outlook.rnicrosoft.pl** lub **onedrive.rnicrosoft.pl**.
2. Serwer odpowiada adresem IP do konkretnej domeny, np. 192.168.56.55, 192.168.56.65, 192.168.56.75 oraz **ustawia TTL losowo z zakresu**, np. (5,150) sekund.
3. Klient wysyła kolejne zapytanie po upłynięciu czasu TTL - nie szybciej.