/* Sovereign Nation of Waikiki — Nature and Sanctuaries Interactive Engine */
(() => {
    'use strict';

    function initBiomeExplorer() {
        const tabBtns = Array.from(document.querySelectorAll('.biome-tab-btn'));
        const infoCards = Array.from(document.querySelectorAll('.biome-info-card'));
        const mapNodes = Array.from(document.querySelectorAll('.map-zone-node'));

        if (!tabBtns.length) return;

        function activateBiome(zoneId) {
            tabBtns.forEach(btn => {
                const isActive = btn.getAttribute('data-biome-target') === zoneId;
                btn.classList.toggle('is-active', isActive);
                btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
            });

            infoCards.forEach(card => {
                const isActive = card.getAttribute('data-biome-card') === zoneId;
                card.classList.toggle('is-active', isActive);
            });

            mapNodes.forEach(node => {
                const isActive = node.getAttribute('data-map-zone') === zoneId;
                node.classList.toggle('is-active', isActive);
            });
        }

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const zoneId = btn.getAttribute('data-biome-target');
                if (zoneId) activateBiome(zoneId);
            });
        });

        mapNodes.forEach(node => {
            node.addEventListener('click', () => {
                const zoneId = node.getAttribute('data-map-zone');
                if (zoneId) activateBiome(zoneId);
            });
        });
    }

    function initCanopyInspector() {
        const strataTiers = Array.from(document.querySelectorAll('.strata-tier'));
        const layerCards = Array.from(document.querySelectorAll('.canopy-layer-card'));

        if (!layerCards.length) return;

        function highlightStratum(tierId) {
            strataTiers.forEach(tier => {
                const matches = tier.getAttribute('data-strata') === tierId;
                tier.classList.toggle('is-highlighted', matches);
                if (tierId) {
                    tier.style.opacity = matches ? '1' : '0.35';
                } else {
                    tier.style.opacity = '1';
                }
            });

            layerCards.forEach(card => {
                const matches = card.getAttribute('data-layer') === tierId;
                card.classList.toggle('is-active', matches);
            });
        }

        layerCards.forEach(card => {
            const tierId = card.getAttribute('data-layer');

            card.addEventListener('mouseenter', () => highlightStratum(tierId));
            card.addEventListener('mouseleave', () => highlightStratum(null));
            card.addEventListener('click', () => highlightStratum(tierId));
        });

        strataTiers.forEach(tier => {
            const tierId = tier.getAttribute('data-strata');

            tier.addEventListener('mouseenter', () => highlightStratum(tierId));
            tier.addEventListener('mouseleave', () => highlightStratum(null));
            tier.addEventListener('click', () => highlightStratum(tierId));
        });
    }

    function initSanctuaryFilter() {
        const filterBtns = Array.from(document.querySelectorAll('.sanctuary-filter-btn'));
        const cards = Array.from(document.querySelectorAll('.sanctuary-card'));

        if (!filterBtns.length || !cards.length) return;

        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => {
                    const active = b === btn;
                    b.classList.toggle('is-active', active);
                    b.setAttribute('aria-pressed', active ? 'true' : 'false');
                });

                const cat = btn.getAttribute('data-filter') || 'all';

                cards.forEach(card => {
                    const cardCat = card.getAttribute('data-cat');
                    const show = cat === 'all' || cardCat === cat;

                    card.style.display = show ? 'flex' : 'none';
                    if (show) {
                        card.style.animation = 'fadeInCard 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards';
                    }
                });
            });
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        initBiomeExplorer();
        initCanopyInspector();
        initSanctuaryFilter();
    });
})();
