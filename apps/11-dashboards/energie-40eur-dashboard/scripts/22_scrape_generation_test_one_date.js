/**
 * Quick test: Scrape Generation for ONE date only
 */

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

async function main() {
    const testDate = '2024-06-15';
    const outputFile = path.join(__dirname, '..', 'data', 'raw', `entsoe_generation_test.jsonl`);

    console.log(`Testing scraping for ${testDate}...\n`);

    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    const url = `https://newtransparency.entsoe.eu/generation/actual/perType/generation?appState=%7B%22sa%22%3A%5B%22CTY%7C10YFR-RTE------C%22%5D%2C%22st%22%3A%22CTY%22%2C%22mm%22%3Afalse%2C%22ma%22%3Afalse%2C%22dt%22%3A%22TABLE%22%2C%22df%22%3A%5B%22${testDate}%22%2C%22${testDate}%22%5D%2C%22tz%22%3A%22CET%22%7D`;

    await page.goto(url, { timeout: 30000 });
    await page.waitForTimeout(10000); // Wait for data to load

    const data = await page.evaluate((date) => {
        const rows = document.querySelectorAll('table tbody tr');
        const results = [];

        // Hardcoded header names based on ENTSO-E Generation page
        const headerNames = [
            'Biomass',
            'Energy storage',
            'Fossil Brown coal/Lignite',
            'Fossil Coal-derived gas',
            'Fossil Gas',
            'Fossil Hard coal',
            'Fossil Oil',
            'Fossil Oil shale',
            'Fossil Peat',
            'Geothermal',
            'Hydro Pumped Storage',
            'Hydro Run-of-river and poundage',
            'Hydro Water Reservoir',
            'Marine',
            'Nuclear',
            'Other',
            'Other renewable',
            'Solar',
            'Waste',
            'Wind Offshore',
            'Wind Onshore'
        ];

        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 2) { // At least time + 1 production type
                const timeRange = cells[0]?.textContent?.trim();

                if (timeRange && timeRange.includes(' - ')) {
                    const record = {
                        date: date,
                        timeRange: timeRange,
                        generation: {}
                    };

                    // Parse all columns (skip first which is time)
                    for (let i = 1; i < cells.length && i <= headerNames.length; i++) {
                        const value = cells[i]?.textContent?.trim();
                        const headerName = headerNames[i - 1] || `col_${i}`;

                        // Handle n/e (not available) and convert to number
                        if (value && value !== 'n/e' && value !== '') {
                            record.generation[headerName] = parseFloat(value.replace(/,/g, '') || '0');
                        } else {
                            record.generation[headerName] = null;
                        }
                    }

                    results.push(record);
                }
            }
        });
        return results;
    }, testDate);

    console.log(`Extracted ${data.length} hour records`);

    if (data && data.length > 0) {
        // Write to file
        const stream = fs.createWriteStream(outputFile);
        for (const record of data) {
            stream.write(JSON.stringify(record) + '\n');
        }
        stream.end();

        console.log(`\nSUCCESS! Wrote ${data.length} records to ${outputFile}`);
        console.log(`\nSample record:`);
        console.log(JSON.stringify(data[0], null, 2));
    } else {
        console.log('ERROR: No data extracted');
    }

    await browser.close();
}

main().catch(console.error);
