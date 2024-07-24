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

doXHR("GET", "/ajax/Menu/meals", getMeals);

function getMeals (response) {
  var meals = JSON.parse(response).meals;
  for (var i = 0; i < meals.length; i++) {
    var meal = document.createElement("div");
    meal.classList.add("meal");
    var dish_pic = document.createElement("div");
    dish_pic.classList.add("meal-pic");
    var pic = document.createElement("img");
    pic.src = "/res/Menu/image/" + meals[i].id + ".jpg";
    pic.classList.add("pic");
    dish_pic.appendChild(pic);
    meal.appendChild(dish_pic);
    var meal_name = document.createElement("div");
    meal_name.textContent = meals[i].name;
    meal_name.classList.add("name");
    meal.appendChild(meal_name);
    var restaurant = document.createElement("div");
    restaurant.textContent = "學生餐廳";
    restaurant.classList.add("restaurant");
    meal.appendChild(restaurant);
    var price = document.createElement("div");
    price.textContent = '$' + meals[i].price;
    price.classList.add("price");
    meal.appendChild(price);
    var intro = document.createElement("div");
    intro.textContent = meals[i].intro;
    intro.classList.add("intro");
    meal.appendChild(intro);
    meal.id = meals[i].id;
    meal.onclick = function (event) {
      var e = event.target;
      while (!(e.classList.contains('meal'))) {
        e = e.parentNode;
      }
      detail = e.cloneNode(true);
      detail.classList.add('detail');
      detail.classList.add('hidden');
      orderbtn = document.createElement('button');
      orderbtn.onclick = function () {
        if (document.cookie.split('; ').find(row => row.startsWith('session')) == null || document.cookie.split('; ').find(row => row.startsWith('session')).split('=')[1] === '') {
          alert('您尚未登入');
        } else {
          doXHR("POST", "/ajax/Order", ajaxOrder, document.getElementsByClassName("detail")[0].id);
        }
      }
      btntext = document.createTextNode("訂購");
      orderbtn.appendChild(btntext);
      orderbtn.classList.add('order-btn');
      detail.appendChild(orderbtn);
      document.getElementsByClassName("detail")[0].replaceWith(detail);
      document.getElementById("overlay").classList.remove("hidden");
      detail.classList.remove("hidden");
      window.overlay = detail;
    }
    document.getElementById("browse").appendChild(meal);
  }
}

function setup () {
  if (!("slide" in window)) {
    slide = 1
  }
  
  window.onhashchange = function () {
    if (location.hash === "#Browse" || location.hash === "") {
      document.getElementById("option-browse").classList.add("active");
      document.getElementById("option-browse-decoration").classList.add("active");
      document.getElementById("option-search").classList.remove("active");
      document.getElementById("option-search-decoration").classList.remove("active");
    } else if (location.hash === "#Search") {
      document.getElementById("option-search").classList.add("active");
      document.getElementById("option-search-decoration").classList.add("active");
      document.getElementById("option-browse").classList.remove("active");
      document.getElementById("option-browse-decoration").classList.remove("active");
    }
  }
  
  window.onhashchange()
  document.getElementById("option-browse").classList.remove("initial");
  document.getElementById("option-browse-decoration").classList.remove("initial");
  document.getElementById("option-search").classList.remove("initial");
  document.getElementById("option-search-decoration").classList.remove("initial");
  
  document.getElementById("next-slide").onclick = function () {
    slide += 1;
    show_slide(slide);
    document.getElementById("next-slide").classList.add("clicked")
    setTimeout(() => document.getElementById("next-slide").classList.remove("clicked"), 300)
  }
  document.getElementById("prev-slide").onclick = function () {
    slide -= 1;
    show_slide(slide);
    document.getElementById("prev-slide").classList.add("clicked");
    setTimeout(() => document.getElementById("prev-slide").classList.remove("clicked"), 300)
  }
}

function show_slide (n) {
  var slides = document.getElementsByClassName("image");
  for (var i = 0; i < slides.length; i++) {
    slides[i].classList.remove("prev");
    slides[i].classList.remove("show");
    slides[i].classList.remove("next");
  }
  if (n > slides.length) {
    n = slides.length;
  } else if (n < 1) {
    n = 1;
  }
  slide = n;
  if (n < slides.length) {
    slides[n].classList.add("show");
    slides[n].classList.add("next");
  }
  if (n > 1) {
    slides[n - 2].classList.add("show");
    slides[n - 2].classList.add("prev");
  }
  slides[n - 1].classList.add("show");
}

function ajaxOrder (response) {
  if (response == "success") {
    alert('訂購成功');
    document.querySelector("a:nth-child(1) .sidenav-link").click();    
  } else {
    alert('訂購失敗');
  }
}




