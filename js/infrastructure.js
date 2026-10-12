/* Infrastructure page: artificial island tabs and interactive map hotspots */
(() => {
    const isHu = (document.documentElement.lang || '').toLowerCase().startsWith('hu');
    const i18n = {
        close: isHu ? 'Bezárás' : 'Close',
        details: isHu ? 'Részletek' : 'Details'
    };
    function initTabs() {
        const tabButtons = Array.from(document.querySelectorAll('.island-tab-btn'));
        const tabPanels = document.querySelectorAll('.island-panel');
        if (!tabButtons.length) return;
        const activate = btn => {
            const island = btn.getAttribute('data-island-tab');
            tabButtons.forEach(b => {
                const on = b === btn;
                b.classList.toggle('is-active', on);
                b.setAttribute('aria-selected', on ? 'true' : 'false');
                b.setAttribute('tabindex', on ? '0' : '-1');
            });
            tabPanels.forEach(panel => {
                panel.classList.toggle('is-active', panel.id === `tab-panel-${island}`);
            });
            document.dispatchEvent(new CustomEvent('island:tabchange'));
        };
        tabButtons.forEach(btn => {
            btn.setAttribute('tabindex', btn.classList.contains('is-active') ? '0' : '-1');
            btn.addEventListener('click', () => activate(btn));
        });
        const tabList = document.querySelector('.island-tabs-bar');
        if (tabList) {
            tabList.addEventListener('keydown', e => {
                const index = tabButtons.indexOf(document.activeElement);
                if (index === -1) return;
                let next = null;
                if (e.key === 'ArrowRight') next = (index + 1) % tabButtons.length;
                else if (e.key === 'ArrowLeft') next = (index - 1 + tabButtons.length) % tabButtons.length;
                else if (e.key === 'Home') next = 0;
                else if (e.key === 'End') next = tabButtons.length - 1;
                if (next !== null) {
                    e.preventDefault();
                    tabButtons[next].focus();
                    activate(tabButtons[next]);
                }
            });
        }
    }
    function initHotspots(panel) {
        const canvas = panel.querySelector('.island-map-canvas');
        const hotspots = Array.from(panel.querySelectorAll('.map-hotspot'));
        const cards = Array.from(panel.querySelectorAll('.island-hotspot-card'));
        if (!canvas || !hotspots.length) return;
        const cardFor = id => panel.querySelector(`.island-hotspot-card[data-spot="${id}"]`);
        const spotFor = id => panel.querySelector(`.map-hotspot[data-spot="${id}"]`);
        // Tooltip overlay
        const tip = document.createElement('div');
        tip.className = 'map-tooltip';
        tip.id = `${panel.id}-tooltip`;
        tip.setAttribute('role', 'tooltip');
        tip.hidden = true;
        tip.innerHTML = `
            <div class="map-tooltip-top">
                <span class="map-tooltip-badge"></span>
                <button type="button" class="map-tooltip-close" aria-label="${i18n.close}">×</button>
            </div>
            <h4 class="map-tooltip-title"></h4>
            <p class="map-tooltip-text"></p>
            <button type="button" class="map-tooltip-more">${i18n.details} <span aria-hidden="true">↓</span></button>`;
        canvas.appendChild(tip);
        const els = {
            badge: tip.querySelector('.map-tooltip-badge'),
            title: tip.querySelector('.map-tooltip-title'),
            text: tip.querySelector('.map-tooltip-text'),
            close: tip.querySelector('.map-tooltip-close'),
            more: tip.querySelector('.map-tooltip-more')
        };
        let current = null;
        let pinned = false;
        let hideTimer = null;
        // Make each SVG pin a real, focusable button
        hotspots.forEach(spot => {
            const id = spot.getAttribute('data-spot');
            const card = cardFor(id);
            const title = card ? card.querySelector('h4').textContent.trim() : id;
            spot.setAttribute('tabindex', '0');
            spot.setAttribute('role', 'button');
            spot.setAttribute('aria-label', `${id}. ${title}`);
            spot.setAttribute('aria-controls', tip.id);
            spot.setAttribute('aria-expanded', 'false');
            spot.setAttribute('focusable', 'true');
        });
        const setActive = id => {
            hotspots.forEach(s => {
                const on = s.getAttribute('data-spot') === id;
                s.classList.toggle('is-highlighted', on);
                s.setAttribute('aria-expanded', on && !tip.hidden ? 'true' : 'false');
            });
            cards.forEach(c => c.classList.toggle('is-active', c.getAttribute('data-spot') === id));
        };
        const position = spot => {
            const core = spot.querySelector('.hotspot-core') || spot;
            const c = canvas.getBoundingClientRect();
            const r = core.getBoundingClientRect();
            const x = r.left + r.width / 2 - c.left;
            const top = r.top - c.top;
            const bottom = r.bottom - c.top;
            const gap = 12;
            const pad = 10;
            const tw = tip.offsetWidth;
            const th = tip.offsetHeight;
            const left = Math.max(pad, Math.min(x - tw / 2, c.width - tw - pad));
            let below = top - th - gap < pad;
            if (below && bottom + th + gap > c.height - pad && top > c.height - bottom) below = false;
            let y = below ? bottom + gap : top - th - gap;
            y = Math.max(pad, Math.min(y, c.height - th - pad));
            tip.style.left = `${left}px`;
            tip.style.top = `${y}px`;
            tip.style.setProperty('--arrow-x', `${Math.max(14, Math.min(x - left, tw - 14))}px`);
            tip.classList.toggle('is-below', below);
        };
        const show = (spot, pin = false) => {
            clearTimeout(hideTimer);
            const id = spot.getAttribute('data-spot');
            const card = cardFor(id);
            if (!card) return;
            els.badge.textContent = id;
            els.title.textContent = card.querySelector('h4').textContent.trim();
            els.text.textContent = card.querySelector('p').textContent.trim();
            current = spot;
            pinned = pin || pinned;
            tip.classList.toggle('is-pinned', pinned);
            tip.hidden = false;
            tip.classList.remove('is-visible');
            position(spot);
            requestAnimationFrame(() => tip.classList.add('is-visible'));
            setActive(id);
        };
        const hide = (force = false) => {
            if (pinned && !force) return;
            pinned = false;
            tip.classList.remove('is-visible', 'is-pinned');
            tip.hidden = true;
            current = null;
            setActive(null);
        };
        const scheduleHide = () => {
            clearTimeout(hideTimer);
            hideTimer = setTimeout(() => hide(), 140);
        };
        hotspots.forEach(spot => {
            spot.addEventListener('pointerenter', e => {
                if (e.pointerType === 'mouse' && !pinned) show(spot);
            });
            spot.addEventListener('pointerleave', e => {
                if (e.pointerType === 'mouse') scheduleHide();
            });
            spot.addEventListener('focus', () => show(spot));
            spot.addEventListener('blur', e => {
                if (!tip.contains(e.relatedTarget)) scheduleHide();
            });
            spot.addEventListener('click', e => {
                e.stopPropagation();
                if (pinned && current === spot) {
                    hide(true);
                    return;
                }
                pinned = false;
                show(spot, true);
            });
            spot.addEventListener('keydown', e => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    spot.click();
                } else if (e.key === 'Escape') {
                    hide(true);
                }
            });
        });
        tip.addEventListener('pointerenter', () => clearTimeout(hideTimer));
        tip.addEventListener('pointerleave', e => {
            if (e.pointerType === 'mouse') scheduleHide();
        });
        tip.addEventListener('click', e => e.stopPropagation());
        els.close.addEventListener('click', () => {
            const spot = current;
            hide(true);
            if (spot) spot.focus({ preventScroll: true });
        });
        els.more.addEventListener('click', () => {
            const id = current && current.getAttribute('data-spot');
            const card = id && cardFor(id);
            hide(true);
            if (card) {
                card.scrollIntoView({ behavior: 'smooth', block: 'center' });
                setActive(id);
            }
        });
        document.addEventListener('click', e => {
            if (!tip.hidden && !canvas.contains(e.target)) hide(true);
        });
        document.addEventListener('keydown', e => {
            if (e.key === 'Escape' && !tip.hidden) hide(true);
        });
        document.addEventListener('island:tabchange', () => hide(true));
        window.addEventListener('resize', () => {
            if (current && !tip.hidden) position(current);
        });
        // Cards highlight their pin on hover, and open the tooltip on click
        cards.forEach(card => {
            const id = card.getAttribute('data-spot');
            card.addEventListener('mouseenter', () => {
                if (!pinned) hotspots.forEach(s => s.classList.toggle('is-highlighted', s.getAttribute('data-spot') === id));
            });
            card.addEventListener('mouseleave', () => {
                if (!pinned) hotspots.forEach(s => s.classList.remove('is-highlighted'));
            });
            card.addEventListener('click', () => {
                const spot = spotFor(id);
                if (!spot) return;
                canvas.scrollIntoView({ behavior: 'smooth', block: 'center' });
                pinned = false;
                show(spot, true);
            });
        });
    }
    function init() {
        initTabs();
        document.querySelectorAll('.island-panel').forEach(initHotspots);
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();
