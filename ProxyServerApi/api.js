import express from 'express';
import puppeteer from 'puppeteer';
import cors from 'cors';

const app = express();
const port = 3000;

app.use(cors())

// Middleware to log request and response time
app.use((req, res, next) => {
  const startTime = Date.now();
  console.log(`Request Time: ${new Date().toISOString()}`);

  res.on('finish', () => {
    const duration = Date.now() - startTime;
    console.log(`Response Time: ${new Date().toISOString()} - Duration: ${duration}ms`);
  });

  next();
});

// Endpoint to fetch HTML content
app.get('/fetch', async (req, res) => {
  const url = req.query.url;

  if (!url) {
    return res.status(400).send({ error: 'URL parameter is required.' });
  }

  try {
    const decodedUrl = decodeURIComponent(url);

    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto(decodedUrl, { waitUntil: 'networkidle2' });

    const htmlContent = await page.content();

    await browser.close();

    res.set('Content-Type', 'text/html');
    res.send(htmlContent);

  } catch (error) {
    console.error('Error fetching the HTML content:', error);
    res.status(500).send({ error: 'Failed to fetch the HTML content. Check the URL and try again.' });
  }
});

// Root route
app.get('/', (req, res) => {
  res.send('Hello World!!');
});

// Start the server
app.listen(port, () => {
  console.log(`Proxy Server API is listening at port ${port}`);
});
