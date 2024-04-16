function dark_light(){
  const colors = document.querySelectorAll(".color");

  colors.forEach(color => {
    color.addEventListener("click", e => {
      colors.forEach(c => c.classList.remove("selected"));
      const theme = color.getAttribute("data-color");
      document.body.setAttribute("data-theme", theme);
      color.classList.add("selected");
    });
  });
  document.body.classList.toggle("dark-mode");
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

var userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone
var csrftoken = getCookie('csrftoken');
var xhr = new XMLHttpRequest();
xhr.open('POST', '/save_timezone/', true);
xhr.setRequestHeader('Content-Type', 'application/json');
xhr.setRequestHeader('X-CSRFToken', csrftoken);

xhr.onreadystatechange = function() {
    if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status === 200) {
            console.log('Timezone saved successfully');
        } else {
            console.error('Error saving timezone');
        }
    }
};

xhr.send(JSON.stringify({ timezone: userTimezone }));


$.ajaxSetup({
  headers: {
      "X-CSRFToken": getCookie("csrftoken")
  }
});
$(document).ready(function () {
  $("#input_message").on("submit", function (event) {
    var $form = $(this);
    event.preventDefault();

    document.getElementById('emoji-menu').style.display = 'none';
    $.ajax({
      url: document.URL,
      type: "post",
      data: $form.serialize(),
      success: function(data){
        $("body").html(data);
      }
    })
  });
});

$.ajaxSetup({
  headers: {
      "X-CSRFToken": getCookie("csrftoken")
  }
});

$(document).ready(function () {
  const emojiIcon = document.getElementById('emoji-icon');
  const emojiMenu = document.getElementById('emoji-menu');

  emojiIcon.addEventListener('click', function() {
    if (emojiMenu.style.display === 'block'){
      emojiMenu.style.display = 'none';
    }
    else {
      emojiMenu.style.display = 'block';
    }
  });

});

function insertEmoji(emoji) {
  var input = document.getElementById('input_message').input_message;
  input.value += emoji;
}