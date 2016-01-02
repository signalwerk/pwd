$(function () {

  var jsonData = null;

  var generatPW = function (items) {
    var itemsCount = items.length
    var pw = '';

    for (var i = 4; i > 0; i--) {
      pw += items[Math.floor(Math.random() * itemsCount)];
    };

    return pw;
  }

  var outputPW = function (items) {
    var passwords = [];
    var count = 25;

    for (var i = count; i > 0; i--) {
      passwords.push(generatPW(items));
    };

    $("#output").val(passwords.join('\n'));
  }

  $.getJSON("./public/xkcd_de.json", function (data) {
    var jsonData = data.words;
    outputPW(jsonData);
    $(".generate").click(function () {
      outputPW(jsonData);
    });
    $(".generate").removeClass('hidden');
  });
});
