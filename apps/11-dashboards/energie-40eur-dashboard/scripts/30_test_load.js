/**
 * Test Script: Load Scraper Test for One Date
 * Tests the corrected Load scraper on 2024-06-15
 */

const fs = require('fs');
const path = require('path');

async function main() {
    const { chromium } = require('playwright');

    const testDate = '2024-06-15';
    console.log('='.repeat(60));
    console.log(`TESTING LOAD SCRAPER ON ${testDate}`);
    console.log('='.repeat(60));

    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    try {
        // URL format for Actual Total Load (NEW PLATFORM - CORRECTED)
        const url = `https://newtransparency.entsoe.eu/load/total/dayAhead?appState=%7B%22sa%22%3A%5B%22BZN%7C10YFR-RTE------C%22%5D%2C%22st%22%3A%22BZN%22%2C%22mm%22%3Atrue%2C%22ma%22%3Afalse%2C%22sp%22%3A%22HALF%22%2C%22dt%22%3A%22TABLE%22%2C%22df%22%3A%5B%22${testDate}%22%2C%22${testDate}%22%5D%2C%22tz%22%3A%22CET%22%7D`;

        console.log(`\n1. Navigating to URL...`);
        await page.goto(url, { timeout: 30000 });

        console.log(`2. Waiting for data to load (10s)...`);
        await page.waitForTimeout(10000);

        console.log(`3. Extracting data...`);
        const data = await page.evaluate((date) => {
            const rows = document.querySelectorAll('table tbody tr');
            const results = [];

            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length >= 3) {
                    const timeRange = cells[0]?.textContent?.trim();

                    if (timeRange && timeRange.includes(' - ')) {
                        const forecastLoad = cells[1]?.textContent?.trim();
                        const actualLoad = cells[2]?.textContent?.trim();

                        const record = {
                            date: date,
                            timeRange: timeRange,
                            load: {}
                        };

                        if (forecastLoad && forecastLoad !== 'n/e' && forecastLoad !== '') {
                            record.load.forecast_mw = parseFloat(forecastLoad.replace(/,/g, '') || '0');
                        } else {
                            record.load.forecast_mw = null;
                        }

                        if (actualLoad && actualLoad !== 'n/e' && actualLoad !== '') {
                            record.load.actual_mw = parseFloat(actualLoad.replace(/,/g, '') || '0');
                        } else {
                            record.load.actual_mw = null;
                        }

                        if (record.load.actual_mw !== null && record.load.forecast_mw !== null) {
                            record.load.delta_mw = record.load.actual_mw - record.load.forecast_mw;
                        }

                        results.push(record);
                    }
                }
            });
            return results;
        }, testDate);

        console.log(`\n4. Results:`);
        console.log(`   Records extracted: ${data.length}`);

        if (data.length > 0) {
            console.log(`\n5. Sample records (first 3):`);
            data.slice(0, 3).forEach((record, idx) => {
                console.log(`\n   Record ${idx + 1}:`);
                console.log(`   ${JSON.stringify(record, null, 2)}`);
            });

            console.log(`\n6. Statistics:`);
            const avgActual = data.reduce((sum, r) => sum + (r.load.actual_mw || 0), 0) / data.length;
            const avgForecast = data.reduce((sum, r) => sum + (r.load.forecast_mw || 0), 0) / data.length;
            const avgDelta = data.reduce((sum, r) => sum + (r.load.delta_mw || 0), 0) / data.length;

            console.log(`   Avg Actual Load: ${avgActual.toFixed(2)} MW`);
            console.log(`   Avg Forecast Load: ${avgForecast.toFixed(2)} MW`);
            console.log(`   Avg Delta: ${avgDelta.toFixed(2)} MW`);

            // Write to test file
            const outputFile = path.join(__dirname, '..', 'data', 'raw', 'entsoe_load_test.jsonl');
            const stream = fs.createWriteStream(outputFile);
            data.forEach(record => {
                stream.write(JSON.stringify(record) + '\n');
            });
            stream.end();

            console.log(`\n7. Test output written to: ${outputFile}`);
            console.log(`\n${'='.repeat(60)}`);
            console.log(`✅ TEST SUCCESSFUL - Script is working correctly!`);
            console.log(`${'='.repeat(60)}`);
        } else {
            console.log(`\n❌ TEST FAILED - No data extracted`);
        }

    } catch (error) {
        console.error(`\n❌ TEST FAILED - Error: ${error.message}`);
    } finally {
        await browser.close();
    }
}

main().catch(console.error);
