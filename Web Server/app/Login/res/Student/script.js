if (document.readyState == "complete") {
  setup();
}
else {
  if ("load" in window) {
    load.push(setup);
  }
  else {
    load = [setup];
  }
}

function setup () {
  document.getElementById("login-btn").onclick = function () {
    var data = new Object();
    data.username = document.getElementById("username").value;
    data.password = document.getElementById("password").value;
    doXHR("POST", "/ajax/RestaurantLogin", RestaurantLoginResult, JSON.stringify(data))
  }
}

function RestaurantLoginResult (response) {
  var json = JSON.parse(response);
  if (json.status === "success") {
    document.cookie = "session=" + json.id;
  } else {
    alert(json.msg)
  }
}
