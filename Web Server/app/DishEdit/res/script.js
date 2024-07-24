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
  document.getElementById("image-preview").onclick = function () {
    document.getElementById("image-input").click()
  }

  document.getElementById("image-input").onchange = function () {
    if (document.getElementById("image-input").files[0]) {
      var file = new FileReader();
      file.onloadend = function () {
        document.getElementById("image-preview").src = file.result;
        doXHR("POST", "/ajax/DishEdit/image", ajaxImageUpload, file.result)
      }
    file.readAsDataURL(document.getElementById("image-input").files[0]);
    }
  }

  document.getElementById("save").onclick = function () {
    var data = new Object();
    var info = document.getElementsByClassName("info");
    for (var i = 0; i < info.length; i++) {
        data[info[i].name] = info[i].value;
    }
    doXHR("POST", "/ajax/DishEdit/save", ajaxSave, JSON.stringify(data))
  }
}

function ajaxImageUpload (response) {
  var json = JSON.parse(response);
  if (json.status === "success") {
    document.getElementById("image-preview").value = json.id;
    alert("圖片上傳成功!");
  } else {
    alert(json.msg);
  }
}

function ajaxSave (response) {
  var json = JSON.parse(response);
  if (json.status === "success") {
    document.querySelector("a:nth-child(1) .sidenav-link").click();
  } else {
    alert(json.msg);
  }
}
