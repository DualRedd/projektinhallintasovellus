# Projektinhallintasovellus

Kirjautumisominaisuudet ja ryhmät:
- Kirjautuminen on pakollista sovelluksen käyttämiseksi.
- Sovelluksella on sivut uuden käyttäjän luomiselle sekä kirjautumiselle.
- Kirjauduttua etusivulla näkyy ryhmät joihin kuuluu sekä mahdolliset ryhmäkutsut.
- Etusivulla on linkki uuden ryhmän luomiseen.

Ryhmän hallinta:
- Ryhmän omistajat voivat kutsua uusia jäseniä ja asettaa heidän roolinsa.
- Ryhmän jäsenten rooleja voi muokata ja jäseniä voi poistaa ryhmästä (vain omistajat).
- Ryhmän asetuksista voi muuttaa ryhmän nimeä ja kuvausta sekä poistaa ryhmän (vain ryhmän omistaja) tai poistua ryhmästä.
- Ryhmän projektisivulla voi luoda uusia projekteja.

Projektit ja tehtävät:
- Projektien sisällä voi luoda tehtäviä, joiden tietoja voi myöhemmin muokata.
- Tehtäville voi asettaa nimen, kuvauksen, tärkeysasteen, määräpäivän sekä jäsenet.
- Tehtävillä on myös tila (mm. keskeneräinen tai valmis), jota voi muokata kaikista tehtävänäkymistä nopeasti.
- Projekteilla on statistiikka-sivu, jossa näkyy miten tehtävät ja niiden edistyminen jakautuvat ryhmän jäsenille.
- Tehtäviä voi katsoa projektikohtaisesti projektin omalla sivulla tai koko ryhmän laajuisesti ryhmän tehtävä-sivulla.
- Tehtävänäkymistä löytyy hakuominaisuudet, joilla tehtäviä voi järjestää ja suodattaa.
- Projekteja voi arkistoida, jolloin niiden sisältämiä tehtäviä ei voi muokata ja projekti ei enää näy sivupalkissa.
- Arkistoidun projektin tehtävät eivät myöskään näy oletuksena ryhmän tehtäväsivulla, mutta niitä on mahdollista hakea suodattimilla.
- Arkistoidun projektin voi myös aktivoida uudelleen tai poistaa kokonaan.

Muita QoL-ominaisuuksia:
- Jos ryhmän jäsen poistuu tai poistetaan, hänen nimensä näkyy harmaana tehtävissä, joihin hänet oli asetettu tekijäksi. Jos jäsen palaa ryhmään, hän on siten automaattisesti taas jäsenenä tehtävissä.
- Tehtävät, joissa määräaikä on mennyt ohi, on se korostettu punaisella.
- Linkkipolku, joka helpottaa hahmottamaan sivuhierarkiaa.
- Määräaika on mahdollista asettaa päivän tai päivän ja ajan tarkkuudella, ja se myös näytetään oikein käyttöliittymässä.

Muit teknisiä ominaisuuksia:
- Salasanat tallennetaan tietokantaan hajautusarvona.
- Syötteiden pituudet tarkistetaan aina ennen kuin ne päätyvät tietokantaan.
- Ennen sivun palauttamista tai tietokannan muokkaamista tarkastetaan käyttäjän oikeudet.
- Kaikki lomakkeet käyttävät csrf-tokenia, joka tarkastetaan.

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

# Alkuperäinen idea

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
