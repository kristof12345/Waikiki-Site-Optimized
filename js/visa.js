/**
 * Visa and Entry Requirements — Interactive 6-Tier Checker Logic
 * Sovereign Nation of Waikiki
 */
(function() {
    'use strict';

    function initVisaChecker() {
        const checker = document.getElementById('visa-checker');
        if (!checker) return;

        const tierCards = checker.querySelectorAll('[data-checker-tier]');
        const purposePills = checker.querySelectorAll('[data-checker-purpose]');
        const resultPanel = checker.querySelector('[data-checker-result]');
        if (!tierCards.length || !resultPanel) return;

        const isHungarian = (document.documentElement.lang || 'en') === 'hu';

        const tierData = {
            us_ca: {
                defaultRegion: isHungarian ? 'Egyesült Államok és Kanada' : 'United States and Canada',
                tag: isHungarian ? 'Igazolvánnyal szabad belépés' : 'ID-Only Direct Entry',
                tagClass: 'tag-free',
                doc: isHungarian ? 'Elég egy igazolvány' : 'ID Card or Passport',
                docSub: isHungarian ? 'Útlevél nem szükséges (ID vagy jogosítvány)' : 'No passport required — Photo ID suffices',
                prereg: isHungarian ? 'Nem kell regisztráció' : 'No Pre-Registration',
                preregSub: isHungarian ? 'Előzetes bejelentés nélkül utazhat' : 'Direct check-in without prior form',
                border: isHungarian ? 'Digitális határellenőrzés' : 'Digital Border Control',
                borderSub: isHungarian ? 'Automatikus SmartBorder e-kapuk' : 'Contactless SmartBorder e-Gates',
                purposes: {
                    tourism: {
                        title: isHungarian
                            ? 'Belépés igazolvánnyal és digitális határellenőrzéssel'
                            : 'Direct Photo ID Entry and Digital SmartBorder',
                        lead: isHungarian
                            ? 'Az Egyesült Államok és Kanada állampolgárainak nem kell előzetes regisztráció és útlevél: elég egy fényképes igazolvány, a belépés pedig digitális határellenőrzéssel történik.'
                            : 'Citizens of the United States and Canada do not need a passport or advance registration—a valid government photo ID card is sufficient with automated digital border control.',
                        items: isHungarian
                            ? [
                                'Nem kell útlevél: állami fényképes személyazonosító igazolvány vagy jogosítvány elegendő',
                                'Nem kell előzetes regisztráció vagy vízum az indulás előtt',
                                'Gyorsított digitális határellenőrzés a SmartBorder biometrikus kapukon',
                                'Visszaúti vagy továbbutazási menetjegy igazolása'
                            ]
                            : [
                                'Government-issued photo ID card (state driver\'s license, national ID) or passport',
                                'No advance registration or visa required prior to departure',
                                'Automated digital border control via SmartBorder biometric e-gates',
                                'Return or onward travel ticket confirmation'
                            ],
                        stay: isHungarian ? 'Legfeljebb 90 nap' : 'Up to 90 Days',
                        fee: isHungarian ? '0 WUD (Díjmentes)' : '0 WUD (Free)',
                        time: isHungarian ? 'Azonnali beléptetés' : 'Instant at Gate'
                    },
                    business: {
                        title: isHungarian
                            ? 'Közvetlen üzleti belépés igazolvánnyal'
                            : 'Direct Business Entry with Photo ID',
                        lead: isHungarian
                            ? 'Az Egyesült Államok és Kanada üzleti utazói előzetes regisztráció és útlevél nélkül, fényképes igazolvánnyal és digitális határellenőrzéssel léphetnek be.'
                            : 'Business visitors from the United States and Canada enter without pre-registration or a passport using a government photo ID and digital SmartBorder gates.',
                        items: isHungarian
                            ? [
                                'Állami fényképes igazolvány vagy jogosítvány (útlevél nem szükséges)',
                                'Nem kell előzetes online regisztráció üzleti megbeszélésekhez és konferenciákhoz',
                                'Azonnali digitális határellenőrzés és VIP üzleti sáv használata',
                                '90 napos üzleti és befektetői tartózkodási jogosultság'
                            ]
                            : [
                                'Valid government photo ID card or driver\'s license (no passport required)',
                                'No pre-registration required for meetings, conferences, and investment forums',
                                'Automated digital border control with priority executive lane access',
                                'Up to 90 days authorized stay for commercial and diplomatic engagements'
                            ],
                        stay: isHungarian ? 'Legfeljebb 90 nap' : 'Up to 90 Days',
                        fee: isHungarian ? '0 WUD (Díjmentes)' : '0 WUD (Free)',
                        time: isHungarian ? 'Azonnali beléptetés' : 'Instant at Gate'
                    },
                    transit: {
                        title: isHungarian
                            ? 'Szabad tranzit igazolvánnyal és digitális kapuval'
                            : 'Direct Photo ID Transit and City Access',
                        lead: isHungarian
                            ? 'Átszálláskor sem kell útlevél vagy előzetes regisztráció: fényképes igazolvánnyal és digitális határellenőrzéssel szabadon látogatható a főváros.'
                            : 'Transiting passengers from the United States and Canada require no passport or pre-registration and may exit the terminal via digital e-gates.',
                        items: isHungarian
                            ? [
                                'Elég egy fényképes igazolvány a terminál elhagyásához is',
                                'Nem kell előzetes regisztráció átszálláshoz',
                                'Digitális határellenőrzés a SmartBorder kapukon',
                                'Díjmentes expressz maglev kapcsolat Nova Aurelia központjával'
                            ]
                            : [
                                'Photo ID card suffices to exit the airport during layovers',
                                'No pre-registration required for airside or landside transit',
                                'Digital border control via SmartBorder biometric e-gates',
                                'Complimentary Express Maglev rail token to Nova Aurelia center'
                            ],
                        stay: isHungarian ? 'Korlátlan tranzit (90 napig)' : 'Unrestricted (Up to 90 Days)',
                        fee: isHungarian ? '0 WUD (Díjmentes)' : '0 WUD (Free)',
                        time: isHungarian ? 'Azonnali beléptetés' : 'Instant at Gate'
                    }
                }
            },
            eu_ch_au_uk: {
                defaultRegion: isHungarian ? 'EU, Svájc, Ausztrália és UK' : 'EU, Switzerland, Australia and UK',
                tag: isHungarian ? 'Vízummentes · 24 órás regisztráció' : 'Visa-Free · 24h Pre-Registration',
                tagClass: 'tag-free',
                doc: isHungarian ? 'Útlevél szükséges' : 'Passport Required',
                docSub: isHungarian ? 'Érvényes biometrikus útlevél' : 'Valid biometric national passport',
                prereg: isHungarian ? 'Előzetes regisztráció (24 óra)' : 'Pre-Registration (24 Hours)',
                preregSub: isHungarian ? 'Indulás előtt legalább 24 órával' : 'Complete at least 24h before flight',
                border: isHungarian ? 'Digitális határellenőrzés' : 'Digital Border Control',
                borderSub: isHungarian ? 'Automatikus SmartBorder e-kapuk' : 'Automated SmartBorder e-Gates',
                purposes: {
                    tourism: {
                        title: isHungarian
                            ? 'Útlevél, 24 órás előzetes regisztráció és digitális kapu'
                            : 'Passport with 24-Hour Pre-Registration and Digital Gate',
                        lead: isHungarian
                            ? 'Az EU, Svájc, Ausztrália és az Egyesült Királyság állampolgárainak útlevél szükséges, indulás előtt 24 órával előzetes regisztrációt kell végezniük, a belépés pedig digitális határellenőrzéssel történik.'
                            : 'Citizens of the EU, Switzerland, Australia, and the UK require a valid passport and 24-hour advance online registration, with seamless digital border control upon arrival.',
                        items: isHungarian
                            ? [
                                'Érvényes útlevél szükséges (a tervezett távozásig érvényes biometrikus útlevél)',
                                'Kötelező, díjmentes előzetes regisztráció a Waikiki One felületén indulás előtt 24 órával',
                                'Érintésmentes digitális határellenőrzés a SmartBorder biometrikus e-kapukon',
                                'Visszaúti vagy továbbutazási menetjegy igazolása'
                            ]
                            : [
                                'Valid biometric passport required for international travel',
                                'Free Waikiki One pre-departure registration completed at least 24 hours before flight',
                                'Contactless digital border control through SmartBorder biometric e-gates',
                                'Proof of return or onward transportation booking'
                            ],
                        stay: isHungarian ? 'Legfeljebb 60 nap' : 'Up to 60 Days',
                        fee: isHungarian ? '0 WUD (Díjmentes)' : '0 WUD (Free)',
                        time: isHungarian ? '24 órás előzetes regisztráció' : '24h Advance Registration'
                    },
                    business: {
                        title: isHungarian
                            ? 'Üzleti belépés 24 órás regisztrációval és digitális kapuval'
                            : 'Business Entry with 24-Hour Registration and Digital Gate',
                        lead: isHungarian
                            ? 'Üzleti tárgyalásokhoz és konferenciákhoz útlevél és 24 órás előzetes Waikiki One regisztráció szükséges, digitális határellenőrzéssel.'
                            : 'Business travelers from the EU, Switzerland, Australia, and the UK enter visa-free with a passport, 24-hour advance registration, and digital border control.',
                        items: isHungarian
                            ? [
                                'Érvényes útlevél szükséges',
                                'Díjmentes előzetes regisztráció indulás előtt 24 órával (üzleti cél megjelölésével)',
                                'Digitális határellenőrzés és gyorsított SmartBorder üzleti sáv',
                                'Hivatalos meghívólevél vagy konferencia-regisztráció'
                            ]
                            : [
                                'Valid biometric passport required',
                                'Free 24-hour advance Waikiki One registration selecting Business purpose',
                                'Digital border control with fast-track SmartBorder executive e-gates',
                                'Corporate invitation or accredited symposium confirmation'
                            ],
                        stay: isHungarian ? 'Legfeljebb 60 nap' : 'Up to 60 Days',
                        fee: isHungarian ? '0 WUD (Díjmentes)' : '0 WUD (Free)',
                        time: isHungarian ? '24 órás előzetes regisztráció' : '24h Advance Registration'
                    },
                    transit: {
                        title: isHungarian
                            ? 'Tranzit útlevéllel, 24 órás regisztrációval és digitális kapuval'
                            : 'Transit with Passport, 24h Registration and Digital Gate',
                        lead: isHungarian
                            ? 'Átszálláshoz és városlátogatáshoz érvényes útlevél és 24 órás előzetes regisztráció szükséges, digitális határellenőrzéssel.'
                            : 'Transit passengers use their passport and 24-hour advance registration to clear digital SmartBorder e-gates.',
                        items: isHungarian
                            ? [
                                'Érvényes útlevél szükséges',
                                'Előzetes regisztráció 24 órával az indulás előtt',
                                'Digitális határellenőrzés a SmartBorder e-kapukon',
                                'Továbbutazási beszállókártya 48 órán belüli járatra'
                            ]
                            : [
                                'Valid passport required',
                                'Pre-departure registration submitted 24 hours prior to boarding',
                                'Digital border control via SmartBorder e-gates',
                                'Confirmed onward flight ticket within 48 hours'
                            ],
                        stay: isHungarian ? 'Legfeljebb 48 óra' : 'Up to 48 Hours',
                        fee: isHungarian ? '0 WUD (Díjmentes)' : '0 WUD (Free)',
                        time: isHungarian ? '24 órás előzetes regisztráció' : '24h Advance Registration'
                    }
                }
            },
            jp_ar_partners: {
                defaultRegion: isHungarian ? 'Japán, Argentína stb.' : 'Japan, Argentina, etc.',
                tag: isHungarian ? 'Vízummentes · 48 órás regisztráció' : 'Visa-Free · 48h Pre-Registration',
                tagClass: 'tag-fast',
                doc: isHungarian ? 'Útlevél szükséges' : 'Passport Required',
                docSub: isHungarian ? 'Min. 6 hónapig érvényes útlevél' : 'Valid passport (min. 6 months)',
                prereg: isHungarian ? 'Előzetes regisztráció (48 óra)' : 'Pre-Registration (48 Hours)',
                preregSub: isHungarian ? 'Indulás előtt legalább 48 órával' : 'Complete at least 48h before flight',
                border: isHungarian ? 'Digitális határellenőrzés' : 'Digital Border Control',
                borderSub: isHungarian ? 'Automatikus SmartBorder e-kapuk' : 'Automated SmartBorder e-Gates',
                purposes: {
                    tourism: {
                        title: isHungarian
                            ? 'Útlevél, 48 órás előzetes regisztráció és digitális kapu'
                            : 'Passport with 48-Hour Pre-Registration and Digital Gate',
                        lead: isHungarian
                            ? 'Japán, Argentína és a kiemelt szerződéses országok állampolgárainak útlevél szükséges, az előzetes regisztrációt indulás előtt 48 órával kell elvégezni, a beléptetés pedig digitális határellenőrzéssel zajlik.'
                            : 'Citizens of Japan, Argentina, South Korea, New Zealand, Singapore, and Chile require a passport and 48-hour advance registration, clearing arrival through digital border control.',
                        items: isHungarian
                            ? [
                                'Érvényes útlevél szükséges (legalább 6 hónap érvényességgel)',
                                'Kötelező előzetes regisztráció a Waikiki One rendszerben indulás előtt 48 órával',
                                'Gyorsított digitális határellenőrzés a SmartBorder biometrikus e-kapukon',
                                'Szállásfoglalás és visszaúti menetjegy igazolása'
                            ]
                            : [
                                'Valid national passport required (minimum 6 months validity)',
                                'Mandatory Waikiki One pre-registration completed at least 48 hours before departure',
                                'Automated digital border control via SmartBorder biometric e-gates',
                                'Confirmed accommodation and return or onward flight ticket'
                            ],
                        stay: isHungarian ? 'Legfeljebb 30 nap' : 'Up to 30 Days',
                        fee: isHungarian ? '0 WUD (Díjmentes)' : '0 WUD (Free)',
                        time: isHungarian ? '48 órás előzetes regisztráció' : '48h Advance Registration'
                    },
                    business: {
                        title: isHungarian
                            ? 'Üzleti belépés 48 órás regisztrációval és digitális kapuval'
                            : 'Business Entry with 48-Hour Registration and Digital Gate',
                        lead: isHungarian
                            ? 'Japán, Argentína és partnerországok üzleti küldöttei útlevéllel, 48 órás előzetes regisztrációval és digitális határellenőrzéssel léphetnek be.'
                            : 'Business delegates from Japan, Argentina, and treaty partners require a passport and 48-hour advance registration with digital e-gate border clearance.',
                        items: isHungarian
                            ? [
                                'Érvényes útlevél szükséges',
                                'Előzetes regisztráció indulás előtt 48 órával üzleti meghívó csatolásával',
                                'Digitális határellenőrzés a SmartBorder e-kapukon',
                                '30 napos üzleti tartózkodás (online meghosszabbítható)'
                            ]
                            : [
                                'Valid national passport required',
                                '48-hour advance registration including host company or forum reference',
                                'Digital border control at SmartBorder biometric e-gates',
                                '30-day business stay allowance (extendable online)'
                            ],
                        stay: isHungarian ? 'Legfeljebb 30 nap' : 'Up to 30 Days',
                        fee: isHungarian ? '0 WUD (Díjmentes)' : '0 WUD (Free)',
                        time: isHungarian ? '48 órás előzetes regisztráció' : '48h Advance Registration'
                    },
                    transit: {
                        title: isHungarian
                            ? 'Tranzit 48 órás regisztrációval és digitális határellenőrzéssel'
                            : 'Transit with 48-Hour Registration and Digital Gate',
                        lead: isHungarian
                            ? 'Átszálló utasok számára útlevél és 48 órás előzetes regisztráció szükséges a digitális határellenőrzésen való áthaladáshoz.'
                            : 'Transiting travelers present a valid passport and 48-hour pre-registration to use the digital SmartBorder gates.',
                        items: isHungarian
                            ? [
                                'Érvényes útlevél szükséges',
                                'Előzetes regisztráció 48 órával a felszállás előtt',
                                'Digitális határellenőrzés a SmartBorder kapukon',
                                'Megerősített továbbutazási jegy 48 órán belül'
                            ]
                            : [
                                'Valid passport required',
                                'Pre-departure registration completed 48 hours ahead of travel',
                                'Digital border control via SmartBorder e-gates',
                                'Confirmed onward boarding pass within 48 hours'
                            ],
                        stay: isHungarian ? 'Legfeljebb 48 óra' : 'Up to 48 Hours',
                        fee: isHungarian ? '0 WUD (Díjmentes)' : '0 WUD (Free)',
                        time: isHungarian ? '48 órás előzetes regisztráció' : '48h Advance Registration'
                    }
                }
            },
            partner_other: {
                defaultRegion: isHungarian ? 'További partner országok' : 'Additional Partner Countries',
                tag: isHungarian ? 'Egyszerűsített e-Visa · Digitális kapu' : 'Simplified e-Visa · Digital Gate',
                tagClass: 'tag-evisa',
                doc: isHungarian ? 'Útlevél szükséges' : 'Passport Required',
                docSub: isHungarian ? 'Min. 6 hónapig érvényes biometrikus útlevél' : 'Biometric passport (min. 6 months)',
                prereg: isHungarian ? 'Egyszerűsített e-Visa' : 'Simplified e-Visa',
                preregSub: isHungarian ? 'Gyorsított online űrlap a Waikiki One-ban' : 'Streamlined online e-Visa application',
                border: isHungarian ? 'Digitális határellenőrzés' : 'Digital Border Control',
                borderSub: isHungarian ? 'SmartBorder biometrikus e-kapuk' : 'SmartBorder biometric e-Gates',
                purposes: {
                    tourism: {
                        title: isHungarian
                            ? 'Egyszerűsített e-Visa és digitális határellenőrzés'
                            : 'Simplified e-Visa with Digital Border Control',
                        lead: isHungarian
                            ? 'A további partner országok állampolgárai egyszerűsített online e-Visa igényléssel utazhatnak be, és érkezéskor a gyorsított digitális határellenőrzést vehetik igénybe.'
                            : 'Citizens of additional partner countries qualify for a simplified online e-Visa and enjoy automated digital border control upon arrival.',
                        items: isHungarian
                            ? [
                                'Érvényes útlevél (legalább 6 hónap érvényességgel)',
                                'Egyszerűsített e-Visa igénylés a Waikiki One alkalmazásban (dokumentumfeltöltés percek alatt)',
                                'Érintésmentes digitális határellenőrzés a SmartBorder e-kapukon',
                                'Szállásigazolás és visszaúti repülőjegy bemutatása'
                            ]
                            : [
                                'Valid biometric passport (minimum 6 months validity)',
                                'Simplified e-Visa submitted online via the Waikiki One portal in minutes',
                                'Automated digital border control through SmartBorder biometric e-gates',
                                'Confirmed accommodation and return flight itinerary'
                            ],
                        stay: isHungarian ? '30 nap (egyszeri vagy többszöri)' : '30 Days (Single or Multiple)',
                        fee: isHungarian ? '20 WUD (Kedvezményes)' : '20 WUD (Partner Rate)',
                        time: isHungarian ? '2–6 órán belül' : 'Within 2 to 6 Hours'
                    },
                    business: {
                        title: isHungarian
                            ? 'Üzleti egyszerűsített e-Visa és digitális határellenőrzés'
                            : 'Business Simplified e-Visa and Digital Gate',
                        lead: isHungarian
                            ? 'Partnerországok üzleti utazói egyszerűsített üzleti e-Visa engedéllyel és digitális határellenőrzéssel léphetnek be.'
                            : 'Commercial visitors from partner countries obtain a simplified business e-Visa and clear arrival via digital SmartBorder gates.',
                        items: isHungarian
                            ? [
                                'Érvényes biometrikus útlevél',
                                'Egyszerűsített üzleti e-Visa és fogadó vállalati meghívó referenciaszám',
                                'Digitális határellenőrzés a SmartBorder e-kapukon',
                                'Legfeljebb 60 napos üzleti tartózkodás'
                            ]
                            : [
                                'Valid biometric passport',
                                'Simplified business e-Visa with host company or forum reference code',
                                'Digital border control via SmartBorder e-gates',
                                'Up to 60 days authorized business stay'
                            ],
                        stay: isHungarian ? 'Legfeljebb 60 nap' : 'Up to 60 Days',
                        fee: isHungarian ? '45 WUD' : '45 WUD',
                        time: isHungarian ? '6 órán belül' : 'Under 6 Hours'
                    },
                    transit: {
                        title: isHungarian
                            ? 'Tranzit egyszerűsített e-Visa-val és digitális kapuval'
                            : 'Transit with Simplified e-Visa and Digital Gate',
                        lead: isHungarian
                            ? 'A terminál elhagyásával járó átszálláshoz egyszerűsített tranzit e-Visa szükséges, digitális határellenőrzéssel.'
                            : 'Landside transit requires a simplified online transit e-Visa with digital SmartBorder gate clearance.',
                        items: isHungarian
                            ? [
                                'Érvényes útlevél és 48 órán belüli továbbutazási jegy',
                                'Díjmentes egyszerűsített tranzit e-Visa igénylés online',
                                'Digitális határellenőrzés a SmartBorder kapukon',
                                'Belépés Nova Aurelia tranzitzónájába és belvárosába'
                            ]
                            : [
                                'Valid passport and onward ticket departing within 48 hours',
                                'Complimentary simplified transit e-Visa issued online',
                                'Digital border control through SmartBorder e-gates',
                                'Full access to Nova Aurelia during layover'
                            ],
                        stay: isHungarian ? 'Legfeljebb 48 óra' : 'Up to 48 Hours',
                        fee: isHungarian ? '0 WUD (Díjmentes tranzit)' : '0 WUD (Free Transit)',
                        time: isHungarian ? '1 órán belül' : 'Under 1 Hour'
                    }
                }
            },
            developed_other: {
                defaultRegion: isHungarian ? 'További fejlett országok' : 'Additional Developed Countries',
                tag: isHungarian ? 'Normál e-Visa · Személyes ellenőrzés' : 'Standard e-Visa · In-Person Control',
                tagClass: 'tag-evisa',
                doc: isHungarian ? 'Útlevél szükséges' : 'Passport Required',
                docSub: isHungarian ? 'Min. 6 hónapig érvényes útlevél' : 'Valid passport (min. 6 months)',
                prereg: isHungarian ? 'Online e-Visa' : 'Standard e-Visa',
                preregSub: isHungarian ? 'Előzetes online e-Visa jóváhagyás' : 'Prior online e-Visa approval',
                border: isHungarian ? 'Személyes határellenőrzés' : 'In-Person Border Control',
                borderSub: isHungarian ? 'Határrendészeti tisztviselői pult' : 'Border officer inspection desk',
                purposes: {
                    tourism: {
                        title: isHungarian
                            ? 'Online e-Visa és személyes határellenőrzés'
                            : 'Standard e-Visa and In-Person Border Control',
                        lead: isHungarian
                            ? 'A további fejlett országok állampolgárai online igényelhető e-Visa engedéllyel utazhatnak be, érkezéskor pedig személyes határellenőrzésen vesznek részt.'
                            : 'Citizens of additional developed countries apply online for a standard e-Visa prior to travel and complete in-person border inspection upon arrival.',
                        items: isHungarian
                            ? [
                                'Érvényes útlevél (legalább 6 hónap érvényességgel és két üres oldallal)',
                                'Előzetesen jóváhagyott online e-Visa a Waikiki One konzuli portálon',
                                'Személyes határellenőrzés és ujjlenyomat-azonosítás a határrendészeti pultnál',
                                'Megerősített szállásfoglalás, utazási biztosítás és visszaúti jegy'
                            ]
                            : [
                                'Valid national passport (minimum 6 months validity and two blank pages)',
                                'Pre-approved standard e-Visa via the Waikiki One consular portal',
                                'In-person border control and biometric verification with a border officer',
                                'Confirmed hotel booking, travel insurance, and return ticket'
                            ],
                        stay: isHungarian ? 'Legfeljebb 30 nap' : 'Up to 30 Days',
                        fee: isHungarian ? '35 WUD (kb. 88 USD)' : '35 WUD (approx $88 USD)',
                        time: isHungarian ? '24–48 óra' : '24 to 48 Hours'
                    },
                    business: {
                        title: isHungarian
                            ? 'Üzleti e-Visa és személyes határellenőrzés'
                            : 'Business e-Visa and In-Person Border Control',
                        lead: isHungarian
                            ? 'Üzleti utazáshoz online üzleti e-Visa igénylés és érkezéskor személyes határellenőrzés szükséges.'
                            : 'Business visitors apply online for a commercial e-Visa and clear arrival through an in-person border control officer.',
                        items: isHungarian
                            ? [
                                'Érvényes útlevél és online üzleti e-Visa kérelem',
                                'Hivatalos waikiki vállalati vagy intézményi meghívólevél',
                                'Személyes határellenőrzés az üzleti érkezési sávban',
                                'Legfeljebb 60 napos tartózkodás'
                            ]
                            : [
                                'Valid passport and approved online Business e-Visa',
                                'Official letter of invitation from a registered Waikiki entity',
                                'In-person border control at the dedicated business arrival desk',
                                'Up to 60 days stay per entry'
                            ],
                        stay: isHungarian ? 'Legfeljebb 60 nap' : 'Up to 60 Days',
                        fee: isHungarian ? '75 WUD' : '75 WUD',
                        time: isHungarian ? '24–48 óra' : '24 to 48 Hours'
                    },
                    transit: {
                        title: isHungarian
                            ? 'Tranzit e-Visa és személyes határellenőrzés'
                            : 'Transit e-Visa and In-Person Border Control',
                        lead: isHungarian
                            ? 'A tranzitzóna elhagyásához előzetes online tranzit e-Visa és személyes határellenőrzés szükséges.'
                            : 'Leaving the international transit lounge requires a pre-approved transit e-Visa and in-person officer clearance.',
                        items: isHungarian
                            ? [
                                'Érvényes útlevél és továbbutazási menetjegy',
                                'Online tranzit e-Visa igénylés indulás előtt',
                                'Személyes határellenőrzés a tranzitpultnál',
                                'Legfeljebb 48 órás tartózkodás'
                            ]
                            : [
                                'Valid passport and confirmed onward ticket',
                                'Online transit e-Visa approved prior to boarding',
                                'In-person border control at the transit inspection desk',
                                'Up to 48 hours authorized layover stay'
                            ],
                        stay: isHungarian ? 'Legfeljebb 48 óra' : 'Up to 48 Hours',
                        fee: isHungarian ? '15 WUD' : '15 WUD',
                        time: isHungarian ? '24 óra' : '24 Hours'
                    }
                }
            },
            other_world: {
                defaultRegion: isHungarian ? 'Egyéb országok' : 'Other Countries',
                tag: isHungarian ? 'Vízum igénylés · Személyes ellenőrzés' : 'Visa Application · In-Person Control',
                tagClass: 'tag-visa',
                doc: isHungarian ? 'Útlevél és vízum' : 'Passport and Consular Visa',
                docSub: isHungarian ? 'Előzetesen elbírált vízum szükséges' : 'Prior consular visa approval required',
                prereg: isHungarian ? 'Vízum igénylés' : 'Visa Application',
                preregSub: isHungarian ? 'Teljes körű konzuli vízumeljárás' : 'Full consular application before travel',
                border: isHungarian ? 'Személyes határellenőrzés' : 'In-Person Border Control',
                borderSub: isHungarian ? 'Személyes határrendészeti vizsgálat' : 'Full in-person officer inspection',
                purposes: {
                    tourism: {
                        title: isHungarian
                            ? 'Előzetes vízum igénylés és személyes határellenőrzés'
                            : 'Consular Visa Application and In-Person Border Control',
                        lead: isHungarian
                            ? 'Az egyéb országok állampolgárainak utazás előtt hivatalos vízum igénylés szükséges, a beléptetés pedig személyes határellenőrzéssel történik.'
                            : 'Citizens of other countries must complete a formal consular visa application prior to travel and undergo in-person border control upon arrival.',
                        items: isHungarian
                            ? [
                                'Érvényes útlevél (legalább 6 hónap érvényességgel a tervezett távozás után)',
                                'Előzetes vízum igénylés és pénzügyi fedezetigazolás benyújtása',
                                'Személyes határellenőrzés, biometrikus rögzítés és dokumentumvizsgálat érkezéskor',
                                'Teljes utazási terv, szállásigazolás és visszaúti repülőjegy'
                            ]
                            : [
                                'Valid passport (minimum 6 months validity beyond planned departure)',
                                'Prior consular visa application with proof of financial means and itinerary',
                                'In-person border control, biometric scan, and document review upon arrival',
                                'Confirmed accommodation voucher and return flight booking'
                            ],
                        stay: isHungarian ? 'Legfeljebb 30 nap' : 'Up to 30 Days',
                        fee: isHungarian ? '60 WUD (kb. 150 USD)' : '60 WUD (approx $150 USD)',
                        time: isHungarian ? '5–10 munkanap' : '5 to 10 Business Days'
                    },
                    business: {
                        title: isHungarian
                            ? 'Üzleti vízum igénylés és személyes határellenőrzés'
                            : 'Business Visa Application and In-Person Control',
                        lead: isHungarian
                            ? 'Üzleti látogatáshoz előzetes konzuli üzleti vízum igénylés, meghívólevél-hitelesítés és személyes határellenőrzés szükséges.'
                            : 'Commercial travelers require a pre-approved consular business visa, verified sponsor invitation, and in-person border control.',
                        items: isHungarian
                            ? [
                                'Előzetes üzleti vízum igénylés és akkreditált waikiki meghívólevél',
                                'Konzuli interjú vagy videóhitelesítés az indulás előtt',
                                'Személyes határellenőrzés a határrendészeti pultnál',
                                '30–90 napos engedélyezett tartózkodás a vízumtól függően'
                            ]
                            : [
                                'Prior consular business visa application and accredited sponsor letter',
                                'Consular verification or remote video interview before departure',
                                'In-person border control with a consular officer on arrival',
                                '30 to 90 days authorized stay depending on visa grant'
                            ],
                        stay: isHungarian ? '30–90 nap' : '30 to 90 Days',
                        fee: isHungarian ? '120 WUD' : '120 WUD',
                        time: isHungarian ? '5–7 munkanap' : '5 to 7 Business Days'
                    },
                    transit: {
                        title: isHungarian
                            ? 'Tranzitvízum igénylés és személyes határellenőrzés'
                            : 'Transit Visa Application and In-Person Control',
                        lead: isHungarian
                            ? 'Nemzetközi átszálláshoz előzetes tranzitvízum igénylés és személyes határellenőrzés szükséges.'
                            : 'Transiting through Waikiki requires a prior transit visa application and in-person inspection at the border desk.',
                        items: isHungarian
                            ? [
                                'Érvényes útlevél és a célországba szóló vízum / repülőjegy',
                                'Előzetes tranzitvízum igénylés az utazás előtt',
                                'Személyes határellenőrzés a repülőtéri tranzitpultnál',
                                'Legfeljebb 24–48 órás átszállási időtartam'
                            ]
                            : [
                                'Valid passport, onward ticket, and destination visa if applicable',
                                'Prior transit visa application submitted before departure',
                                'In-person border control at the airport transit counter',
                                'Up to 24 to 48 hours authorized transit window'
                            ],
                        stay: isHungarian ? 'Legfeljebb 48 óra' : 'Up to 48 Hours',
                        fee: isHungarian ? '30 WUD' : '30 WUD',
                        time: isHungarian ? '3–5 munkanap' : '3 to 5 Business Days'
                    }
                }
            }
        };

        let currentTier = 'us_ca';
        let currentPurpose = 'tourism';

        function syncTierCards() {
            tierCards.forEach(function(card) {
                const cardTier = card.getAttribute('data-checker-tier');
                if (cardTier === currentTier) {
                    card.classList.add('is-active');
                    card.setAttribute('aria-pressed', 'true');
                } else {
                    card.classList.remove('is-active');
                    card.setAttribute('aria-pressed', 'false');
                }
            });
        }

        function updateResult() {
            const tier = tierData[currentTier] || tierData.us_ca;
            const purposeInfo = tier.purposes[currentPurpose] || tier.purposes.tourism;

            const tagEl = resultPanel.querySelector('[data-result-tag]');
            const regionEl = resultPanel.querySelector('[data-result-region]');
            const titleEl = resultPanel.querySelector('[data-result-title]');
            const leadEl = resultPanel.querySelector('[data-result-lead]');
            const docEl = resultPanel.querySelector('[data-result-doc]');
            const docSubEl = resultPanel.querySelector('[data-result-doc-sub]');
            const preregEl = resultPanel.querySelector('[data-result-prereg]');
            const preregSubEl = resultPanel.querySelector('[data-result-prereg-sub]');
            const borderEl = resultPanel.querySelector('[data-result-border]');
            const borderSubEl = resultPanel.querySelector('[data-result-border-sub]');
            const itemsEl = resultPanel.querySelector('[data-result-items]');
            const stayEl = resultPanel.querySelector('[data-result-stay]');
            const feeEl = resultPanel.querySelector('[data-result-fee]');
            const timeEl = resultPanel.querySelector('[data-result-time]');

            if (tagEl) {
                tagEl.textContent = tier.tag;
                tagEl.className = 'result-tag ' + tier.tagClass;
            }
            if (regionEl) {
                regionEl.textContent = tier.defaultRegion;
            }
            if (titleEl) titleEl.textContent = purposeInfo.title;
            if (leadEl) leadEl.textContent = purposeInfo.lead;
            if (docEl) docEl.textContent = tier.doc;
            if (docSubEl) docSubEl.textContent = tier.docSub;
            if (preregEl) preregEl.textContent = tier.prereg;
            if (preregSubEl) preregSubEl.textContent = tier.preregSub;
            if (borderEl) borderEl.textContent = tier.border;
            if (borderSubEl) borderSubEl.textContent = tier.borderSub;
            if (stayEl) stayEl.textContent = purposeInfo.stay;
            if (feeEl) feeEl.textContent = purposeInfo.fee;
            if (timeEl) timeEl.textContent = purposeInfo.time;

            if (itemsEl) {
                const checkSvg = '<svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>';
                itemsEl.innerHTML = purposeInfo.items.map(function(item) {
                    return '<li>' + checkSvg + '<span>' + item + '</span></li>';
                }).join('');
            }
        }

        tierCards.forEach(function(card) {
            card.addEventListener('click', function() {
                const targetTier = card.getAttribute('data-checker-tier');
                if (!targetTier || !tierData[targetTier]) return;
                currentTier = targetTier;
                syncTierCards();
                updateResult();
            });
        });

        purposePills.forEach(function(pill) {
            pill.addEventListener('click', function() {
                purposePills.forEach(function(p) { p.classList.remove('is-active'); });
                pill.classList.add('is-active');
                currentPurpose = pill.getAttribute('data-checker-purpose') || 'tourism';
                updateResult();
            });
        });

        syncTierCards();
        updateResult();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVisaChecker);
    } else {
        initVisaChecker();
    }
})();
