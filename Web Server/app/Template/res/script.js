if ("load" in window) {
  load.push(setup);
}
else {
  load = [setup];
}

function setup() {
  document.getElementById("sidenav-toggler").onclick = function () {
    document.getElementById("sidenav").classList.remove("hidden");
    document.getElementById("overlay").classList.remove("hidden");
    window.overlay = document.getElementById("sidenav");
  }
  document.getElementById("cart-toggler").onclick = function () {
    document.getElementById("cart").classList.remove("hidden");
    document.getElementById("overlay").classList.remove("hidden");
    window.overlay = document.getElementById("cart");
  }
  document.getElementById("overlay").onclick = function () {
    window.overlay.classList.add("hidden");
    document.getElementById("overlay").classList.add("hidden");
  }
  if (document.cookie.split('; ').find(row => row.startsWith('session')) == null || document.cookie.split('; ').find(row => row.startsWith('session')).split('=')[1] === '') {
    document.querySelector('a:nth-child(3) .sidenav-link').style = "display: none;";
    document.querySelector('a:nth-child(2) .sidenav-link').style = "display: block;";
  } else {
    document.querySelector('a:nth-child(2) .sidenav-link').style = "display: none;";
    document.querySelector('a:nth-child(3) .sidenav-link').style = "display: block;";
  }
  var links = document.getElementsByClassName("sidenav-link");
  for (var i = 0; i < links.length; i++) {
    links[i].onclick = function (event) {
      event.preventDefault();
      document.getElementById("content").classList.add('hidden');
      var e = event.target;
      while (e.tagName != "A") {
        e = e.parentNode;
      }
      history.pushState("", "", new URL(e.href).pathname);
      setTimeout(() => doXHR("GET", "/ajax" + new URL(e.href).pathname, load_page), 200);
      document.getElementById("overlay").click();
    }
  }
}

window.onload = function () {
  for (var i = 0; i < load.length; i++) {
    load[i]();
  }
}

function load_page(response) {
  var head = document.getElementsByTagName("head")[0]
  var change = document.querySelectorAll(".change")
  for (var i = 0; i < change.length; i++) {
    head.removeChild(change[i]);
  }
  response = JSON.parse(response);
  document.getElementById("content").innerHTML = response.html;
  head.insertAdjacentHTML('beforeend', response.style);
  var scripts = document.createElement(null);
  scripts.innerHTML = response.script;
  scripts = scripts.children;
  for (var i = 0; i < scripts.length; i++) {
    var script = document.createElement("script");
    attr = scripts[i].attributes
    for (var j = 0; j < attr.length; j++)
    script.setAttribute(attr[j].nodeName, attr[j].nodeValue);
    head.appendChild(script);
  }
  if (document.cookie.split('; ').find(row => row.startsWith('session')) == null || document.cookie.split('; ').find(row => row.startsWith('session')).split('=')[1] === '') {
    document.querySelector('a:nth-child(3) .sidenav-link').style = "display: none;";
    document.querySelector('a:nth-child(2) .sidenav-link').style = "display: block;";
  } else {
    document.querySelector('a:nth-child(2) .sidenav-link').style = "display: none;";
    document.querySelector('a:nth-child(3) .sidenav-link').style = "display: block;";
  }
  setTimeout(() => document.getElementById("content").classList.remove('hidden'), 800);
}

function doXHR(method, url, handler, data=null) {
  var ajax = new XMLHttpRequest();
  ajax.onload = function () {
    handler(ajax.responseText);
  }
  ajax.open(method, url);
  ajax.send(data);
}
