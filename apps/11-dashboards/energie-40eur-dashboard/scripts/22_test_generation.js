/**
 * Test script to explore ENTSO-E Generation page structure
 */

const { chromium } = require('playwright');

async function test() {
    const browser = await chromium.launch({ headless: false }); // visible pour debug
    const page = await browser.newPage();

    const testDate = '2024-06-15'; // Date de test (été = solaire élevé)

    console.log(`Testing Generation scraping for ${testDate}...\n`);

    const url = `https://newtransparency.entsoe.eu/generation/actual/perType/generation?appState=%7B%22sa%22%3A%5B%22CTY%7C10YFR-RTE------C%22%5D%2C%22st%22%3A%22CTY%22%2C%22mm%22%3Afalse%2C%22ma%22%3Afalse%2C%22dt%22%3A%22TABLE%22%2C%22df%22%3A%5B%22${testDate}%22%2C%22${testDate}%22%5D%2C%22tz%22%3A%22CET%22%7D`;

    await page.goto(url, { timeout: 30000 });
    console.log('Page loaded, waiting 10s for data to render...');
    await page.waitForTimeout(10000);

    // Take a screenshot to debug
    await page.screenshot({ path: 'generation_page_debug.png', fullPage: true });
    console.log('Screenshot saved as generation_page_debug.png');

    // First, let's find what tables exist
    const tableInfo = await page.evaluate(() => {
        const tables = document.querySelectorAll('table');
        return {
            count: tables.length,
            info: Array.from(tables).map((table, i) => ({
                index: i,
                rows: table.querySelectorAll('tr').length,
                hasThead: table.querySelector('thead') !== null,
                hasTbody: table.querySelector('tbody') !== null
            }))
        };
    });

    console.log('TABLES FOUND:');
    console.log(JSON.stringify(tableInfo, null, 2));
    console.log('');

    // Try different selectors
    const headers = await page.evaluate(() => {
        // Try multiple selector strategies
        const strategies = [
            'table thead tr th',
            'table th',
            '.table thead tr th',
            '[class*="table"] th',
            'thead th'
        ];

        for (const selector of strategies) {
            const headerCells = document.querySelectorAll(selector);
            if (headerCells.length > 0) {
                const headers = [];
                headerCells.forEach(cell => {
                    headers.push(cell.textContent?.trim());
                });
                return { selector, headers };
            }
        }

        return { selector: 'none', headers: [] };
    });

    console.log('TABLE HEADERS:');
    console.log(`Selector used: ${headers.selector}`);
    console.log(JSON.stringify(headers.headers, null, 2));
    console.log('');

    // Extract first 3 rows of data
    const sampleData = await page.evaluate(() => {
        const rows = document.querySelectorAll('table tbody tr');
        const samples = [];

        for (let r = 0; r < Math.min(3, rows.length); r++) {
            const row = rows[r];
            const cells = row.querySelectorAll('td');
            const rowData = [];

            cells.forEach(cell => {
                rowData.push(cell.textContent?.trim());
            });

            samples.push(rowData);
        }

        return samples;
    });

    console.log('SAMPLE DATA (first 3 rows):');
    sampleData.forEach((row, i) => {
        console.log(`Row ${i+1}:`, JSON.stringify(row, null, 2));
    });
    console.log('');

    // Map headers to data
    console.log('MAPPED SAMPLE:');
    sampleData.forEach((row, i) => {
        console.log(`\nHour ${i+1}:`);
        headers.forEach((header, j) => {
            if (j < row.length) {
                console.log(`  ${header}: ${row[j]}`);
            }
        });
    });

    await page.waitForTimeout(5000); // Keep browser open to inspect
    await browser.close();
}

test().catch(console.error);
