import puppeteer from 'puppeteer';
import express from 'express';

// Launch the browser and open a new blank page
const browser = await puppeteer.launch();
const page = await browser.newPage();

// Initializing the Express application
const app = express();

// Defining the port where the server will run
const port = 3000;

// Middleware to log request and response time
app.use((req, res, next) => {
  const currentDate = new Date();
  const startTime = currentDate.getTime();

  console.log(`Request Time: ${currentDate.getHours()}:${currentDate.getMinutes()}:${currentDate.getSeconds()}`);

  // Once the response is sent, log the response time
  res.on('finish', () => {
    const endTime = new Date().getTime();
    const duration = endTime - startTime;
    console.log(`Response Time: ${new Date().getHours()}:${new Date().getMinutes()}:${new Date().getSeconds()} - Duration: ${duration}ms`);
  });

  next(); // Proceed to the next middleware or route handler
});

// Setting up the route for the root URL ('/')
app.get('/', (req, res) => {
  res.send('Hello World!!');
});

// Starting the server and listening on the defined port
app.listen(port, () => {
  console.log(`Proxy Server API is listening at port ${port}`);
});
