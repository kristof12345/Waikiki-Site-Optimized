# Ténybeli és Kronológiai Ellentmondások Elemzése

Ez a dokumentum a távoli hivatalos weboldal (https://waikikigovernment.github.io/Website/) és a lokális kódbázis összehasonlító vizsgálata, valamint a belső szövegkörnyezeti adatok és a valós történelmi tények elemzése során feltárt ténybeli ellentmondásokat, kronológiai anakronizmusokat és számszaki eltéréseket foglalja össze.

---

## 1. Valós Történelmi Tényekkel és Kronológiával Való Ellentmondások

### 1.1. I. Erzsébet királynő és a római consul legyőzése
* **Távoli oldal (`history.html`):** 1558-ban I. Erzsébet angol királynő seregei „legyőzték az utolsó római konzult és elfoglalták Nova Aureliát”.
* **Lokális oldal (`hu/history.html` és `en/history.html`):** Ugyanez az esemény 1625-re van datálva: *„1625-ben I. Erzsébet királynő seregei végleg legyőzték az utolsó római konzult”*.
* **Ténybeli ellentmondás és hiba:**
  1. I. Erzsébet angol királynő 1533-ban született és **1603. március 24-én meghalt**. 1625-ben nem vezethetett hadsereget (1625-ben I. Károly lépett az angol trónra).
  2. A Nyugatrómai Birodalom Kr. u. 476-ban bukott el; a római consuli cím mint politikai tisztség I. Justinianus idején, Kr. u. 541-ben megszűnt. A 16. vagy 17. században nem létezett legyőzhető római consul.

### 1.2. Augustus császár és Vaikikia provincia alapítása
* **Távoli oldal (`history.html`):** Augustus császár Kr. e. 5-ben (i.e. 5) alapította meg Vaikikia provinciát.
* **Lokális oldal (`hu/history.html` és `en/history.html`):** *„Kr. u. 24-ben Augustus császár expedíciót indított és megalapította Vaikikia provinciát.”*
* **Ténybeli ellentmondás és hiba:**
  * Augustus római császár (Gaius Octavius) **Kr. u. 14. augusztus 19-én meghalt** Nolában. Kr. u. 24-ben már tíz éve halott volt; a Római Birodalom élén ekkor Tiberius császár (uralkodott: Kr. u. 14-37) állt. Augustus tehát semmiképp sem alapíthatott provinciát Kr. u. 24-ben.

### 1.3. Caesarion mint Augustus „elődje”
* **Mindkét oldalon (`history.html`):** A szöveg szerint Augustus császár a megalapított fővárost, Caesariont *„elődjéről, Caesarionról nevezte el”*.
* **Ténybeli ellentmondás és hiba:**
  * XV. Ptolemaiosz Caesarion (Julius Caesar és VII. Kleopátra fia) soha nem volt Augustus elődje a római trónon. Octavianus (a későbbi Augustus) riválisként tekintett rá, és Kr. e. 30-ban, Alexandria elfoglalása után kivégeztette Caesariont (*„Két Caesar sok egynek”* jelszóval).

### 1.4. Stuart Mária uralkodása (1603-1647)
* **Távoli és lokális oldal (`history.html`):** *„1603-tól Stuart Mária kiterjesztette a gyarmatosítást... Uralkodása 1647-ben ért véget.”*
* **Ténybeli ellentmondás és hiba:**
  * Stuart Mária skót királynőt **1587. február 8-án kivégezték** I. Erzsébet parancsára. 1603 és 1625 között I. Jakab (Mária fia), 1625 és 1649 között pedig I. Károly uralkodott. 1603 és 1647 között sem Angliában, sem Skóciában nem uralkodott Stuart Mária nevű királynő.

### 1.5. IV. Vilmos brit király uralkodási ideje (1830-1897)
* **Távoli és lokális oldal (`history.html`):** IV. Vilmos uralkodását 1830 és 1897 közé teszi a szöveg.
* **Ténybeli ellentmondás és hiba:**
  * IV. Vilmos brit király valójában mindössze **1830-tól 1837-ig** uralkodott (1837-ben elhunyt). 1837 és 1901 között 63 éven át Viktória királynő volt a Brit Birodalom uralkodója.

### 1.6. I. Károly palotája 1734-ben, mint „középkori műemlék”
* **Távoli oldal (`history.html`):** Károly kormányzó 1734-ben fejezte be a palota építését, amely ma *„Waikiki leglátogatottabb középkori műemléke”*.
* **Ténybeli ellentmondás és hiba:**
  * 1734 a 18. század (újkor, barokk és felvilágosodás kora), semmiképpen sem a középkor (amely a történészek szerint 1492-ben ért véget). Emellett I. Károly angol királyt 1649-ben lefejezték.

---

## 2. A Távoli (Remote) és a Helyi (Lokális) Kódbázis Közötti Eltérések

### 2.1. Teljes népességszám és tartományi bontás
* **Távoli oldal (`index.html`, `state.html`):**
  * Össznépesség: **210 000 000 fő**
  * Waikiki tartomány: 13 000 000 fő
  * Amazónia tartomány: 92 000 000 fő
  * Brazília tartomány: 105 000 000 fő
* **Lokális oldal (`hu/society.html`, `en/society.html`, `index.html`):**
  * Össznépesség: **212 000 000 fő**
  * Waikiki tartomány: 13 500 000 fő
  * Amazónia tartomány: 92 300 000 fő
  * Brazília tartomány: 106 200 000 fő
* **Eltérés:** 2 millió fős különbség a teljes lakosságszámban és eltérő tartományi statisztikák.

### 2.2. Tartományok területi rangsora (Amazónia vs. Brazília)
* **Távoli oldal (`state.html`):**
  * Brazília tartomány: *„több mint 4,3 millió km²”*
  * Amazónia tartomány: *„közel 4,3 millió km²”*
  * Itt Brazília tartomány szerepel a legnagyobbként.
* **Lokális oldal (`society.html`):**
  * Amazónia tartomány: **4 305 000 km²** (a legnagyobb területű)
  * Brazília tartomány: **4 242 000 km²**
* **Eltérés:** A tartományok nagyságrendi sorrendje felcserélődött a két forrás között.

### 2.3. A 2025-ös kormány hadügyminiszterének személye
* **Távoli oldal (`ministers.html`):**
  * A 2025-ös kabinet tagjaként: **Morgan Clark** szerepel hadügyminiszterként.
* **Lokális oldal (`hu/government.html`, `en/government.html`):**
  * A 2025-ös kabinet tagjaként: **Mark Milley** tábornok szerepel hadügyminiszterként.

### 2.4. A legmagasabb felhőkarcoló neve és jellemzői
* **Távoli oldal (`sights.html`):**
  * Név: **Central Tower** (220 emelet, 65 felvonó).
* **Lokális oldal (`hu/sights.html`, `en/sights.html`):**
  * Név: **Sky City** (956 méter magas, 220 emelet, 6600 fúvókás zenélő szökőkút).

### 2.5. Megújuló energia aránya az energiamixben
* **Távoli oldal (`economy.html`):** Az energiaszükséglet **50%-át** biztosítják megújuló források, a maradék több mint 80%-át atomenergia adja.
* **Lokális oldal (`society.html`, `economy.html`):** Az energiamix **több mint 90%-át** megújuló (nap, szél) és fúziós reaktorok fedezik.

---

## 3. Belső Önellentmondások a Távoli Weboldalon (Remote Lore)

### 3.1. Chease Young és Jessica Walker esküvőjének dátuma és helyszíne
* **`senate.html`:** *„1993. június 5-én feleségül vette feleségét, Jessica Walkert Mavericksben.”*
* **`chease-and-jessica.html` és `royal-family.html`:** Az esküvőt **1993. június 21-én** tartották egy csendes-óceáni magánbirtokon.
* **Ellentmondás:** Eltérő dátum (június 5. vs. június 21.) és eltérő helyszín.

### 3.2. Kuba átvétele és Waikiki állam megalapítása
* **`senate.html`:** *„1999-ben, amikor Kuba csődbe ment, Chease megvásárolta a szigetet.”* (Kereskedelmi adásvétel csődhelyzetben).
* **`chease-and-jessica.html` és `history.html`:** Fidel Castro kubai elnök politikai tárgyalások és NATO-beavatkozási fenyegetés hatására 1999. március 10-én békésen lemondott és átadta a hatalmat Chease Youngnak.

### 3.3. Raimondo herceg személyes ENSZ BT vétójoga
* **`senate.html`:** *„Raimondo 2015 óta vétójoggal rendelkezik az ENSZ Biztonsági Tanácsában.”*
* **Valóság és lokális diplomáciai szövegek:** Az ENSZ Alapokmánya szerint vétójoggal kizárólag szuverén államok állandó ENSZ-képviselői bírnak (az öt állandó tagállam), nem pedig 19 éves magánszemélyek saját személyükben.

---

## 4. Belső Önellentmondások a Helyi (Lokális) Kódbázisban

### 4.1. Egy főre jutó GDP számítási ellentmondás (`society.html`) [MEGOLDVA]
* **`hu/society.html` 206. sor (Stat box):** Egy főre jutó GDP: **$196 415 USD** (2025-ös hivatalos kanonikus adat).
* **`hu/society.html` és `en/society.html` (Tartományi összehasonlító táblázat és panelek):**
  * Eredetileg a tartományi táblázatban a súlyozott átlag $187 821 USD volt (Waikiki: $219 489 | Amazónia: $193 722 | Brazília: $178 667).
  * **Feloldás:** A tartományi táblázat és a tartományi panelek adatai egységesítésre kerültek a hivatalos 2025-ös $196 415 USD országos értékhez (+4,57%-os arányos skálázással: Waikiki: **$229 532**, Amazónia: **$202 586**, Brazília: **$186 842**, Összesen: **$196 415**).

### 4.2. A Szuverén Vagyonalap méretének leírása [MEGOLDVA]
* **Hivatalos kanonikus adat (2025):**
  * Nemzeti valutában: **11,12 billió WUD**
  * Amerikai dollárban: **25,58 billió USD** (kerekítve: **$25,6 billió USD**)
  * GDP-arány: **61%** (a 41,8 billió USD / 18,19 billió WUD teljes GDP-hez viszonyítva; 1 WUD = 2,30 USD).
* **Lokális állapot:** A jelenlegi kódbázisban már teljes az összhang:
  * `hu/wealth-fund.html` és `en/wealth-fund.html`: **₩ 11,12T WUD** és **61% GDP-arány**.
  * `hu/economy.html` és `en/economy.html`: **25,58 billió dollár** és **61% GDP**.
  * `hu/society.html` és `en/society.html`: **$25,6 billió** / **$25.6 Trillion** (A legnagyobb szuverén vagyonalap).
  * `content/Economy.md` és `content/Overview.md`: **11,12 billió WUD (25,58 billió USD)**.
* **A korábbi eltérés forrása:** A korábbi feljegyzésben említett 2,1 / 2,4 / 2,8 billió értékek korábbi évekből (2007: 2,07T USD állami tartalék, 2009: 2,72T WUD tartalék, 2011: 2,42T USD királyi magánvagyon), illetve korai vázlatokból maradtak fenn; a jelenlegi kódbázisban már sehol sem szerepelnek.

---

## 5. Összegzés és Ajánlások

| Terület | Érintett oldalak | Megoldási javaslat |
| :--- | :--- | :--- |
| **I. Erzsébet római győzelme** | `history.html` | Javítás a fiktív kronológiában (pl. 16. századi fiktív kormányzó vagy 1588-as spanyol armada analógia alkalmazása római consul helyett). |
| **Augustus császár Kr. u. 24** | `history.html` | Kr. e. 5 vagy Kr. u. 10 körüli dátum használata, amikor Augustus még élt. |
| **Caesarion „elődje”** | `history.html` | Megfogalmazás módosítása: nem elődje, hanem Julius Caesar fia. |
| **Stuart Mária uralkodása** | `history.html` | I. Jakab vagy I. Károly nevének szerepeltetése Stuart Mária helyett 1603-1647 között. |
| **IV. Vilmos 1897-ig** | `history.html` | IV. Vilmos (1830-1837) és Viktória királynő (1837-1901) uralkodásának helyesbítése. |
| **GDP / fő eltérés** | `society.html` | **Megoldva**: A tartományi tábla és a panelek értékei egységesítve a 2025-ös $196 415 USD országos adathoz ($229 532 / $202 586 / $186 842). |
| **Szuverén Vagyonalap mérete** | `wealth-fund.html` / `economy.html` / `society.html` | **Megoldva**: A hivatalos adat 11,12 billió WUD (25,58 billió USD, ~25,6 billió USD), a GDP 61%-a. A régebbi vázlatokban szereplő 2,1 / 2,4 / 2,8 billió már nincs a kódbázisban. |
| **Chease és Jessica esküvője** | `senate.html` / `chease-and-jessica.html` | Az 1993. június 21-i dátum egységesítése minden lapon. |
