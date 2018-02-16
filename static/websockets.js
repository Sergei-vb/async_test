function loadImages() {
        var ws = new WebSocket("ws://" + location.host + "/load_images/");
        ws.onopen = function() {
           console.log("connected")
        };
        ws.onmessage = function (evt) {
           console.log(evt.data);
           var getjson_images = evt.data;
           var parsejson_images = JSON.parse(getjson_images);
           for (key in parsejson_images.images) {
             document.getElementById("print_images").innerHTML += "<li>" + parsejson_images.images[key] + "</li>";
           };
        };
        ws.onclose = function() {
           console.log("closed");
        };
    }

function loadRunningContainers() {
        var ws = new WebSocket("ws://" + location.host + "/load_running_containers/");
        ws.onopen = function() {
           console.log("connected");
        };
        ws.onmessage = function (evt) {
           console.log(evt.data);
           var getjson_containers = evt.data;
           var parsejson_containers = JSON.parse(getjson_containers);
           for (key in parsejson_containers.containers) {
             document.getElementById("print_containers").innerHTML += "<li>" + parsejson_containers.containers[key] + "</li>";
           };
        };
        ws.onclose = function() {
           console.log("closed");
        };
    }
