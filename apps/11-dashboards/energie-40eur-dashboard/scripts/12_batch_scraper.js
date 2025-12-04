/**
 * Script 12: Batch ENTSO-E Scraper using Playwright
 * Scrapes all remaining 2024 dates efficiently
 */

const fs = require('fs');
const path = require('path');

// Generate date range
function generateDateRange2024() {
    const dates = [];
    const start = new Date('2024-01-01');
    const end = new Date('2024-12-31');

    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
        dates.push(d.toISOString().split('T')[0]);
    }

    return dates;
}

// Read existing scraped dates
function getExistingDates(filePath) {
    if (!fs.existsSync(filePath)) {
        return new Set();
    }

    const existing = new Set();
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n').filter(l => l.trim());

    for (const line of lines) {
        try {
            const record = JSON.parse(line);
            existing.add(record.date);
        } catch (e) {
            // Skip invalid lines
        }
    }

    return existing;
}

async function main() {
    const { chromium } = require('playwright');

    console.log('='.repeat(80));
    console.log('BATCH ENTSO-E 2024 SCRAPER');
    console.log('='.repeat(80));

    const outputFile = path.join(__dirname, '..', 'data', 'raw', 'entsoe_2024_scraped.jsonl');
    const allDates = generateDateRange2024();
    const existingDates = getExistingDates(outputFile);
    const datesToScrape = allDates.filter(d => !existingDates.has(d));

    console.log(`\nTotal dates: ${allDates.length}`);
    console.log(`Already scraped: ${existingDates.size}`);
    console.log(`Remaining: ${datesToScrape.length}\n`);

    if (datesToScrape.length === 0) {
        console.log('✅ All dates already scraped!');
        return;
    }

    // Launch browser
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    const stream = fs.createWriteStream(outputFile, { flags: 'a' });
    let successCount = 0;
    let errorCount = 0;

    for (let i = 0; i < datesToScrape.length; i++) {
        const dateStr = datesToScrape[i];
        process.stdout.write(`[${i+1}/${datesToScrape.length}] Scraping ${dateStr}... `);

        try {
            const url = `https://newtransparency.entsoe.eu/market/energyPrices?appState=%7B%22sa%22%3A%5B%22BZN%7C10YFR-RTE------C%22%5D%2C%22st%22%3A%22BZN%22%2C%22mm%22%3Afalse%2C%22ma%22%3Afalse%2C%22sp%22%3A%22HALF%22%2C%22dt%22%3A%22TABLE%22%2C%22df%22%3A%22${dateStr}%22%2C%22tz%22%3A%22CET%22%7D`;

            await page.goto(url, { timeout: 30000 });
            await page.waitForTimeout(4000);

            const data = await page.evaluate((date) => {
                const rows = document.querySelectorAll('table tbody tr');
                const results = [];
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 2) {
                        const timeRange = cells[0]?.textContent?.trim();
                        const priceText = cells[1]?.textContent?.trim();
                        if (timeRange && priceText && timeRange.includes('/')) {
                            const price = parseFloat(priceText.replace(/["']/g, ''));
                            results.push({
                                date: date,
                                timeRange: timeRange,
                                price: price
                            });
                        }
                    }
                });
                return results;
            }, dateStr);

            if (data && data.length > 0) {
                for (const record of data) {
                    stream.write(JSON.stringify(record) + '\n');
                }
                const below40 = data.filter(r => r.price <= 40).length;
                console.log(`✓ ${data.length} hours (${below40} ≤40€)`);
                successCount++;
            } else {
                console.log('⚠️  No data');
                errorCount++;
            }

            // Rate limiting
            await page.waitForTimeout(2000);

            // Progress checkpoint
            if ((i + 1) % 50 === 0) {
                console.log(`\n📊 Progress: ${i+1}/${datesToScrape.length} (${((i+1)/datesToScrape.length*100).toFixed(1)}%)`);
                console.log(`   Success: ${successCount}, Errors: ${errorCount}\n`);
            }

        } catch (error) {
            console.log(`❌ Error: ${error.message}`);
            errorCount++;
        }
    }

    stream.end();
    await browser.close();

    console.log('\n' + '='.repeat(80));
    console.log('✅ SCRAPING COMPLETE!');
    console.log('='.repeat(80));
    console.log(`Successfully scraped: ${successCount} dates`);
    console.log(`Errors: ${errorCount} dates`);
    console.log(`Output: ${outputFile}`);
}

main().catch(console.error);
