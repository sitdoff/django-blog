/*-------------------------------------------------------------------------------
    PRE LOADER
  -------------------------------------------------------------------------------*/

$(window).load(function() {
  $(".preloader").fadeOut(1000); // set duration in brackets
});

/*-------------------------------------------------------------------------------
    jQuery Parallax
  -------------------------------------------------------------------------------*/

function initParallax() {
  $("#home").parallax("50%", 0.3);
}
initParallax();

/* Back top
  -----------------------------------------------*/

$(window).scroll(function() {
  if ($(this).scrollTop() > 200) {
    $(".go-top").fadeIn(200);
  } else {
    $(".go-top").fadeOut(200);
  }
});
// Animate the scroll to top
$(".go-top").click(function(event) {
  event.preventDefault();
  $("html, body").animate({ scrollTop: 0 }, 300);
});

/* Close message
  -----------------------------------------------*/

// Функция, которая будет вызывать метод click() для каждой кнопки
function clickButtons() {
  // Получаем все кнопки с классом "myButton"
  var buttons = document.getElementsByClassName("close");
  // Перебираем все кнопки
  for (var i = 0; i < buttons.length; i++) {
    // Задержка выполнения метода click() для каждой кнопки на 5 секунд
    setTimeout(
      function(button) {
        button.click();
      },
      5000 * (i + 1),
      buttons[i],
    ); // Увеличиваем задержку для каждой кнопки
  }
}

document.addEventListener("DOMContentLoaded", function() {
  console.log("START!");
  // Вызываем функцию через 5 секунд
  setTimeout(clickButtons, 5000);
  console.log("END!");
});
