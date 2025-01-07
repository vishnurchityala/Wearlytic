// Importing Express to create the server
const express = require('express')

// Initializing the Express application
const app = express()

// Defining the port where the server will run
const port = 3000

// Setting up the route for the root URL ('/')
app.get('/', (req, res) => {
    res.send('Hello World!!')
})

// Starting the server and listening on the defined port
app.listen(port, () => {
    console.log(`Proxy Server API is listening at port ${port}`)
})
