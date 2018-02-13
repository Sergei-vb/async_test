var ws = new WebSocket("ws://" + location.host + "/websocket/");
ws.onopen = function() {
   console.log("connected");
};
ws.onmessage = function (evt) {
   console.log(evt.data);
};
ws.onclose = function() {
   console.log("closed")
};
