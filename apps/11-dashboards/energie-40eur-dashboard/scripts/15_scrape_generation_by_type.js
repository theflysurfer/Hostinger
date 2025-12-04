/**
 * Script 15: Scraper for Generation by Production Type
 * Scrapes actual generation data by production type (Wind, Solar, Nuclear, etc.)
 * Usage: node scripts/15_scrape_generation_by_type.js 2024
 */

const fs = require('fs');
const path = require('path');

// Get year from command line argument
const year = parseInt(process.argv[2]) || new Date().getFullYear();

// Generate date range for specified year
function generateDateRange(year) {
    const dates = [];
    const start = new Date(year, 0, 1);
    const end = new Date(year, 11, 31);

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
    console.log(`ENTSO-E ${year} GENERATION BY TYPE SCRAPER`);
    console.log('='.repeat(80));

    const outputFile = path.join(__dirname, '..', 'data', 'raw', `entsoe_${year}_generation.jsonl`);
    const allDates = generateDateRange(year);
    const existingDates = getExistingDates(outputFile);
    const datesToScrape = allDates.filter(d => !existingDates.has(d));

    console.log(`\nTotal dates in ${year}: ${allDates.length}`);
    console.log(`Already scraped: ${existingDates.size}`);
    console.log(`Remaining: ${datesToScrape.length}\n`);

    if (datesToScrape.length === 0) {
        console.log(`All dates for ${year} already scraped!`);
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
            // URL format: actualGenerationPerProductionType with France BZN
            const url = `https://newtransparency.entsoe.eu/generation/r2/actualGenerationPerProductionType/show?appState=%7B%22sa%22%3A%5B%22BZN%7C10YFR-RTE------C%22%5D%2C%22st%22%3A%22BZN%22%2C%22mm%22%3Afalse%2C%22ma%22%3Afalse%2C%22sp%22%3A%22HALF%22%2C%22dt%22%3A%22TABLE%22%2C%22df%22%3A%22${dateStr}%22%2C%22tz%22%3A%22CET%22%7D`;

            await page.goto(url, { timeout: 30000 });
            await page.waitForTimeout(5000); // Wait for table to load

            const data = await page.evaluate((date) => {
                const table = document.querySelector('table');
                if (!table) return null;

                const rows = table.querySelectorAll('tbody tr');
                const results = [];

                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length < 2) return;

                    const timeRange = cells[0]?.textContent?.trim();
                    if (!timeRange || !timeRange.includes('/')) return;

                    // Extract all production types (columns vary)
                    const productionData = {
                        date: date,
                        timeRange: timeRange
                    };

                    // Get header to map production types
                    const headers = Array.from(table.querySelectorAll('thead th')).map(h => h.textContent.trim());

                    for (let i = 1; i < cells.length; i++) {
                        const value = cells[i]?.textContent?.trim();
                        const header = headers[i];
                        if (header && value) {
                            productionData[header] = parseFloat(value.replace(/['"]/g, '')) || 0;
                        }
                    }

                    results.push(productionData);
                });

                return results;
            }, dateStr);

            if (data && data.length > 0) {
                for (const record of data) {
                    stream.write(JSON.stringify(record) + '\n');
                }
                console.log(`✓ ${data.length} records`);
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
    console.log(`${year} GENERATION SCRAPING COMPLETE!`);
    console.log('='.repeat(80));
    console.log(`Successfully scraped: ${successCount} dates`);
    console.log(`Errors: ${errorCount} dates`);
    console.log(`Output: ${outputFile}`);
}

main().catch(console.error);
