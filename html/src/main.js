import * as utils from "/src/utils.js"
import * as packets from "/src/packets.js"
import * as auth from "/src/auth.js"
import * as jsonpack from "/src/jsonpack.js"

const hostname = window.location.href.split('/')[2]

//import * as crypto from "/src/crypto-js.min.js"

let rawClient = new packets.rawClient('/listen')
let client = new auth.authClient(rawClient)

window.utils = utils
window.packets = packets
window.auth = auth
window.jsonpack = jsonpack

window.rawClient = rawClient
window.authClient = client

window.authLogin = client.login
window.sendAuth = client.send
window.sendRaw = rawClient.send
window.addRawTypeListener = rawClient.addRawTypeListener