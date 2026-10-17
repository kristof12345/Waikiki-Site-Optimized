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
        const resultPanel = checker.querySelector('[data-checker-result]');
        if (!tierCards.length || !resultPanel) return;

        const isHungarian = (document.documentElement.lang || 'en') === 'hu';

        const tierData = {
            us_ca: {
                defaultRegion: isHungarian ? 'Egyesült Államok és Kanada' : 'United States and Canada',
                tag: isHungarian ? 'Igazolvánnyal szabad belépés' : 'ID-Only Direct Entry',
                tagClass: 'tag-free',
                doc: isHungarian ? 'Elég egy igazolvány' : 'Photo ID Suffices',
                prereg: isHungarian ? 'Nem kell regisztráció' : 'No Registration Required',
                border: isHungarian ? 'Digitális határellenőrzés' : 'Digital Border Control',
                title: isHungarian
                    ? 'Belépés igazolvánnyal és digitális határellenőrzéssel'
                    : 'Direct Photo ID Entry and Digital Border Control',
                lead: isHungarian
                    ? 'Az Egyesült Államok és Kanada állampolgárainak nem kell előzetes regisztráció és útlevél. Elég egy fényképes igazolvány, a belépés pedig digitális határellenőrzéssel történik.'
                    : 'Citizens of the United States and Canada do not need advance registration and passport. A photo ID is sufficient, and entry is processed with digital border control.',
                stay: isHungarian ? 'Legfeljebb 60 nap' : 'Up to 60 Days',
                fee: isHungarian ? '0 WUD (Díjmentes)' : '0 WUD (Free)',
                time: isHungarian ? 'Azonnali beléptetés' : 'Instant at Gate'
            },
            eu_ch_au_uk: {
                defaultRegion: isHungarian
                    ? 'EU, Egyesült Királyság, Svájc, Ausztrália és Új-Zéland'
                    : 'EU, United Kingdom, Switzerland, Australia and New Zealand',
                tag: isHungarian ? 'Vízummentes · 24 órás regisztráció' : 'Visa-Free · 24h Registration',
                tagClass: 'tag-fast',
                doc: isHungarian ? 'Útlevél szükséges' : 'Passport Required',
                prereg: isHungarian ? 'Előzetes regisztráció (24 óra)' : 'Pre-Registration (24 Hours)',
                border: isHungarian ? 'Digitális határellenőrzés' : 'Digital Border Control',
                title: isHungarian
                    ? 'Útlevél, 24 órás előzetes regisztráció és digitális kapu'
                    : 'Passport with 24-Hour Pre-Registration and Digital Gate',
                lead: isHungarian
                    ? 'Az EU, az Egyesült Királyság, Svájc, Ausztrália és Új-Zéland állampolgárainak útlevél és 24 órás előzetes regisztráció szükséges, a belépés pedig digitális határellenőrzéssel történik.'
                    : 'Citizens of the EU, United Kingdom, Switzerland, Australia, and New Zealand require a valid passport and 24-hour advance registration, with digital border control upon arrival.',
                stay: isHungarian ? 'Legfeljebb 30 nap' : 'Up to 30 Days',
                fee: isHungarian ? '0 WUD (Díjmentes)' : '0 WUD (Free)',
                time: isHungarian ? '24 órás előzetes regisztráció' : '24h Advance Registration'
            },
            jp_ar_partners: {
                defaultRegion: isHungarian
                    ? 'Amerikai Unió, Japán, Argentína, Dél-Korea és Szingapúr'
                    : 'American Union, Japan, Argentina, South Korea and Singapore',
                tag: isHungarian ? 'Vízummentes · 48 órás regisztráció' : 'Visa-Free · 48h Registration',
                tagClass: 'tag-fast',
                doc: isHungarian ? 'Útlevél szükséges' : 'Passport Required',
                prereg: isHungarian ? 'Előzetes regisztráció (48 óra)' : 'Pre-Registration (48 Hours)',
                border: isHungarian ? 'Digitális határellenőrzés' : 'Digital Border Control',
                title: isHungarian
                    ? 'Útlevél, 48 órás előzetes regisztráció és digitális kapu'
                    : 'Passport with 48-Hour Pre-Registration and Digital Gate',
                lead: isHungarian
                    ? 'Az Amerikai Unió, Japán, Argentína, Dél-Korea és Szingapúr állampolgárainak útlevél és 48 órás előzetes regisztráció szükséges, a beléptetés pedig digitális határellenőrzéssel zajlik.'
                    : 'Citizens of the American Union, Japan, Argentina, South Korea, and Singapore require a passport and 48-hour advance registration, clearing arrival through digital border control.',
                stay: isHungarian ? 'Legfeljebb 30 nap' : 'Up to 30 Days',
                fee: isHungarian ? '0 WUD (Díjmentes)' : '0 WUD (Free)',
                time: isHungarian ? '48 órás előzetes regisztráció' : '48h Advance Registration'
            },
            partner_other: {
                defaultRegion: isHungarian ? 'További partner országok' : 'Additional Partner Countries',
                tag: isHungarian ? 'Egyszerűsített e-Visa · Digitális kapu' : 'Simplified e-Visa · Digital Gate',
                tagClass: 'tag-evisa',
                doc: isHungarian ? 'Biometrikus útlevél szükséges' : 'Biometric Passport Required',
                prereg: isHungarian ? 'Egyszerűsített e-Visa' : 'Simplified e-Visa',
                border: isHungarian ? 'Digitális határellenőrzés' : 'Digital Border Control',
                title: isHungarian
                    ? 'Egyszerűsített e-Visa és digitális határellenőrzés'
                    : 'Simplified e-Visa with Digital Border Control',
                lead: isHungarian
                    ? 'A további partner országok állampolgárai egyszerűsített online e-Visa igényléssel utazhatnak be, és érkezéskor a gyorsított digitális határellenőrzést vehetik igénybe.'
                    : 'Citizens of additional partner countries with a biometric passport qualify for a simplified online e-Visa registration process. They enjoy automated digital border control upon arrival.',
                stay: isHungarian ? 'Legfeljebb 30 nap' : 'Up to 30 Days',
                fee: isHungarian ? '20 WUD (Kedvezményes)' : '20 WUD (Partner Rate)',
                time: isHungarian ? '1-2 napon belül' : 'Within 1-2 Days'
            },
            developed_other: {
                defaultRegion: isHungarian ? 'További fejlett országok' : 'Additional Developed Countries',
                tag: isHungarian ? 'Normál e-Visa · Személyes ellenőrzés' : 'Standard e-Visa · In-Person Control',
                tagClass: 'tag-evisa',
                doc: isHungarian ? 'Útlevél szükséges' : 'Passport Required',
                prereg: isHungarian ? 'Online e-Visa' : 'Standard e-Visa',
                border: isHungarian ? 'Személyes határellenőrzés' : 'In-Person Border Control',
                title: isHungarian
                    ? 'Online e-Visa és személyes határellenőrzés'
                    : 'Standard e-Visa and In-Person Border Control',
                lead: isHungarian
                    ? 'A további fejlett országok állampolgárai előzetesen online igényelhető e-Visa engedéllyel utazhatnak be, érkezéskor pedig személyes határellenőrzésen vesznek részt.'
                    : 'Citizens of additional developed countries apply online for a standard e-Visa prior to travel and must complete traditional in-person border inspection upon arrival.',
                stay: isHungarian ? 'Legfeljebb 30 nap' : 'Up to 30 Days',
                fee: isHungarian ? '35 WUD' : '35 WUD',
                time: isHungarian ? '1 héten belül' : 'Within 1 Week'
            },
            other_world: {
                defaultRegion: isHungarian ? 'Egyéb országok' : 'Other Countries',
                tag: isHungarian ? 'Vízum igénylés · Személyes ellenőrzés' : 'Visa Application · In-Person Control',
                tagClass: 'tag-visa',
                doc: isHungarian ? 'Útlevél és vízum' : 'Passport and Visa',
                prereg: isHungarian ? 'Vízum igénylés' : 'Visa Application',
                border: isHungarian ? 'Személyes határellenőrzés' : 'In-Person Border Control',
                title: isHungarian
                    ? 'Előzetes vízum igénylés és személyes határellenőrzés'
                    : 'Consular Visa Application and In-Person Border Control',
                lead: isHungarian
                    ? 'Az egyéb országok állampolgárainak utazás előtt hivatalos vízum igénylés szükséges, melynek elbírálása akár 2 hetet vehet igénybe. A beléptetés pedig személyes határellenőrzéssel történik.'
                    : 'Citizens of other countries must complete a formal consular visa application prior to travel. The evaluation may take up to 2 weeks. Entry is through in-person border control.',
                stay: isHungarian ? 'Legfeljebb 30 nap' : 'Up to 30 Days',
                fee: isHungarian ? '60 WUD' : '60 WUD',
                time: isHungarian ? '5-10 munkanap' : '5 to 10 Business Days'
            }
        };

        let currentTier = 'us_ca';

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

            const tagEl = resultPanel.querySelector('[data-result-tag]');
            const regionEl = resultPanel.querySelector('[data-result-region]');
            const titleEl = resultPanel.querySelector('[data-result-title]');
            const leadEl = resultPanel.querySelector('[data-result-lead]');
            const docEl = resultPanel.querySelector('[data-result-doc]');
            const preregEl = resultPanel.querySelector('[data-result-prereg]');
            const borderEl = resultPanel.querySelector('[data-result-border]');
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
            if (titleEl) titleEl.textContent = tier.title;
            if (leadEl) leadEl.textContent = tier.lead;
            if (docEl) docEl.textContent = tier.doc;
            if (preregEl) preregEl.textContent = tier.prereg;
            if (borderEl) borderEl.textContent = tier.border;
            if (stayEl) stayEl.textContent = tier.stay;
            if (feeEl) feeEl.textContent = tier.fee;
            if (timeEl) timeEl.textContent = tier.time;
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

        syncTierCards();
        updateResult();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVisaChecker);
    } else {
        initVisaChecker();
    }
})();
