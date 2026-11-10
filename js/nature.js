/* Waikiki Nature and Sanctuaries Interactive Engine */
(() => {
    'use strict';

    function initProvinceFilter() {
        const filterBtns = Array.from(document.querySelectorAll('.province-btn'));
        const cards = Array.from(document.querySelectorAll('.sanctuary-item'));

        if (!filterBtns.length || !cards.length) return;

        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const prov = btn.getAttribute('data-prov-filter') || 'all';

                filterBtns.forEach(b => {
                    const active = b === btn;
                    b.classList.toggle('is-active', active);
                    b.setAttribute('aria-pressed', active ? 'true' : 'false');
                });

                let visibleIdx = 0;
                cards.forEach(card => {
                    const cardProv = card.getAttribute('data-prov');
                    const show = prov === 'all' || cardProv === prov;

                    if (show) {
                        card.style.display = 'flex';
                        card.style.opacity = '0';
                        card.style.transform = 'translateY(14px)';
                        const delay = visibleIdx * 45;
                        visibleIdx++;

                        window.setTimeout(() => {
                            requestAnimationFrame(() => {
                                card.style.transition = 'opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1), transform 0.35s cubic-bezier(0.16, 1, 0.3, 1)';
                                card.style.opacity = '1';
                                card.style.transform = 'translateY(0)';
                                window.setTimeout(() => {
                                    card.style.transition = '';
                                    card.style.transform = '';
                                    card.style.opacity = '';
                                }, 360);
                            });
                        }, delay);
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        initProvinceFilter();
    });
})();
