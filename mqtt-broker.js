const aedes = require('aedes')()
const server = require('net').createServer(aedes.handle)
const httpServer = require('http').createServer()
const ws = require('websocket-stream')

// MQTT over TCP
const MQTT_PORT = 1885
// MQTT over WebSocket  
const WS_PORT = 9003

// Start MQTT server
server.listen(MQTT_PORT, function () {
  console.log(`🚀 Aedes MQTT server listening on port ${MQTT_PORT}`)
})

// Start WebSocket server
ws.createServer({ server: httpServer }, aedes.handle)
httpServer.listen(WS_PORT, function () {
  console.log(`🌐 WebSocket server listening on port ${WS_PORT}`)
})

// Log client connections
aedes.on('client', function (client) {
  console.log(`📱 Client connected: ${client.id}`)
})

aedes.on('clientDisconnect', function (client) {
  console.log(`📱 Client disconnected: ${client.id}`)
})

aedes.on('publish', function (packet, client) {
  if (packet.topic !== '$SYS/lastWill') {
    console.log(`📨 Message published on ${packet.topic}:`, packet.payload.toString())
  }
})

aedes.on('subscribe', function (subscriptions, client) {
  console.log(`📡 Client ${client.id} subscribed to:`, subscriptions.map(s => s.topic).join(', '))
})

console.log('🔧 MQTT Broker with WebSocket support started')
