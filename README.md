# Projektinhallintasovellus

Projektien ja tehtävien seurantaa.
- Sovellukseen on kirjauduttava
- Voi luoda omia ryhmiä ja kutsua muita käyttäjiä niiden jäseniksi
- Ryhmän omistajat voivat luoda ja hallinnoida projekteja.
- Projektit voivat koostua useista tehtävistä.
- Tehtäviä voi jakaa tiimin jäsenille ja asettaa deadlinet.
- Ryhmän sivulla näkyy koottuna eri projektien tehtävät.
- Projektisivulla näkyy koottuna kyseisen projektin tehtävät sekä tilastoja projektiin liittyen.
- Tehtävät voi merkitä esim. keskeneräiseksi tai valmiiksi.
- Tehtävien hakutoiminnot, joilla voi rajata ja järjestää ryhmän/projektin tehtävät.
- Eri tärkeysasteita tehtäville

Mahdolllisia lisäyksiä:
- Mahdollisuus kommentoida tehtäviä ja/tai lähettää viestiä tiimin vetäjälle.
- Kalenterinäkymä


# Asennusohjeet

1. Kloonaa repositorio omalle koneellesi ja siirry sen juurikansioon
2. Luo tiedosto .env ja määritä ympäristömuuttujat DATABASE_URL ja SECRET_KEY.

        DATABASE_URL=<tietokannan-paikallinen-osoite>
        SECRET_KEY=<salainen-avain>

3. Aktivoi virtuaaliympäristö ja asenna riippuvuudet 

        $ python3 -m venv venv
        $ source venv/bin/activate
        $ pip install -r ./requirements.txt

4. Määritä tietokannan skeema

        $ psql <tietokannan-nimi> < schema.sql

5. Käynnistä sovellus seuraavalla komennolla

        $ flask run

# Sovelluksen nykytilanne

- Sovelluksella on sivu uuden käyttäjän luomiselle sekä kirjautumiselle.
- Kirjauduttua etusivulla näkyy ryhmät joihin kuuluu sekä mahdolliset ryhmäkutsut.
- Etusivulla on myös linkki uuden ryhmän luomiseen.
- Ryhmän omistajat voivat kutsua uusia jäseniä ja asettaa heidän roolinsa.
- Ryhmän asetuksista voi muuttaa nimeä ja kuvausta sekä poistaa ryhmän (vain ryhmän omistaja) tai poistua ryhmästä.
- Ryhmän projektisivulla voi luoda uusia projekteja.
- Projektien sisällä voi luoda tehtäviä sekä muokata tehtävien tilaa.

# Viimeiset puuttuvat ominaisuudet

- Tehtävien koonti ryhmän sivuille.
- Projektien arkistointi, statistiikat sekä asetukset.
- Tehtävien muokkaaminen.
- Tehtävien haku- ja järjestystoiminnot.
- Ryhmän jäsenten poistaminen sekä roolien muokkaaminen.
- Mahdollinen profiilisivu (ei kovin tärkeä).

