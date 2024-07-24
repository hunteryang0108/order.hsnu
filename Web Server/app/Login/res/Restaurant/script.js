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
    doXHR("POST", "/ajax/Login/Restaurant", RestaurantLoginResult, JSON.stringify(data))
  }
}

function RestaurantLoginResult (response) {
  var json = JSON.parse(response);
  if (json.status === "success") {
    document.querySelector("a:nth-child(1) .sidenav-link").click();
  } else {
    alert(json.msg)
  }
}
