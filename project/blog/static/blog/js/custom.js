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

$(document).ready(function() {
  // Функция, которая будет проверять наличие контейнера с классом "message-container fixed-top"
  function getMessageContainer() {
    var existingContainer = document.querySelector(".message-container.fixed-top");
    if (!existingContainer) {
      existingContainer = document.createElement("div");
      existingContainer.className = "message-container fixed-top";
      document.body.appendChild(existingContainer);
    }
    return existingContainer;
  }

  $(".subscribe-unsubscribe").on("click", "#subscribe-link", function(event) {
    event.preventDefault(); // Предотвращаем стандартное действие ссылки

    var link = this;

    // Получаем URL из атрибута data-url
    var url = link.getAttribute("data-url");

    // Выполняем AJAX запрос
    $.ajax({
      url: url, // URL представления
      method: "GET", // Метод запроса (GET, POST и т.д.)
      success: function(data) {
        // Меняем текст в ссылке
        if (link.textContent == "Подписаться") {
          link.textContent = "Отписаться";
          link.id = "unsubscribe-link";
          var unsubscribeUrl = url.replace("subscribe", "unsubscribe");
          link.setAttribute("data-url", unsubscribeUrl);
        } else {
          link.textContent = "Подписаться";
        }

        showMessage(data.message, data.message_level);
      },
      error: function(xhr, status, error) {
        // Обработка ошибки
        console.error("Произошла ошибка:", error);
      },
    });
  });

  $(".subscribe-unsubscribe").on("click", "#unsubscribe-link", function(event) {
    event.preventDefault(); // Предотвращаем стандартное действие ссылки

    var link = this;

    // Получаем URL из атрибута data-url
    var url = link.getAttribute("data-url");

    // Выполняем AJAX запрос
    $.ajax({
      url: url, // URL представления
      method: "GET", // Метод запроса (GET, POST и т.д.)
      success: function(data) {
        // Меняем текст в ссылке
        if (link.textContent == "Отписаться") {
          link.textContent = "Подписаться";
          link.id = "subscribe-link";
          var subscribeUrl = url.replace("unsubscribe", "subscribe");
          link.setAttribute("data-url", subscribeUrl);
        } else {
          link.textContent = "Отписаться";
        }

        showMessage(data.message, data.message_level);
      },
      error: function(xhr, status, error) {
        // Обработка ошибки
        console.error("Произошла ошибка:", error);
      },
    });
  });

  function showMessage(message, messageLevel) {
    // Создаем родительский контейнер для сообщений и присваиваем ему класс
    var messageDivParent = getMessageContainer();

    // Создаем дочерний класс сообщений и присваиваем ему id, класс и роль
    var messageDiv = document.createElement("div");
    messageDiv.id = "message-div";
    messageDiv.className = "alert " + messageLevel + " alert-dismissible";
    messageDiv.role = "alert";
    messageDiv.textContent = message;

    // Добавляем дочерний класс в родительский
    messageDivParent.appendChild(messageDiv);

    // Показываем div
    $("#message-div").show();

    setTimeout(function() {
      // Скрываем и удаляем элемент
      $("#message-div").remove();
    }, 2000); // 2000 миллисекунд = 2 секунды
  }
});
