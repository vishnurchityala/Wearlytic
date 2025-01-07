// Importing Express to create the server
const express = require('express')

// Initializing the Express application
const app = express()

// Defining the port where the server will run
const port = 3000

// Setting up the route for the root URL ('/')
app.get('/', (req, res) => {
  const currentDate = new Date();
  var hours = currentDate.getHours();
  var minutes = currentDate.getMinutes();
  var seconds = currentDate.getSeconds();
  console.log(`Request Time: ${hours}:${minutes}:${seconds}`);
  res.send('Hello World!!')
  hours = currentDate.getHours();
  minutes = currentDate.getMinutes();
  seconds = currentDate.getSeconds();
  console.log(`Response Time: ${hours}:${minutes}:${seconds}`);
})

// Starting the server and listening on the defined port
app.listen(port, () => {
    console.log(`Proxy Server API is listening at port ${port}`)
})
