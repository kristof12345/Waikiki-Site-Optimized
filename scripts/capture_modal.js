const { chromium } = require('/usr/local/lib/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const siteDir = __dirname ? path.resolve(__dirname, '..') : process.cwd();
const outDir = '/Users/kristof/.gemini/antigravity/brain/88e7f69e-8078-4b5a-ada9-4d6651db16ae';

const mimeTypes = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.svg': 'image/svg+xml',
    '.jpg': 'image/jpeg',
    '.png': 'image/png',
    '.woff2': 'font/woff2',
    '.woff': 'font/woff',
};

const server = http.createServer((req, res) => {
    let filePath = path.join(siteDir, decodeURIComponent(req.url.split('?')[0]));
    if (filePath.endsWith('/')) filePath += 'index.html';
    
    fs.readFile(filePath, (err, data) => {
        if (err) {
            res.writeHead(404);
            res.end('Not Found: ' + req.url);
            return;
        }
        const ext = path.extname(filePath).toLowerCase();
        res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'application/octet-stream' });
        res.end(data);
    });
});

server.listen(8099, async () => {
    console.log('Server started on port 8099');
    try {
        const browser = await chromium.launch({ headless: true });
        const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });

        page.on('console', msg => console.log('PAGE LOG:', msg.text()));
        page.on('pageerror', err => console.log('PAGE ERROR:', err.message));

        await page.goto('http://localhost:8099/en/citizenship.html');
        await page.waitForLoadState('networkidle');

        // Wait for open assessment button
        await page.waitForSelector('.open-assessment');
        await page.click('.open-assessment');
        await page.waitForSelector('.assessment-modal');

        // 1. INTRO - Light mode
        await page.screenshot({ path: path.join(outDir, 'modal-intro-light.png') });
        console.log('Saved modal-intro-light.png');

        // 1b. INTRO - Dark mode
        await page.evaluate(() => document.documentElement.classList.add('body-dark'));
        await page.screenshot({ path: path.join(outDir, 'modal-intro-dark.png') });
        console.log('Saved modal-intro-dark.png');

        // Reset to light mode for quiz
        await page.evaluate(() => document.documentElement.classList.remove('body-dark'));

        // 2. QUIZ - Click "Begin Assessment"
        await page.click('button:has-text("Begin Assessment")');
        await page.waitForTimeout(300);

        // Light mode quiz
        await page.screenshot({ path: path.join(outDir, 'modal-quiz-light.png') });
        console.log('Saved modal-quiz-light.png');

        // Dark mode quiz
        await page.evaluate(() => document.documentElement.classList.add('body-dark'));
        await page.waitForTimeout(350);
        const btnInfo = await page.locator('.assessment-modal-body button').first().evaluate(el => {
            const cs = window.getComputedStyle(el);
            const span = el.querySelector('span');
            const spanCs = span ? window.getComputedStyle(span) : null;
            return {
                tag: el.tagName,
                className: el.className,
                bg: cs.backgroundColor,
                color: cs.color,
                border: cs.border,
                spanColor: spanCs ? spanCs.color : null,
                matchesBodyDark: document.documentElement.matches('.body-dark'),
                matchesGroup: el.matches('.group'),
                matchesBodyDarkBtn: el.matches('.body-dark .assessment-modal-body button.group')
            };
        });
        console.log('BTN DEBUG INFO:', JSON.stringify(btnInfo, null, 2));
        const matchedRules = await page.locator('.assessment-modal-body button').first().evaluate(el => {
            const matched = [];
            for (const sheet of document.styleSheets) {
                try {
                    for (const rule of sheet.cssRules) {
                        if (rule.selectorText && el.matches(rule.selectorText)) {
                            matched.push(rule.cssText);
                        }
                    }
                } catch (e) {}
            }
            return matched;
        });
        console.log('MATCHED RULES CSSTEXT:', matchedRules);
        await page.screenshot({ path: path.join(outDir, 'modal-quiz-dark.png') });
        console.log('Saved modal-quiz-dark.png');

        // Hover state on option in dark mode
        const firstOption = page.locator('.assessment-modal-body button').first();
        await firstOption.hover();
        await page.screenshot({ path: path.join(outDir, 'modal-quiz-dark-hover.png') });

        // Answer questions to get to result
        await page.evaluate(() => document.documentElement.classList.remove('body-dark'));
        for (let i = 0; i < 25; i++) {
            const option = page.locator('.assessment-modal-body button').first();
            if (await option.count() > 0) {
                const text = await option.innerText();
                if (text.includes('Begin Assessment') || text.includes('Official Application') || text.includes('Close') || text.includes('Start Investment')) break;
                await option.click();
                await page.waitForTimeout(50);
            } else {
                break;
            }
        }

        // Wait for analyzing
        await page.waitForTimeout(400);
        await page.screenshot({ path: path.join(outDir, 'modal-analyzing-light.png') });
        await page.evaluate(() => document.documentElement.classList.add('body-dark'));
        await page.screenshot({ path: path.join(outDir, 'modal-analyzing-dark.png') });

        // Wait for result stage (3s timer)
        await page.evaluate(() => document.documentElement.classList.remove('body-dark'));
        await page.waitForTimeout(3500);
        await page.screenshot({ path: path.join(outDir, 'modal-result-light.png') });
        console.log('Saved modal-result-light.png');

        // Dark mode result
        await page.evaluate(() => document.documentElement.classList.add('body-dark'));
        await page.screenshot({ path: path.join(outDir, 'modal-result-dark.png') });
        console.log('Saved modal-result-dark.png');

        await browser.close();
    } catch (e) {
        console.error('Test error:', e);
    } finally {
        server.close();
        console.log('Done!');
        process.exit(0);
    }
});
