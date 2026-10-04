#!/usr/bin/env node
/**
 * Format document and remove all empty lines in document.
 * 
 * Usage:
 *   node scripts/format_document.js [files...]
 *   node scripts/format_document.js --all
 *   cat file.html | node scripts/format_document.js -
 */
const fs = require('fs');
const path = require('path');
const beautify = require('js-beautify').html;

const BEAUTIFY_OPTIONS = {
    indent_size: 4,
    indent_char: ' ',
    max_preserve_newlines: 0,
    preserve_newlines: false,
    extra_liners: [],
    end_with_newline: true,
    wrap_line_length: 0,
    indent_inner_html: false
};

function formatAndRemoveEmptyLines(htmlContent) {
    // 1. Format document
    const formatted = beautify(htmlContent, BEAUTIFY_OPTIONS);

    // 2. Remove empty lines in document
    const lines = formatted.split(/\r?\n/).filter(line => line.trim().length > 0);
    return lines.join('\n') + '\n';
}

function getAllHtmlFiles(dir) {
    let results = [];
    const list = fs.readdirSync(dir, { withFileTypes: true });
    for (const dirent of list) {
        if (dirent.name === 'node_modules' || dirent.name === '.git') continue;
        const fullPath = path.join(dir, dirent.name);
        if (dirent.isDirectory()) {
            results = results.concat(getAllHtmlFiles(fullPath));
        } else if (dirent.isFile() && dirent.name.endsWith('.html')) {
            results.push(fullPath);
        }
    }
    return results;
}

function processFile(filePath) {
    try {
        const original = fs.readFileSync(filePath, 'utf8');
        const processed = formatAndRemoveEmptyLines(original);
        if (original !== processed) {
            fs.writeFileSync(filePath, processed, 'utf8');
            console.log(`Formatted & cleaned: ${path.relative(process.cwd(), filePath)}`);
            return true;
        }
    } catch (err) {
        console.error(`Error processing ${filePath}:`, err.message);
    }
    return false;
}

function main() {
    const args = process.argv.slice(2);
    if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
        console.log('Usage:');
        console.log('  node scripts/format_document.js <file1.html> [file2.html ...]');
        console.log('  node scripts/format_document.js --all');
        console.log('  cat index.html | node scripts/format_document.js -');
        process.exit(0);
    }

    if (args[0] === '-') {
        // Read from stdin, output to stdout
        let input = '';
        process.stdin.setEncoding('utf8');
        process.stdin.on('data', chunk => { input += chunk; });
        process.stdin.on('end', () => {
            process.stdout.write(formatAndRemoveEmptyLines(input));
        });
        return;
    }

    let files = [];
    if (args.includes('--all')) {
        const root = process.cwd();
        files = getAllHtmlFiles(path.join(root, 'en'))
            .concat(getAllHtmlFiles(path.join(root, 'hu')));
        const rootIndex = path.join(root, 'index.html');
        if (fs.existsSync(rootIndex)) files.push(rootIndex);
    } else {
        files = args.map(f => path.resolve(f));
    }

    let changed = 0;
    for (const file of files) {
        if (processFile(file)) changed++;
    }
    console.log(`Done. Processed ${files.length} file(s), updated ${changed}.`);
}

if (require.main === module) {
    main();
}

module.exports = {
    formatAndRemoveEmptyLines,
    processFile
};
