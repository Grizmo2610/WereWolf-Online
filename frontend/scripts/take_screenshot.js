import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  try {
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle0', timeout: 10000 });
  } catch (e) {
    console.log('Could not connect to localhost:5173, taking screenshot');
  }
  await new Promise(r => setTimeout(r, 2000));
  await page.screenshot({ path: '../images/screenshot.png', fullPage: true });
  await browser.close();
  console.log('Screenshot saved to images/screenshot.png');
})();
