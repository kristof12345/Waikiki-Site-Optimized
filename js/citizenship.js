const { useState, useEffect } = React;

// --- ADATOK: KÉRDÉSEK ÉS OPCIÓK ---
const questionsData = [
    // I. DEMOGRÁFIA
    {
        id: 1, section: "Demográfia", text: "Mely régió állampolgára Ön elsődlegesen?",
        options: [
            { label: "OECD tagállam (EU, USA, CAN, AUS, NZ, JPN, KOR)", points: 5 },
            { label: "Latin-Amerika (MERCOSUR államok)", points: 3 },
            { label: "Egyéb régió", points: 0 }
        ]
    },
    {
        id: 2, section: "Demográfia", text: "Hány éves Ön?",
        options: [
            { label: "25 - 45 év között (Gazdaságilag legaktívabb)", points: 4 },
            { label: "20 - 24 év vagy 46 - 55 év között", points: 2 },
            { label: "55 év felett vagy 20 év alatt", points: 0 }
        ]
    },
    {
        id: 3, section: "Demográfia", text: "Mi a jelenlegi családi állapota?",
        options: [
            { label: "Házas, legalább 1 gyermekkel (Nukleáris család)", points: 4 },
            { label: "Házas, gyermektelen", points: 2 },
            { label: "Egyedülálló / Elvált", points: 0 }
        ]
    },
    {
        id: 4, section: "Demográfia", text: "Milyen szinten beszél angolul és van-e stratégiai nyelvtudása?",
        options: [
            { label: "Angol (C1) + Stratégiai nyelv (Mandarin, Orosz, Arab)", points: 4 },
            { label: "Angol (C1)", points: 2 },
            { label: "Angol (B2 vagy alatta)", points: 0, fatal: true }
        ]
    },
    {
        id: 5, section: "Demográfia", text: "Hány napot garantál, hogy fizikailag Waikiki területén tölt évente?",
        options: [
            { label: "Több mint 183 nap (Adóügyi illetőség)", points: 3 },
            { label: "90 - 182 nap", points: 1 },
            { label: "Kevesebb mint 90 nap", points: 0 }
        ]
    },
    // II. GAZDASÁG
    {
        id: 6, section: "Gazdaság", text: "Mi a legmagasabb iskolai végzettsége?",
        options: [
            { label: "STEM PhD vagy Tier 1 diploma (Fúzió, AI, Orvosi)", points: 8 },
            { label: "MSc/MA diploma piaci tapasztalattal", points: 5 },
            { label: "BSc/BA diploma", points: 2 },
            { label: "Nincs felsőfokú végzettségem", points: 0 }
        ]
    },
    {
        id: 7, section: "Gazdaság", text: "Mekkora az Ön igazolt, azonnal mozgósítható likvid vagyona (USD)?",
        options: [
            { label: "Több mint $10,000,000", points: 8 },
            { label: "Több mint $5,000,000", points: 5 },
            { label: "Több mint $250,000", points: 3 },
            { label: "Kevesebb mint $250,000", points: 0 }
        ]
    },
    {
        id: 8, section: "Gazdaság", text: "Vagyonának mekkora hányadát hajlandó a Waikiki Nemzeti Bankba transzferálni?",
        options: [
            { label: "100% (Teljes pénzügyi áttelepülés)", points: 6 },
            { label: "50% - 99%", points: 4 },
            { label: "Kevesebb mint 50%", points: 0 }
        ]
    },
    {
        id: 9, section: "Gazdaság", text: "Milyen ingatlanvásárlást tervez az első évben?",
        options: [
            { label: "Új építésű ingatlan fejlesztési területen (min. $2M)", points: 5 },
            { label: "Használt vagy kisebb értékű ingatlan", points: 3 },
            { label: "Csak bérelni tervezek", points: 0 }
        ]
    },
    {
        id: 10, section: "Gazdaság", text: "Volt-e cége csődeljárás alatt az elmúlt 10 évben?",
        options: [
            { label: "Soha, minden vállalkozásom stabil", points: 5 },
            { label: "Igen, de mindenkit kifizettünk", points: 2 },
            { label: "Igen, csőddel végződött", points: 0, fatal: true }
        ]
    },
    {
        id: 11, section: "Gazdaság", text: "Jövedelmének hány százaléka passzív forrás?",
        options: [
            { label: "Több mint 75%", points: 4 },
            { label: "25% - 74%", points: 2 },
            { label: "Kevesebb mint 25%", points: 0 }
        ]
    },
    {
        id: 12, section: "Gazdaság", text: "Hajlandó-e tőkét fektetni állami stratégiai startupba (min. $250k)?",
        options: [
            { label: "Igen, azonnal", points: 4 },
            { label: "Megfontolom az üzleti terv alapján", points: 2 },
            { label: "Nem", points: 0 }
        ]
    },
    // III. IDEOLÓGIA
    {
        id: 13, section: "Ideológia", text: "Vészhelyzetben elfogadja a magánszámlák 15%-ának ideiglenes zárolását védelmi kötvényért?",
        options: [
            { label: "Azonnal aláírom (Lojalitás)", points: 6 },
            { label: "Mentesítést kérelmezek", points: 3 },
            { label: "Jogi útra terelem / Menekítem a vagyont", points: 0 }
        ]
    },
    {
        id: 14, section: "Ideológia", text: "Hány polgári peres eljárásban vett részt az elmúlt 5 évben?",
        options: [
            { label: "0 (Konfliktusmentes)", points: 5 },
            { label: "1-2 (Normál üzleti kockázat)", points: 3 },
            { label: "3 vagy több", points: -5 }
        ]
    },
    {
        id: 15, section: "Ideológia", text: "Hányszor függesztették fel közösségi média fiókját moderációs okokból?",
        options: [
            { label: "Soha", points: 5 },
            { label: "Egyszer, tévedésből", points: 2 },
            { label: "Többször / Végleges tiltás", points: 0, fatal: true }
        ]
    },
    {
        id: 16, section: "Ideológia", text: "Hova íratná gyermekét a waikiki szegregált, teljesítményalapú oktatási rendszerben?",
        options: [
            { label: "Elit, versenyalapú tehetséggondozóba", points: 4 },
            { label: "Átlagos állami iskolába", points: 2 },
            { label: "Magántanulónak (verseny elutasítása)", points: 0 }
        ]
    },
    {
        id: 17, section: "Ideológia", text: "Embargó esetén megszakítja-e kapcsolatát származási országával?",
        options: [
            { label: "Azonnal megszüntetem az üzleti kapcsolatot", points: 5 },
            { label: "Külön engedélyt kérek", points: 2 },
            { label: "Kijátszom az embargót", points: 0, fatal: true }
        ]
    },
    {
        id: 18, section: "Ideológia", text: "Hajlandó-e átadni teljes biometrikus profilját a 'The Watcher' rendszernek?",
        options: [
            { label: "Igen, teljes körűen", points: 5 },
            { label: "Csak a törvényi minimumot", points: 2 },
            { label: "Nem, elutasítom", points: 0, fatal: true }
        ]
    },
    {
        id: 19, section: "Ideológia", text: "Hajlandó-e 5 éves egészségügyi fedezeti alapot befizetni kockázat esetén?",
        options: [
            { label: "Igen, elfogadom", points: 5 },
            { label: "Csak ha visszatérítendő", points: 3 },
            { label: "Nem, ingyenes ellátást várok", points: 0 }
        ]
    },
    {
        id: 20, section: "Ideológia", text: "Volt-e tagja radikális politikai szervezetnek?",
        options: [
            { label: "Soha, semleges vagyok", points: 5 },
            { label: "Régen, diákként", points: 0 },
            { label: "Igen, jelenleg is", points: 0, fatal: true }
        ]
    }
];

