export default function(e) {
    const data = JSON.parse(e.data);
    if (data.type !== "frontend") return;
}