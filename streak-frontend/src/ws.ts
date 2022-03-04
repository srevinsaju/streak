import { GetWebsocketId } from './api'
import { WebsocketAuth } from './types'


export function ListenEventChanges() {
    return
    let wsEndpoint = `/`
    let ws = new WebSocket(wsEndpoint)

    let websocketHandshakeSuccess = false

    ws.onmessage = function (event) {
        
    }
    ws.onerror = function (event) {
        console.log(event)
        console.log(`Something went wrong when connecting to wsEndpoint: ${wsEndpoint}`)
    }
}
