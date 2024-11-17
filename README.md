# Projektinhallintasovellus

Projektien ja tehtävien seurantaa.
- Sovellukseen on kirjauduttava
- Voi luoda omia ryhmiä ja kutsua muita käyttäjiä niiden jäseniksi
- Ryhmän omistajat voivat luoda ja hallinnoida projekteja.
- Projektit voivat koostua useista tehtävistä.
- Tehtäviä voi jakaa tiimin jäsenille ja asettaa deadlinet.
- Omalla sivulla näkyy omat ryhmät ja tehtävät.
- Omat tehtävät voi merkitä keskeneräiseksi/valmiiksi (mahdollisesti muita tiloja).
- Hakutoimintoja: esim. voi hakea ryhmän tietyn jäsenen kaikki tehtävät
- Voi järjestää tehtäviä määräpäivän mukaan

Mahdolllisia lisäyksiä:
- Mahdollisuus kommentoida tehtäviä ja/tai lähettää viestiä tiimin vetäjälle.
- Eri tärkeysasteita tehtäville
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
- Sovellukseen kirjauduttua etusivulla näkyy ryhmät joihin kuuluu sekä mahdolliset ryhmäkutsut.
- Etusivulla on myös linkki uuden ryhmän luomiseen.
- Ryhmän omistajat voivat kutsua uusia jäseniä ja asettaa heidän roolinsa

