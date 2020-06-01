const express = require('express')
const path = require('path')
const app = express()
const port = process.env.PORT || 8080

app.use('/organisation', express.static(path.join(__dirname, 'docs')))
app.use('/map-templates', express.static(path.join(__dirname, 'map-templates/docs')))
app.listen(port)
console.log('organisation has been built to http://localhost:' + port + '/organisation')
