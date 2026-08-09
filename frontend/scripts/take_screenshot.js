import puppeteer from 'puppeteer';
import path from 'path';
import { pathToFileURL } from 'url';

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  
  const htmlPath = path.resolve('../html_export/index.html');
  const fileUrl = pathToFileURL(htmlPath).href;
  
  try {
    await page.goto(fileUrl, { waitUntil: 'networkidle0', timeout: 10000 });
  } catch (e) {
    console.log('Error navigating to local html:', e.message);
  }
  
  await new Promise(r => setTimeout(r, 2000));
  await page.screenshot({ path: '../images/screenshot.png', fullPage: true });
  await browser.close();
  console.log('Screenshot updated from html_export/index.html to images/screenshot.png');
})();
