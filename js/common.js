/* ==========================================================================
   WAIKIKI — SHARED INTERACTION & MOTION ENGINE
   Loaded on every page. Page-specific scripts (economy.js, gallery.js, …)
   run independently on top of this file.

   Modules:
     theme        Night-mode toggle (persisted in localStorage)
     curtain      Page enter/leave transition
     header       Scrolled / hidden / on-hero header states
     menu         Full-screen overlay menu + live capital clock
     reveal       Scroll-triggered reveal + word-split headlines
     counters     Count-up animation for statistics
     parallax     Hero parallax and [data-parallax] layers
     pointer      Card spotlight and magnetic buttons
     rail         Auto-generated section navigation rail
     progress     Scroll progress bar + back-to-top ring
     timeline     Scroll-drawn timeline line
   ========================================================================== */

(function () {
    'use strict';

    const root = document.documentElement;
    const DARK_STORAGE_KEY = 'isDarkMode';
    const DARK_CLASS = 'body-dark';
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

    /* ---------------------------------------------------------------- utils */
    const $ = (selector, scope = document) => scope.querySelector(selector);
    const $$ = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));

    /** Run a callback at most once per animation frame. */
    function rafThrottle(callback) {
        let queued = false;
        return (...args) => {
            if (queued) return;
            queued = true;
            requestAnimationFrame(() => {
                queued = false;
                callback(...args);
            });
        };
    }

    /* ---------------------------------------------------------------- theme */
    function isDark() {
        return root.classList.contains(DARK_CLASS);
    }

    function applyTheme(dark) {
        root.classList.toggle(DARK_CLASS, dark);
        document.body.classList.remove(DARK_CLASS, 'body-light');
        try {
            localStorage.setItem(DARK_STORAGE_KEY, String(dark));
        } catch (e) { /* storage unavailable */ }
        $$('[data-theme-toggle]').forEach((button) => {
            button.setAttribute('aria-pressed', String(dark));
            if (button.classList.contains('menu-chip')) {
                button.classList.toggle('is-active', dark);
            }
        });
        const meta = $('meta[name="theme-color"]');
        if (meta) meta.setAttribute('content', dark ? '#0a1c1b' : '#fbf7f0');
        document.dispatchEvent(new CustomEvent('themechange', { detail: { dark } }));
    }

    /** Global for backwards compatibility with inline onclick handlers. */
    window.setTheme = function () {
        applyTheme(!isDark());
    };

    function initTheme() {
        let stored = null;
        try {
            stored = localStorage.getItem(DARK_STORAGE_KEY);
        } catch (e) { /* storage unavailable */ }
        applyTheme(stored === 'true');
        $$('[data-theme-toggle]').forEach((button) => {
            button.addEventListener('click', () => {
                root.classList.add('theme-transition');
                window.setTheme();
            });
        });
    }

    /* -------------------------------------------------------------- animate */
    const ANIMATION_STORAGE_KEY = 'isAnimationDisabled';

    function isAnimate() {
        return !root.classList.contains('no-reveal');
    }

    function applyAnimate(enabled) {
        root.classList.toggle('no-reveal', !enabled);
        try {
            localStorage.setItem(ANIMATION_STORAGE_KEY, String(!enabled));
        } catch (e) { /* storage unavailable */ }

        $$('[data-animate-toggle]').forEach((button) => {
            button.setAttribute('aria-pressed', String(enabled));
            button.classList.toggle('is-disabled', !enabled);
            if (button.classList.contains('menu-chip')) {
                button.classList.toggle('is-active', enabled);
            }
        });

        if (!enabled) {
            $$('[data-reveal]').forEach((element) => {
                element.classList.add('is-in');
            });
            $$('.split-word > span').forEach((span) => {
                span.style.transform = 'none';
                span.style.opacity = '1';
            });
        } else if ('IntersectionObserver' in window && !prefersReducedMotion && window._revealObserver) {
            $$('[data-reveal]').forEach((element) => {
                const rect = element.getBoundingClientRect();
                if (rect.top > window.innerHeight) {
                    element.classList.remove('is-in');
                    window._revealObserver.observe(element);
                }
            });
        }

        document.dispatchEvent(new CustomEvent('animatechange', { detail: { enabled } }));
    }

    window.toggleAnimate = function () {
        applyAnimate(!isAnimate());
    };

    function initAnimate() {
        let disabled = false;
        try {
            disabled = localStorage.getItem(ANIMATION_STORAGE_KEY) === 'true';
        } catch (e) { /* storage unavailable */ }
        applyAnimate(!disabled);
        $$('[data-animate-toggle]').forEach((button) => {
            button.addEventListener('click', () => {
                window.toggleAnimate();
            });
        });
    }

    /* -------------------------------------------------------------- curtain */
    function initCurtain() {
        // Restore pages served from the back/forward cache.
        window.addEventListener('pageshow', (event) => {
            if (event.persisted) root.classList.remove('is-leaving');
        });

        if (prefersReducedMotion || !isAnimate()) return;

        document.addEventListener('click', (event) => {
            const link = event.target.closest('a[href]');
            if (!link || event.defaultPrevented) return;
            if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
            if (link.target && link.target !== '_self') return;
            if (link.hasAttribute('download')) return;

            const url = new URL(link.href, window.location.href);
            if (url.origin !== window.location.origin) return;
            if (url.pathname === window.location.pathname && url.hash) return;
            if (!/\.html?$|\/$/.test(url.pathname)) return;

            event.preventDefault();
            root.classList.add('is-leaving');
            window.setTimeout(() => { window.location.href = url.href; }, 520);
        });
    }

    /* --------------------------------------------------------------- header */
    function initHeader() {
        const header = $('.site-header');
        if (!header) return;

        const hero = $('main > .hero:not(.hero--compact), main > .min-h-screen:first-child');
        let lastY = window.scrollY;

        const update = () => {
            const y = window.scrollY;
            const heroBottom = hero ? hero.offsetHeight - header.offsetHeight : 0;
            const scrolled = y > 24;
            const goingDown = y > lastY + 4;
            const goingUp = y < lastY - 4;

            header.classList.toggle('is-scrolled', scrolled);
            header.classList.toggle('on-hero', Boolean(hero) && y < heroBottom - 40 && !scrolled);

            if (!root.classList.contains('menu-open')) {
                if (goingDown && y > 320) {
                    header.classList.add('is-hidden');
                    root.classList.add('header-hidden');
                } else if (goingUp || y < 320) {
                    header.classList.remove('is-hidden');
                    root.classList.remove('header-hidden');
                }
            }
            lastY = y;
        };

        update();
        window.addEventListener('scroll', rafThrottle(update), { passive: true });
    }

    /* ----------------------------------------------------------------- menu */
    function initMenu() {
        const toggle = $('#menu-toggle');
        const menu = $('#site-menu');
        if (!toggle || !menu) return;

        $$('.menu-group, .menu-aside', menu).forEach((element, index) => element.style.setProperty('--i', index));

        const setOrigin = () => {
            const rect = toggle.getBoundingClientRect();
            menu.style.setProperty('--cx', `${rect.left + rect.width / 2}px`);
            menu.style.setProperty('--cy', `${rect.top + rect.height / 2}px`);
        };

        const open = () => {
            setOrigin();
            root.classList.add('menu-open');
            toggle.setAttribute('aria-expanded', 'true');
            menu.setAttribute('aria-hidden', 'false');
            menu.removeAttribute('inert');
            const firstLink = $('a', menu);
            if (firstLink) window.setTimeout(() => firstLink.focus({ preventScroll: true }), 450);
        };

        const close = () => {
            root.classList.remove('menu-open');
            toggle.setAttribute('aria-expanded', 'false');
            menu.setAttribute('aria-hidden', 'true');
            menu.setAttribute('inert', '');
        };

        toggle.addEventListener('click', () => (root.classList.contains('menu-open') ? close() : open()));
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && root.classList.contains('menu-open')) {
                close();
                toggle.focus();
            }
        });
        menu.addEventListener('click', (event) => {
            if (event.target.closest('a[href^="#"]')) close();
        });

        // Live clock and capital weather for Nova Aurelia (America/Havana).
        const clock = $('[data-capital-clock]', menu);
        const weatherEl = $('[data-capital-weather]', menu);
        if (clock) {
            const isHu = root.lang === 'hu';
            const format = new Intl.DateTimeFormat(isHu ? 'hu-HU' : 'en-GB', {
                hour: '2-digit',
                minute: '2-digit',
                timeZone: 'America/Havana'
            });
            const hourFormat = new Intl.DateTimeFormat('en-US', {
                hour: 'numeric',
                hour12: false,
                timeZone: 'America/Havana'
            });

            const updateClockAndWeather = () => {
                const now = new Date();
                clock.textContent = format.format(now);
                if (weatherEl) {
                    const localHour = parseInt(hourFormat.format(now), 10);
                    const isNight = localHour >= 20 || localHour < 6;
                    const icon = isNight ? '🌙' : '☀️';
                    const temp = isNight ? '24°C' : '28°C';
                    const desc = isNight ? (isHu ? 'Tiszta éjszaka' : 'Clear night') : (isHu ? 'Napos' : 'Sunny');
                    weatherEl.innerHTML = `<span class="weather-icon" aria-hidden="true">${icon}</span> <span class="weather-temp">${temp}</span> <span class="weather-desc">${desc}</span>`;
                }
            };
            updateClockAndWeather();
            window.setInterval(updateClockAndWeather, 15000);
        }
    }

    /* --------------------------------------------------------------- reveal */
    /** Wrap each word of an element in masking spans, preserving inline markup. */
    function splitWords(element) {
        if (element.dataset.split === 'done') return;
        let wordIndex = 0;

        const walk = (node) => {
            Array.from(node.childNodes).forEach((child) => {
                if (child.nodeType === Node.TEXT_NODE) {
                    const parts = child.textContent.split(/(\s+)/);
                    if (!child.textContent.trim()) return;
                    const fragment = document.createDocumentFragment();
                    parts.forEach((part) => {
                        if (!part) return;
                        if (/^\s+$/.test(part)) {
                            fragment.appendChild(document.createTextNode(' '));
                            return;
                        }
                        const outer = document.createElement('span');
                        outer.className = 'split-word';
                        const inner = document.createElement('span');
                        inner.textContent = part;
                        inner.style.setProperty('--w', wordIndex++);
                        outer.appendChild(inner);
                        fragment.appendChild(outer);
                    });
                    child.replaceWith(fragment);
                } else if (child.nodeType === Node.ELEMENT_NODE && child.tagName !== 'BR') {
                    walk(child);
                }
            });
        };

        walk(element);
        element.dataset.split = 'done';
    }

    const REVEAL_GROUPS = [
        // [selector, variant]
        ['.section-intro, .narrative-text, .narrative-content > h3, .narrative-content > ol, .narrative-section-title', ''],
        ['.card, .stat-card, .economy-stat, .faq-item, .reference-card, .admin-card, .stat-box, .content-block, .timeline-event, .timeline-period, .timeline-item, .data-viz-container, .data-viz-container-half, .info-stat, .member-card', ''],
        ['.table, .map-container, .video-wrapper, .comparison-item, .faq-section-title, .private-intro, .next-card, .section-link-wrapper, .faq-cta', ''],
        ['.gallery-item, .sight-image', 'image'],
        ['[data-reveal]', null]
    ];

    function initReveal() {
        const targets = new Set();

        REVEAL_GROUPS.forEach(([selector, variant]) => {
            $$(selector).forEach((element) => {
                if (element.closest('.hero, .site-menu, .site-header, .site-footer, .lightbox, #root')) return;
                if (variant !== null && !element.hasAttribute('data-reveal')) element.setAttribute('data-reveal', variant);
                targets.add(element);
            });
        });

        // Section headings reveal word-by-word.
        $$('.section-title, .display, [data-split]').forEach((heading) => {
            if (heading.closest('.hero')) return;
            splitWords(heading);
            heading.setAttribute('data-reveal', 'split');
            targets.add(heading);
        });

        // Stagger siblings that share a parent.
        const counters = new Map();
        targets.forEach((element) => {
            if (element.style.getPropertyValue('--i')) return;
            const parent = element.parentElement;
            const index = counters.get(parent) || 0;
            element.style.setProperty('--i', Math.min(index, 8));
            counters.set(parent, index + 1);
        });

        if (prefersReducedMotion || !isAnimate() || !('IntersectionObserver' in window)) {
            targets.forEach((element) => element.classList.add('is-in'));
        } else {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) return;
                    entry.target.classList.add('is-in');
                    observer.unobserve(entry.target);
                });
            }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
            window._revealObserver = observer;
            targets.forEach((element) => observer.observe(element));
        }

        // Legacy `.fade-in` hooks used by older page scripts.
        $$('.fade-in').forEach((element) => element.classList.add('visible'));

        // Hero headline plays immediately after the curtain lifts.
        const heroTitle = $('.hero .hero-title');
        if (heroTitle) {
            splitWords(heroTitle);
            heroTitle.style.setProperty('--base-delay', prefersReducedMotion ? '0ms' : '650ms');
            requestAnimationFrame(() => requestAnimationFrame(() => heroTitle.classList.add('is-in')));
        }

        root.classList.add('reveal-ready');
    }

    /* ------------------------------------------------------------- counters */
    /** Parse "$41.8T", "8,8M km²", "<1%" into prefix / number / suffix. */
    function parseStat(text) {
        const match = text.match(/^(\D*?)(\d+(?:[.,]\d+)*)(.*)$/s);
        if (!match) return null;
        const [, prefix, raw, suffix] = match;
        const thousands = /^\d{1,3}([.,]\d{3})+$/.test(raw) && !/^\d+[.,]\d{1,2}$/.test(raw);
        let decimals = 0;
        let separator = '.';
        let value;
        if (thousands) {
            value = parseFloat(raw.replace(/[.,]/g, ''));
        } else {
            const decimalMatch = raw.match(/[.,](\d+)$/);
            if (decimalMatch) {
                decimals = decimalMatch[1].length;
                separator = raw.includes(',') ? ',' : '.';
            }
            value = parseFloat(raw.replace(',', '.'));
        }
        if (Number.isNaN(value)) return null;
        return { prefix, suffix, value, decimals, separator, thousands, raw };
    }

    function formatStat(stat, current) {
        let number;
        if (stat.thousands) {
            number = Math.round(current).toLocaleString('en-US').replace(/,/g, stat.raw.includes('.') ? '.' : ',');
        } else {
            number = current.toFixed(stat.decimals).replace('.', stat.separator);
        }
        return `${stat.prefix}${number}${stat.suffix}`;
    }

    function initCounters() {
        const elements = $$('.stat-number, .economy-number, .stat-big, .stat-value, [data-count]');
        if (!elements.length) return;

        const animate = (element) => {
            const original = element.dataset.countText || element.textContent.trim();
            element.dataset.countText = original;
            const stat = parseStat(original);
            if (!stat || prefersReducedMotion) return;
            if (/^\d{4}$/.test(stat.raw) && !stat.prefix) return; // leave years alone

            const duration = 1800 + Math.min(stat.value, 400) * 2;
            const start = performance.now();
            const step = (now) => {
                const progress = Math.min((now - start) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 4);
                element.textContent = formatStat(stat, stat.value * eased);
                if (progress < 1) requestAnimationFrame(step);
                else element.textContent = original;
            };
            requestAnimationFrame(step);
        };

        if (!('IntersectionObserver' in window)) return;
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                const inHero = entry.target.closest('.hero');
                window.setTimeout(() => animate(entry.target), inHero ? 1300 : 150);
                observer.unobserve(entry.target);
            });
        }, { threshold: 0.4 });
        elements.forEach((element) => observer.observe(element));
    }

    /* ------------------------------------------------------------- parallax */
    function initParallax() {
        if (prefersReducedMotion) return;
        const heroMedia = $('.hero .hero-media');
        const layers = $$('[data-parallax]');
        if (!heroMedia && !layers.length) return;

        const update = () => {
            const y = window.scrollY;
            const vh = window.innerHeight;
            if (heroMedia && y < vh * 1.2) {
                heroMedia.style.setProperty('--hero-shift', `${y * 0.28}px`);
            }
            layers.forEach((layer) => {
                const rect = layer.getBoundingClientRect();
                if (rect.bottom < -200 || rect.top > vh + 200) return;
                const speed = parseFloat(layer.dataset.parallax) || 0.15;
                const offset = (rect.top + rect.height / 2 - vh / 2) * -speed;
                layer.style.transform = `translate3d(0, ${offset.toFixed(1)}px, 0)`;
            });
        };

        update();
        window.addEventListener('scroll', rafThrottle(update), { passive: true });
        window.addEventListener('resize', rafThrottle(update));
    }

    /* -------------------------------------------------------------- pointer */
    function initPointerEffects() {
        if (!finePointer || prefersReducedMotion) return;

        // Spotlight that follows the cursor across cards.
        document.addEventListener('pointermove', rafThrottle((event) => {
            const card = event.target.closest && event.target.closest('.card, .stat-card, .tile, .province-card');
            if (!card) return;
            const rect = card.getBoundingClientRect();
            card.style.setProperty('--mx', `${event.clientX - rect.left}px`);
            card.style.setProperty('--my', `${event.clientY - rect.top}px`);
        }), { passive: true });
    }

    /* ----------------------------------------------------------------- rail */
    function initSectionRail() {
        const sections = $$('main > section[id]').filter((section) => $('.section-title, h2', section));
        if (sections.length < 3) return;

        const rail = document.createElement('nav');
        rail.className = 'section-rail';
        rail.setAttribute('aria-label', root.lang === 'hu' ? 'Fejezetek' : 'Sections');

        const links = sections.map((section) => {
            const heading = $('.section-title, h2', section);
            const label = (heading.dataset.label || heading.textContent).replace(/\s+/g, ' ').trim();
            const link = document.createElement('a');
            link.href = `#${section.id}`;
            link.innerHTML = '<span class="rail-label"></span><span class="rail-dot"></span>';
            link.querySelector('.rail-label').textContent = label.length > 42 ? `${label.slice(0, 40)}…` : label;
            link.setAttribute('aria-label', label);
            rail.appendChild(link);
            return link;
        });
        document.body.appendChild(rail);

        const hero = $('main > .hero');
        const setActive = rafThrottle(() => {
            const marker = window.innerHeight * 0.35;
            let activeIndex = -1;
            sections.forEach((section, index) => {
                if (section.getBoundingClientRect().top <= marker) activeIndex = index;
            });
            links.forEach((link, index) => link.classList.toggle('is-active', index === activeIndex));
            const pastHero = hero ? hero.getBoundingClientRect().bottom < window.innerHeight * 0.5 : window.scrollY > 200;
            const footer = $('.site-footer');
            const beforeFooter = footer ? footer.getBoundingClientRect().top > window.innerHeight * 0.6 : true;
            rail.classList.toggle('is-visible', pastHero && beforeFooter);
        });

        setActive();
        window.addEventListener('scroll', setActive, { passive: true });
    }

    /* ------------------------------------------------------------- progress */
    function initProgress() {
        const bar = $('.scroll-progress');
        const toTop = $('.to-top');

        if (toTop) {
            toTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: prefersReducedMotion ? 'auto' : 'smooth' }));
        }

        $$('.hero-scroll').forEach((button) => {
            button.addEventListener('click', () => {
                const hero = button.closest('.hero');
                const next = hero && hero.nextElementSibling;
                if (next) next.scrollIntoView({ behavior: prefersReducedMotion ? 'auto' : 'smooth' });
            });
        });

        const update = () => {
            const max = document.documentElement.scrollHeight - window.innerHeight;
            const progress = max > 0 ? Math.min(window.scrollY / max, 1) : 0;
            if (bar) bar.style.setProperty('--progress', progress.toFixed(4));
            if (toTop) {
                toTop.style.setProperty('--progress', progress.toFixed(4));
                toTop.classList.toggle('is-visible', window.scrollY > 700);
            }
        };

        update();
        window.addEventListener('scroll', rafThrottle(update), { passive: true });
        window.addEventListener('resize', rafThrottle(update));
    }

    /* ------------------------------------------------------------- timeline */
    function initTimelines() {
        const timelines = $$('.timeline, .timeline-container, .timeline-expanded');
        if (!timelines.length) return;

        const update = () => {
            const vh = window.innerHeight;
            timelines.forEach((timeline) => {
                const rect = timeline.getBoundingClientRect();
                const progress = Math.min(Math.max((vh * 0.65 - rect.top) / rect.height, 0), 1);
                timeline.style.setProperty('--line-progress', progress.toFixed(4));
            });
        };

        update();
        window.addEventListener('scroll', rafThrottle(update), { passive: true });
    }

    /* -------------------------------------------------------------- marquee */
    function initMarquees() {
        $$('.marquee-track').forEach((track) => {
            if (track.dataset.cloned) return;
            Array.from(track.children).forEach((item) => {
                const clone = item.cloneNode(true);
                clone.setAttribute('aria-hidden', 'true');
                track.appendChild(clone);
            });
            track.dataset.cloned = 'true';
        });
    }

    /* ----------------------------------------------------------------- boot */
    function init() {
        initTheme();
        initAnimate();
        initCurtain();
        initHeader();
        initMenu();
        initMarquees();
        initReveal();
        initCounters();
        initParallax();
        initPointerEffects();
        initSectionRail();
        initProgress();
        initTimelines();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
