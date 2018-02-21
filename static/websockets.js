function load(key_from_html, elem) {
        var ws = new WebSocket("ws://" + location.hostname + ":8888" + "/load_from_docker/");
        ws.onopen = function() {
           var dict = {};
           if (key_from_html == "url-address") {
           $("#print_output").empty();
           dict[key_from_html] = $("#url").val();
           dict["tag_image"] = $("#tag_image").val() || "default";
           } else if (key_from_html == "run") {
           dict[key_from_html] = key_from_html;
           dict["elem"] = elem;
           } else if (key_from_html == "stop") {
           dict[key_from_html] = key_from_html;
           dict["elem"] = elem.slice(1);
           } else {
           dict[key_from_html] = key_from_html;
           };
           dict = JSON.stringify(dict);
           ws.send(dict);
        };
        ws.onmessage = function (evt) {
           var getjson = evt.data;
           var parsejson = JSON.parse(getjson);
           if (key_from_html == "images") {$("#print_images").empty();};
           if (key_from_html == "containers") {$("#print_containers").empty();};
           switch (key_from_html) {
              case "images":
                 for (key in parsejson.images) {
                 $("#print_images").append("<li>" + parsejson.images[key] +
                 "</li>" + "<button onclick='load(\"run\", \"" + parsejson.images[key] +
                 "\")'>Run Container</button>");
                 };
                 break;
              case "containers":
                 for (key in parsejson.containers) {
                 $("#print_containers").append("<li>" + parsejson.containers[key] +
                 "</li>" + "<button onclick='load(\"stop\", \"" + parsejson.containers[key] +
                 "\")'>Stop Container</button>");
                 };
                 break;
              case "url-address":
                 for (key in parsejson) {
                 $("#print_output").append("<li>" + parsejson[key] + "</li>");
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
