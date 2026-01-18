export default function handleWebsocketMessages(e) {
    const data = JSON.parse(e.data);
    if (data.sender !== "self") return;

    let header = data.header;

}