// --- COMPONENTS ---

const colors = {
    primary: '#003366',
    secondary: '#002244',
    tertiary: '#4FB3A9',
    gold: '#C95A41',
    silver: '#9CA3AF',
    bronze: '#B45309',
    dark: '#001830',
    light: '#F5EDE1',
    white: '#FFFFFF',
    danger: '#DC2626'
};

const AssessmentForm = ({ onClose }) => {
    const [currentQ, setCurrentQ] = useState(0);
    const [score, setScore] = useState(0);
    const [isFatal, setIsFatal] = useState(false);
    const [stage, setStage] = useState('intro'); // intro, quiz, analyzing, result

    const handleOptionClick = (points, fatal) => {
        const newScore = score + points;
        setScore(newScore);

        if (fatal) {
            setIsFatal(true);
        }

        if (currentQ < questionsData.length - 1) {
            setCurrentQ(currentQ + 1);
        } else {
            setStage('analyzing');
        }
    };

    useEffect(() => {
        if (stage === 'analyzing') {
            const timer = setTimeout(() => {
                setStage('result');
            }, 3000);
            return () => clearTimeout(timer);
        }
    }, [stage]);

    // ÚJ: 4 Szintű Tier Rendszer + Elutasítás
    const getTier = () => {
        if (isFatal) return 'REJECTED';
        if (score >= 90) return 'GOLD';
        if (score >= 75) return 'SILVER';
        if (score >= 60) return 'BRONZE';
        if (score >= 45) return 'BLUE';
        return 'REJECTED';
    };

    const tier = getTier();
    const progress = (currentQ / questionsData.length) * 100;

    const isEn = typeof document !== 'undefined' && document.documentElement.lang === 'en';

    const renderIntro = () => (
        <div className="text-center p-4 sm:p-6">
            <div className="w-14 h-14 sm:w-20 sm:h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-3 sm:mb-6">
                <img src="../icons/mdi/scale-balance.svg" alt="" className="w-8 h-8 sm:w-10 sm:h-10" />
            </div>
            <h3 className="text-xl sm:text-3xl font-bold mb-2 sm:mb-4" style={{ color: colors.secondary }}>{isEn ? "W-MAP Protocol" : "W-MAP Protokoll"}</h3>
            <p className="text-gray-600 text-sm sm:text-base mb-3 sm:mb-6">{isEn ? "The Waikiki Merit Assessment Protocol is a multi-tier evaluation system designed to measure talent, capital, and long-term commitment. The system recognizes 4 eligibility tiers." : "A Waikiki Merit Assessment Protocol egy többszintű értékelési rendszer. Célunk nem csak a vagyon, hanem a tehetség és az elkötelezettség mérése. A rendszer 4 jogosultsági szintet különböztet meg."}</p>
            <div className="bg-yellow-50 border border-yellow-200 p-3 sm:p-4 rounded-lg text-xs sm:text-sm text-left mb-4 sm:mb-6">
                <p className="font-bold text-yellow-800 mb-1 sm:mb-2 flex items-center gap-1.5"><img src="../icons/mdi/shield-alert.svg" alt="" className="w-4 h-4 inline-block" />{isEn ? "Important Notice" : "Figyelmeztetés"}</p>
                <ul className="list-disc list-inside text-yellow-700 space-y-1">
                    <li>{isEn ? "Your responses constitute a legal declaration." : "A válaszai jogi kötelezettségvállalásnak minősülnek."}</li>
                    <li>{isEn ? "The Watcher AI verifies credentials and public data in the background." : "A \"The Watcher\" AI minden adatot ellenőriz a háttérben."}</li>
                    <li>{isEn ? "Providing fraudulent information results in automatic permanent disqualification." : "A hamis adatszolgáltatás automatikus kitiltással jár."}</li>
                </ul>
            </div>
            <button onClick={() => setStage('quiz')} className="w-full py-3 sm:py-4 rounded-lg text-white font-bold text-base sm:text-lg shadow-lg hover:scale-[1.01] active:scale-[0.99] transition-transform" style={{ backgroundColor: colors.primary }}>{isEn ? "Begin Assessment" : "Értékelés Indítása"}</button>
        </div>
    );

    const renderQuiz = () => {
        const q = questionsData[currentQ];
        return (
            <div className="p-4 sm:p-6">
                <div className="mb-4 sm:mb-6">
                    <div className="flex justify-between text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5 sm:mb-2">
                        <span>{q.section}</span>
                        <span>{currentQ + 1} / {questionsData.length}</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full transition-all duration-500 ease-out" style={{ width: `${progress}%`, backgroundColor: colors.gold }}></div>
                    </div>
                </div>

                <h4 className="text-lg sm:text-2xl font-bold mb-4 sm:mb-6 text-gray-800 leading-snug">{q.text}</h4>

                <div className="space-y-2.5 sm:space-y-3">
                    {q.options.map((opt, idx) => (
                        <button key={idx} onClick={() => handleOptionClick(opt.points, opt.fatal)} className="w-full text-left p-3 sm:p-4 rounded-xl border border-gray-200 hover:border-blue-500 hover:bg-blue-50 transition-all group flex items-start gap-2.5 sm:gap-3 text-sm sm:text-base">
                            <div className="w-5 h-5 sm:w-6 sm:h-6 rounded-full border-2 border-gray-300 group-hover:border-blue-500 flex-shrink-0 mt-0.5"></div>
                            <span className="text-gray-700 font-medium group-hover:text-blue-900">{opt.label}</span>
                        </button>
                    ))}
                </div>
            </div>
        );
    };

    const renderAnalyzing = () => (
        <div className="text-center p-6 sm:p-12 flex flex-col items-center justify-center min-h-[300px]">
            <div className="w-16 h-16 sm:w-24 sm:h-24 rounded-full border-4 border-t-transparent animate-spin mb-4 sm:mb-8" style={{ borderColor: `${colors.gold} transparent ${colors.gold} ${colors.gold}` }}></div>
            <h3 className="text-xl sm:text-2xl font-bold mb-2 animate-pulse" style={{ color: colors.secondary }}>{isEn ? "The Watcher is Analyzing..." : "The Watcher Elemzése..."}</h3>
            <p className="text-gray-500 text-xs sm:text-sm">{isEn ? "Verifying biometric credentials... Validating financial background... Computing merit score..." : "Biometrikus adatok ellenőrzése... Pénzügyi háttér validálása... Social Credit pontszámítás..."}</p>
        </div>
    );

    const renderResult = () => {
        let title, desc, icon, bgClass, btnText, badge;

        switch (tier) {
            case 'GOLD':
                title = isEn ? 'GOLD TIER: Strategic Asset' : 'GOLD TIER: Stratégiai Vagyontárgy';
                desc = isEn ? 'Immediate citizenship. You are an exemplary candidate. Zero waiting period, no real estate minimum, VIP fast-track processing.' : 'Azonnali állampolgárság. Ön a tökéletes jelölt. Nincs várakozási idő, nincs ingatlanminimum, VIP ügyintézés.';
                icon = '../icons/mdi/crown.svg';
                bgClass = 'border-yellow-400';
                btnText = isEn ? 'Official Application ($5,000)' : 'Hivatalos Kérelem ($5,000)';
                badge = isEn ? '90+ POINTS' : '90+ PONT';
                break;
            case 'SILVER':
                title = isEn ? 'SILVER TIER: Priority Investor' : 'SILVER TIER: Kiemelt Befektető';
                desc = isEn ? 'Accelerated procedure. Citizenship after 1 year, subject to $1M bond purchase and qualifying property investment.' : 'Gyorsított eljárás. Állampolgárság 1 év után, feltéve, hogy teljesíti a $1M kötvényvásárlást és az ingatlanbefektetést.';
                icon = '../icons/mdi/medal.svg';
                bgClass = 'border-gray-400';
                btnText = isEn ? 'Start Investment Plan' : 'Befektetési Terv Indítása';
                badge = isEn ? '75-89 POINTS' : '75-89 PONT';
                break;
            case 'BRONZE':
                title = isEn ? 'BRONZE TIER: Skilled Resident' : 'BRONZE TIER: Szakképzett Rezidens';
                desc = isEn ? 'Residency permit. Citizenship eligible after 5 years. Security deposit ($100k) and verified employment required.' : 'Letelepedési engedély (Residency). Állampolgárság 5 év után kérvényezhető. Biztonsági letét ($100k) és igazolt munkaviszony szükséges.';
                icon = '../icons/mdi/shield-account.svg';
                bgClass = 'border-orange-300';
                btnText = isEn ? 'Residency Application' : 'Letelepedési Kérelem';
                badge = isEn ? '60-74 POINTS' : '60-74 PONT';
                break;
            case 'BLUE':
                title = isEn ? 'BLUE TIER: Talent / Nomad Visa' : 'BLUE TIER: Talent / Nomad Vízum';
                desc = isEn ? 'Temporary residency status for young innovators and specialized talent. 10-year pathway to citizenship.' : 'Ideiglenes munkavállalói státusz. Fiatal tehetségeknek, akik nem rendelkeznek nagy vagyonnal, de kritikus tudással igen. 10 éves út az állampolgárságig.';
                icon = '../icons/mdi/laptop.svg';
                bgClass = 'border-blue-300';
                btnText = isEn ? 'Apply to Talent Program' : 'Talent Program Jelentkezés';
                badge = isEn ? '45-59 POINTS' : '45-59 PONT';
                break;
            default:
                title = isEn ? 'DECLINED: High Risk' : 'ELUTASÍTVA: High Risk';
                desc = isFatal
                    ? (isEn ? 'The system identified a disqualifying condition (Red Flag). Application declined.' : 'A rendszer KIZÁRÓ OKOT (Red Flag) azonosított. Kérelmét elutasítottuk.')
                    : (isEn ? 'Your score (below 45) does not meet the minimum eligibility threshold.' : 'Pontszáma (45 alatt) nem éri el a minimális belépési küszöböt.');
                icon = '../icons/mdi/cloud-alert.svg';
                bgClass = 'border-red-200';
                btnText = isEn ? 'Close' : 'Bezárás';
                badge = isEn ? 'INSUFFICIENT' : 'ELÉGTELEN';
        }

        return (
            <div className="p-4 sm:p-8 text-center animate-fade-up">
                <div className={`w-14 h-14 sm:w-20 sm:h-20 rounded-full flex items-center justify-center mx-auto mb-3 sm:mb-6 shadow-xl ${tier === 'REJECTED' ? 'bg-red-100' : 'bg-white'}`}>
                    <img src={icon} alt="" className="w-8 h-8 sm:w-10 sm:h-10" />
                </div>

                <div className={`p-4 sm:p-6 rounded-xl border-2 mb-4 sm:mb-6 relative overflow-hidden ${bgClass}`}>
                    <div className="absolute top-0 right-0 px-2.5 py-0.5 sm:px-3 sm:py-1 bg-black/10 text-[10px] sm:text-xs font-bold rounded-bl-lg">{badge}</div>
                    <h3 className="text-xl sm:text-2xl font-bold mb-1.5 sm:mb-2 text-gray-900">{title}</h3>
                    <div className="text-3xl sm:text-4xl font-extrabold mb-2 sm:mb-4" style={{ color: tier === 'REJECTED' ? colors.danger : colors.primary }}>{score} / 100</div>
                    <p className="text-gray-700 leading-relaxed text-xs sm:text-sm">{desc}</p>
                </div>

                {tier !== 'REJECTED' && (
                    <div className="text-left bg-gray-50 p-3 sm:p-4 rounded-lg mb-4 sm:mb-6 text-xs sm:text-sm text-gray-600">
                        <p><strong>{isEn ? 'Next step:' : 'Következő lépés:'}</strong> {isEn ? 'Based on your tier evaluation, you qualify to initiate this program. Please proceed with booking an appointment for biometric credentialing.' : 'A besorolása alapján Ön jogosult a fenti program elindítására. Kérjük, foglaljon időpontot a biometrikus azonosításra.'}</p>
                    </div>
                )}

                <button onClick={onClose} className={`w-full py-3 sm:py-4 rounded-lg text-white font-bold text-base sm:text-lg shadow-lg transition-transform hover:scale-[1.01] active:scale-[0.99] ${tier === 'REJECTED' ? 'bg-gray-500' : 'bg-[#C95A41]'}`}>{btnText}</button>
            </div>
        );
    };

    return (
        <div className="assessment-modal-overlay fixed inset-0 z-[9999] flex items-center justify-center p-2 sm:p-4 bg-black/80 backdrop-blur-md">
            <div className="assessment-modal bg-white rounded-xl sm:rounded-2xl w-full max-w-4xl max-h-[92dvh] sm:max-h-[90vh] flex flex-col shadow-2xl relative overflow-hidden">
                <div className="assessment-modal-header flex-shrink-0 bg-white/95 backdrop-blur px-4 py-3 sm:px-6 sm:py-4 border-b flex justify-between items-center z-10">
                    <span className="assessment-modal-meta font-bold text-gray-400 text-[11px] sm:text-xs tracking-widest">W-MAP v2.1 PROTOCOL</span>
                    <button onClick={onClose} className="assessment-modal-close text-gray-400 hover:text-red-500 transition-colors text-2xl font-bold leading-none p-1" aria-label="Close modal">
                        &times;
                    </button>
                </div>

                <div className="assessment-modal-body flex-1 overflow-y-auto overscroll-contain">
                    {stage === 'intro' && renderIntro()}
                    {stage === 'quiz' && renderQuiz()}
                    {stage === 'analyzing' && renderAnalyzing()}
                    {stage === 'result' && renderResult()}
                </div>
            </div>
        </div>
    );
};

// Modal mounting helpers: render AssessmentForm into #modal-root
let modalRoot = null;

function openAssessment() {
    const el = document.getElementById('modal-root');
    if (!el) return;
    if (!modalRoot) modalRoot = ReactDOM.createRoot(el);
    modalRoot.render(React.createElement(AssessmentForm, { onClose: closeAssessment }));
    document.body.style.overflow = 'hidden';
}

function closeAssessment() {
    if (!modalRoot) return;
    modalRoot.unmount();
    modalRoot = null;
    document.body.style.overflow = '';
}

function initAssessmentBindings() {
    document.querySelectorAll('.open-assessment').forEach(btn => {
        btn.addEventListener('click', openAssessment);
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeAssessment();
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAssessmentBindings);
} else {
    initAssessmentBindings();
}
