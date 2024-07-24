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
  document.getElementById('refresh').onclick = function (event) {
    doXHR("GET", "/ajax/Order", getData);
    event.target.style = 'display: none;';
    setTimeout(() => event.target.click(), 1500);
  }
}

function getData (response) {
  var data = JSON.parse(response);
  classes = Object.keys(data);
  for (var i = 0; i < classes.length; i++) {
    classnum = classes[i];
    var e = document.getElementById(classnum)
    if (e != null) {
      e.getElementsByTagName('progress')[0].value = data[classes[i]];
    } else {
      div = document.createElement('div');
      div.id = classes[i];
      div.classList.add('data');
      span = document.createElement('span');
      span.classList.add('classnum');
      span.textContent = classes[i];
      div.appendChild(span);
      progress = document.createElement('progress');
      progress.classList.add('progress');
      progress.max = 20;
      progress.value = data[classes[i]];
      div.appendChild(progress);
      document.getElementById('classes').appendChild(div);
    }
  }
}




