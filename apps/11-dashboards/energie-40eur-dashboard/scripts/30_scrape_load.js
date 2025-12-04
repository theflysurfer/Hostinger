/**
 * Script 30: Actual Total Load Scraper for ENTSO-E
 * Scrapes actual electricity consumption (load) in France
 * Usage: node scripts/30_scrape_load.js 2024
 */

const fs = require('fs');
const path = require('path');

// Get year from command line argument
const year = parseInt(process.argv[2]) || new Date().getFullYear();

// Generate date range for specified year
function generateDateRange(year) {
    const dates = [];
    const start = new Date(year, 0, 1); // January 1st
    const end = new Date(year, 11, 31); // December 31st

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
    console.log(`ENTSO-E ${year} ACTUAL TOTAL LOAD SCRAPER`);
    console.log('='.repeat(80));

    const outputFile = path.join(__dirname, '..', 'data', 'raw', `entsoe_load_${year}_scraped.jsonl`);
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
            // URL format for Actual Total Load (NEW PLATFORM - CORRECTED)
            // Area: France (10YFR-RTE------C) as BZN (Bidding Zone)
            // Date format must be array: ["YYYY-MM-DD", "YYYY-MM-DD"]
            // mm: true (show multiple markets - forecast + actual)
            // dt: TABLE (table view mode)
            const url = `https://newtransparency.entsoe.eu/load/total/dayAhead?appState=%7B%22sa%22%3A%5B%22BZN%7C10YFR-RTE------C%22%5D%2C%22st%22%3A%22BZN%22%2C%22mm%22%3Atrue%2C%22ma%22%3Afalse%2C%22sp%22%3A%22HALF%22%2C%22dt%22%3A%22TABLE%22%2C%22df%22%3A%5B%22${dateStr}%22%2C%22${dateStr}%22%5D%2C%22tz%22%3A%22CET%22%7D`;

            await page.goto(url, { timeout: 30000 });
            await page.waitForTimeout(10000); // Wait for data to load

            const data = await page.evaluate((date) => {
                const rows = document.querySelectorAll('table tbody tr');
                const results = [];

                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 3) { // Time + forecast + actual columns
                        const timeRange = cells[0]?.textContent?.trim();

                        if (timeRange && timeRange.includes(' - ')) {
                            // Column 0: MTU (time range)
                            // Column 1: Day Ahead Total Load Forecast (MW)
                            // Column 2: Actual Total Load (MW)
                            const forecastLoad = cells[1]?.textContent?.trim();
                            const actualLoad = cells[2]?.textContent?.trim();

                            const record = {
                                date: date,
                                timeRange: timeRange,
                                load: {}
                            };

                            // Parse forecast load
                            if (forecastLoad && forecastLoad !== 'n/e' && forecastLoad !== '') {
                                record.load.forecast_mw = parseFloat(forecastLoad.replace(/,/g, '') || '0');
                            } else {
                                record.load.forecast_mw = null;
                            }

                            // Parse actual load
                            if (actualLoad && actualLoad !== 'n/e' && actualLoad !== '') {
                                record.load.actual_mw = parseFloat(actualLoad.replace(/,/g, '') || '0');
                            } else {
                                record.load.actual_mw = null;
                            }

                            // Calculate delta if both values exist
                            if (record.load.actual_mw !== null && record.load.forecast_mw !== null) {
                                record.load.delta_mw = record.load.actual_mw - record.load.forecast_mw;
                            }

                            results.push(record);
                        }
                    }
                });
                return results;
            }, dateStr);

            if (data && data.length > 0) {
                for (const record of data) {
                    stream.write(JSON.stringify(record) + '\n');
                }

                console.log(`OK ${data.length} hours`);
                successCount++;
            } else {
                console.log('WARNING No data');
                errorCount++;
            }

            // Rate limiting
            await page.waitForTimeout(3000);

            // Progress checkpoint
            if ((i + 1) % 50 === 0) {
                console.log(`\nProgress: ${i+1}/${datesToScrape.length} (${((i+1)/datesToScrape.length*100).toFixed(1)}%)`);
                console.log(`   Success: ${successCount}, Errors: ${errorCount}\n`);
            }

        } catch (error) {
            console.log(`ERROR: ${error.message}`);
            errorCount++;
        }
    }

    stream.end();
    await browser.close();

    console.log('\n' + '='.repeat(80));
    console.log(`${year} LOAD SCRAPING COMPLETE!`);
    console.log('='.repeat(80));
    console.log(`Success: ${successCount}/${datesToScrape.length} dates`);
    console.log(`Errors: ${errorCount}`);
    console.log(`Output: ${outputFile}`);
    console.log('='.repeat(80));
}

main().catch(console.error);
