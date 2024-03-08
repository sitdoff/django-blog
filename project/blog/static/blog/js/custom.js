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
  // Вызываем функцию через 5 секунд
  setTimeout(clickButtons, 5000);
});

/* Subscrib
  -----------------------------------------------*/
// ajax.js

$(document).ready(function() {
  $("#subscribe-link").click(function(event) {
    event.preventDefault(); // Предотвращаем стандартное действие ссылки

    // Получаем URL из атрибута data-url
    var url = $(this).data("url");

    // Выполняем AJAX запрос
    $.ajax({
      url: url, // URL представления
      method: "GET", // Метод запроса (GET, POST и т.д.)
      success: function(data) {
        // Создаем родительский контейнер для сообщений и присваиваем ему класс
        var messageDivParent = document.createElement("div");
        messageDivParent.className = "message-container fixed-top";

        // Добавляем родителский класс в документ
        document.body.appendChild(messageDivParent);

        // Создаем дочерний класс сообщений и присваиваем ему id, класс и роль
        var messageDiv = document.createElement("div");
        messageDiv.id = "message-div";
        messageDiv.className = "alert " + data.message_level + " alert-dismissible";
        messageDiv.role = "alert";

        // Добавляем дочерний класс в родительский
        messageDivParent.appendChild(messageDiv);

        // Получаем текст сообщения
        var message = data.message;
        // Изменяем содержимое div на сообщение
        $("#message-div").text(message);
        // Показываем div
        $("#message-div").show();
        setTimeout(function() {
          // Скрываем и удаляем элемент
          messageDivParent.style.display = "none";
          messageDivParent.remove();
        }, 2000); // 2000 миллисекунд = 2 секунды
      },
      error: function(xhr, status, error) {
        // Обработка ошибки
        console.error("Произошла ошибка:", error);
      },
    });
  });
});
