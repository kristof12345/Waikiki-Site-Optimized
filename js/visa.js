/**
 * Visa and Entry Requirements — Interactive Logic
 * Sovereign Nation of Waikiki
 */
(function() {
    'use strict';

    function initVisaChecker() {
        const checker = document.getElementById('visa-checker');
        if (!checker) return;

        const nationalitySelect = checker.querySelector('[data-checker-nationality]');
        const purposePills = checker.querySelectorAll('[data-checker-purpose]');
        const resultPanel = checker.querySelector('[data-checker-result]');
        if (!nationalitySelect || !resultPanel) return;

        const isHungarian = (document.documentElement.lang || 'en') === 'hu';

        const data = {
            visaFree: {
                tag: isHungarian ? 'Vízummentes Belépés' : 'Visa-Free Access',
                tagClass: 'tag-free',
                title: isHungarian ? 'Automatikus Biometrikus Belépés' : 'Automatic Biometric Clearance',
                lead: isHungarian
                    ? 'Ön jogosult vízummentesen belépni Waikiki Szuverén Államba turizmus, kulturális és üzleti célból.'
                    : 'You are eligible to enter the Sovereign Nation of Waikiki visa-free for tourism, cultural exchange, and business meetings.',
                items: isHungarian
                    ? [
                        'Érvényes útlevél (legalább 6 hónap érvényességgel a tervezett távozástól)',
                        'Ingyenes előzetes regisztráció a Waikiki One rendszerben',
                        'Visszaúti vagy továbbutazási menetjegy igazolása',
                        'Érintésmentes áthaladás a SmartBorder biometrikus e-kapukon'
                    ]
                    : [
                        'Valid national passport (minimum 6 months validity beyond travel)',
                        'Free pre-departure Waikiki One digital registration token',
                        'Proof of return or onward transportation booking',
                        'Contactless pass through SmartBorder biometric e-gates'
                    ],
                stay: isHungarian ? 'Legfeljebb 30 nap' : 'Up to 30 Days',
                fee: isHungarian ? '0 WUD (Díjmentes)' : '0 WUD (Free)',
                time: isHungarian ? 'Azonnali engedély' : 'Instant Clearance'
            },
            evisa: {
                tag: isHungarian ? 'Waikiki One e-Vízum' : 'Waikiki One e-Visa',
                tagClass: 'tag-evisa',
                title: isHungarian ? 'Gyorsított Digitális Utazási Engedély' : 'Fast-Track Digital Authorization',
                lead: isHungarian
                    ? 'Ön jogosult a Waikiki One online portálon keresztüli azonnali elektronikus vízum igénylésére.'
                    : 'You are eligible for streamlined online e-Visa issuance via the Waikiki One sovereign portal.',
                items: isHungarian
                    ? [
                        'Érvényes nemzeti útlevél digitális másolata',
                        'Waikiki One online űrlap kitöltése',
                        'Szállásfoglalás vagy meghívólevél igazolása',
                        'Automatikus biometrikus ellenőrzés a határon'
                    ]
                    : [
                        'Digital biometric passport scan upload',
                        'Standard online Waikiki One traveler questionnaire',
                        'Confirmed accommodation or sovereign host invitation',
                        'Instant QR pass verification at all border entry gates'
                    ],
                stay: isHungarian ? '30 nap (meghosszabbítható)' : '30 Days (Extendable)',
                fee: isHungarian ? '35 WUD (kb. 88 USD)' : '35 WUD (approx $88 USD)',
                time: isHungarian ? '15 percen belül kiadva' : 'Under 15 Minutes'
            },
            business: {
                tag: isHungarian ? 'Üzleti és Befektetői Sáv' : 'Sovereign Business Lane',
                tagClass: 'tag-evisa',
                title: isHungarian ? 'Kiemelt Gazdasági és Fórum Engedély' : 'Priority Economic Delegate Authorization',
                lead: isHungarian
                    ? 'Kiemelt belépési és gyorsított határátlépési jog üzleti tárgyalásokhoz és befektetési fórumokhoz.'
                    : 'Priority entry status and VIP consular lane for commercial partners, symposium attendees, and investors.',
                items: isHungarian
                    ? [
                        'Hivatalos vállalati vagy fórum meghívólevél',
                        'Kiemelt gyorsított átlépés a Nova Aurelia VIP szalonon keresztül',
                        'Hozzáférés a Vagyonalap üzleti partnerhálózatához',
                        'Többszöri belépésre jogosító 1 éves érvényesség'
                    ]
                    : [
                        'Accredited corporate, forum, or investment delegation letter',
                        'VIP terminal fast-track through Aurelia Executive Lounge',
                        'Direct integration with Sovereign Wealth Fund trade liaison',
                        '1 to 3 year multiple entry validity'
                    ],
                stay: isHungarian ? '90 nap / látogatás' : '90 Days / Entry',
                fee: isHungarian ? '120 WUD' : '120 WUD',
                time: isHungarian ? '24 órán belül' : 'Under 24 Hours'
            },
            transit: {
                tag: isHungarian ? '48 Órás Tranzit Engedély' : '48-Hour Transit Pass',
                tagClass: 'tag-free',
                title: isHungarian ? 'Zökkenőmentes Átszállás és Városlátogatás' : 'Seamless Intercontinental Transit',
                lead: isHungarian
                    ? 'Nova Aurelián vagy a Csendes-óceáni Kapun áthaladó utasok díjmentesen felfedezhetik a fővárost.'
                    : 'Passengers transiting through Nova Aurelia may explore the capital without visa fees.',
                items: isHungarian
                    ? [
                        'Megerősített csatlakozó repülőjegy 48 órán belüli indulással',
                        'Digitális tranzitkártya a Waikiki One alkalmazásban',
                        'Díjmentes expressz maglev vasúti jegy a belvárosba',
                        'Poggyász automatikus átszállítása a végcél felé'
                    ]
                    : [
                        'Confirmed onward boarding pass within 48 hours',
                        'Instant digital transit pass issued upon arrival',
                        'Free Nova Aurelia Express Maglev return transit token',
                        'Automated baggage through-check to onward flight'
                    ],
                stay: isHungarian ? 'Legfeljebb 48 óra' : 'Up to 48 Hours',
                fee: isHungarian ? '0 WUD (Díjmentes)' : '0 WUD (Free)',
                time: isHungarian ? 'Azonnali kapunyitás' : 'Instant at Gate'
            }
        };

        let currentNationality = nationalitySelect.value || 'au_eu';
        let currentPurpose = 'tourism';

        function updateResult() {
            let selectedType = 'visaFree';

            if (currentPurpose === 'transit') {
                selectedType = 'transit';
            } else if (currentPurpose === 'business' && (currentNationality === 'other' || currentNationality === 'latam')) {
                selectedType = 'business';
            } else if (currentNationality === 'other') {
                selectedType = 'evisa';
            } else if (currentNationality === 'latam' && currentPurpose !== 'tourism') {
                selectedType = 'business';
            } else {
                selectedType = 'visaFree';
            }

            const info = data[selectedType];
            const tagEl = resultPanel.querySelector('[data-result-tag]');
            const titleEl = resultPanel.querySelector('[data-result-title]');
            const leadEl = resultPanel.querySelector('[data-result-lead]');
            const itemsEl = resultPanel.querySelector('[data-result-items]');
            const stayEl = resultPanel.querySelector('[data-result-stay]');
            const feeEl = resultPanel.querySelector('[data-result-fee]');
            const timeEl = resultPanel.querySelector('[data-result-time]');

            if (tagEl) {
                tagEl.textContent = info.tag;
                tagEl.className = 'result-tag ' + info.tagClass;
            }
            if (titleEl) titleEl.textContent = info.title;
            if (leadEl) leadEl.textContent = info.lead;
            if (stayEl) stayEl.textContent = info.stay;
            if (feeEl) feeEl.textContent = info.fee;
            if (timeEl) timeEl.textContent = info.time;

            if (itemsEl) {
                const checkSvg = '<svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>';
                itemsEl.innerHTML = info.items.map(function(item) {
                    return '<li>' + checkSvg + '<span>' + item + '</span></li>';
                }).join('');
            }
        }

        nationalitySelect.addEventListener('change', function(e) {
            currentNationality = e.target.value;
            updateResult();
        });

        purposePills.forEach(function(pill) {
            pill.addEventListener('click', function() {
                purposePills.forEach(function(p) { p.classList.remove('is-active'); });
                pill.classList.add('is-active');
                currentPurpose = pill.getAttribute('data-checker-purpose') || 'tourism';
                updateResult();
            });
        });

        updateResult();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVisaChecker);
    } else {
        initVisaChecker();
    }
})();
