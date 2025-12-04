/**
 * Script 20: Physical Flows Scraper for ENTSO-E
 * Scrapes cross-border electricity flows between France and neighboring countries
 * Usage: node scripts/20_scrape_physical_flows.js 2024
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
    console.log(`ENTSO-E ${year} PHYSICAL FLOWS SCRAPER`);
    console.log('='.repeat(80));

    const outputFile = path.join(__dirname, '..', 'data', 'raw', `entsoe_flows_${year}_scraped.jsonl`);
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
            // URL format for Physical Flows
            const url = `https://newtransparency.entsoe.eu/transmission/physicalFlows?appState=%7B%22sa%22%3A%5B%22CTY%7C10YFR-RTE------C%22%5D%2C%22st%22%3A%22CTY%22%2C%22mm%22%3Afalse%2C%22ma%22%3Afalse%2C%22dt%22%3A%22TABLE%22%2C%22df%22%3A%22${dateStr}%22%2C%22tz%22%3A%22CET%22%7D`;

            await page.goto(url, { timeout: 30000 });
            await page.waitForTimeout(8000); // Wait for data to load

            const data = await page.evaluate((date) => {
                const rows = document.querySelectorAll('table tbody tr');
                const results = [];

                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 13) { // 1 time + 12 flow columns
                        const timeRange = cells[0]?.textContent?.trim();

                        if (timeRange && timeRange.includes(' - ')) {
                            // Extract flows for each country pair
                            // Order: BE, DE, IT, ES, CH, UK (FR→Country then Country→FR)
                            const record = {
                                date: date,
                                timeRange: timeRange,
                                flows: {
                                    'FR-BE': parseFloat(cells[1]?.textContent?.trim().replace(/["']/g, '') || '0'),
                                    'BE-FR': parseFloat(cells[2]?.textContent?.trim().replace(/["']/g, '') || '0'),
                                    'FR-DE': parseFloat(cells[3]?.textContent?.trim().replace(/["']/g, '') || '0'),
                                    'DE-FR': parseFloat(cells[4]?.textContent?.trim().replace(/["']/g, '') || '0'),
                                    'FR-IT': parseFloat(cells[5]?.textContent?.trim().replace(/["']/g, '') || '0'),
                                    'IT-FR': parseFloat(cells[6]?.textContent?.trim().replace(/["']/g, '') || '0'),
                                    'FR-ES': parseFloat(cells[7]?.textContent?.trim().replace(/["']/g, '') || '0'),
                                    'ES-FR': parseFloat(cells[8]?.textContent?.trim().replace(/["']/g, '') || '0'),
                                    'FR-CH': parseFloat(cells[9]?.textContent?.trim().replace(/["']/g, '') || '0'),
                                    'CH-FR': parseFloat(cells[10]?.textContent?.trim().replace(/["']/g, '') || '0'),
                                    'FR-UK': parseFloat(cells[11]?.textContent?.trim().replace(/["']/g, '') || '0'),
                                    'UK-FR': parseFloat(cells[12]?.textContent?.trim().replace(/["']/g, '') || '0')
                                }
                            };
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

                // Calculate total exports
                const totalExports = data.reduce((sum, r) => {
                    return sum + r.flows['FR-BE'] + r.flows['FR-DE'] + r.flows['FR-IT'] +
                           r.flows['FR-ES'] + r.flows['FR-CH'] + r.flows['FR-UK'];
                }, 0);

                console.log(`✓ ${data.length} hours (exports: ${(totalExports/1000).toFixed(0)} GWh)`);
                successCount++;
            } else {
                console.log('⚠️  No data');
                errorCount++;
            }

            // Rate limiting
            await page.waitForTimeout(3000);

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
    console.log(`${year} PHYSICAL FLOWS SCRAPING COMPLETE!`);
    console.log('='.repeat(80));
    console.log(`Success: ${successCount}/${datesToScrape.length} dates`);
    console.log(`Errors: ${errorCount}`);
    console.log(`Output: ${outputFile}`);
    console.log('='.repeat(80));
}

main().catch(console.error);
