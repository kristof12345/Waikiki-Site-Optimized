/* ==========================================================================
   FEATURE PAGES — Infrastructure & Travel Guide
   Filter chips for landmark and hotel grids.

   Markup:
     <div class="filter-bar" data-filter-for="hotel-grid">
       <button class="filter-chip" data-filter="all" aria-pressed="true">All</button>
       <button class="filter-chip" data-filter="city" aria-pressed="false">City</button>
     </div>
     <div id="hotel-grid"><article data-filter-item data-cat="city islands">…</article></div>
   ========================================================================== */
(function () {
    'use strict';

    function initFilterBar(bar) {
        const grid = document.getElementById(bar.dataset.filterFor);
        if (!grid) return;
        const items = Array.from(grid.querySelectorAll('[data-filter-item]'));
        const chips = Array.from(bar.querySelectorAll('[data-filter]'));

        // Show how many entries each chip reveals.
        chips.forEach((chip) => {
            const key = chip.dataset.filter;
            const total = key === 'all'
                ? items.length
                : items.filter((item) => item.dataset.cat.split(/\s+/).includes(key)).length;
            const count = document.createElement('span');
            count.className = 'count';
            count.textContent = total;
            chip.appendChild(count);
        });

        bar.addEventListener('click', (event) => {
            const chip = event.target.closest('[data-filter]');
            if (!chip || chip.getAttribute('aria-pressed') === 'true') return;
            const key = chip.dataset.filter;

            chips.forEach((other) => other.setAttribute('aria-pressed', String(other === chip)));

            items.forEach((item, index) => {
                const match = key === 'all' || item.dataset.cat.split(/\s+/).includes(key);
                item.classList.remove('is-filtering-in');
                item.hidden = !match;
                if (match) {
                    // Filtered cards must be visible even if the scroll reveal has not fired yet.
                    item.classList.add('is-in');
                    item.style.animationDelay = `${Math.min(index, 8) * 45}ms`;
                    void item.offsetWidth; // restart the entrance animation
                    item.classList.add('is-filtering-in');
                }
            });
        });
    }

    function init() {
        document.querySelectorAll('.filter-bar[data-filter-for]').forEach(initFilterBar);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
