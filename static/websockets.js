function load(key_from_html) {
        var ws = new WebSocket("ws://" + location.host + "/load_from_docker/");
        ws.onopen = function() {
           console.log("opened");
           if (key_from_html == "url-address") {
           var value_url = $("#url").val()
           var dict = {};
           dict[key_from_html] = value_url;
           dict = JSON.stringify(dict);
           ws.send(dict);
           } else {
           var dict = {};
           dict[key_from_html] = key_from_html;
           dict = JSON.stringify(dict);
           ws.send(dict);
           }
        };
        ws.onmessage = function (evt) {
           var getjson = evt.data;
           var parsejson = JSON.parse(getjson);
           if (key_from_html == "images") {$("#print_images").empty();};
           if (key_from_html == "containers") {$("#print_containers").empty();};
           switch (key_from_html) {
              case "images":
                 for (key in parsejson.images) {
                 $("#print_images").append("<li>" + parsejson.images[key] + "</li>");
                 };
                 break;
              case "containers":
                 for (key in parsejson.containers) {
                 $("#print_containers").append("<li>" + parsejson.containers[key] + "</li>");
                 };
                 break;
              case "url-address":
                 for (key in parsejson) {
                 $("#output").append("<li>" + parsejson[key] + "</li>");
                 };
                 break;
              default:
                 alert(parsejson.message)
           };
        };
        ws.onclose = function() {
           console.log("closed");
        };
    }
