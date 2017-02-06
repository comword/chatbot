$("#inputUsername").keydown(function (event) {
  var code = event.keyCode || event.which;
  if (code == "13") {
    $("#btnLogin").trigger("click");
  }
});
$('#mform').on('keyup keypress', function(e) {
  var keyCode = e.keyCode || e.which;
  if (keyCode === 13) {
    e.preventDefault();
    return false;
  }
});
$("#btnLogin").click(function () {
  var strTxtName = encodeURI($("#inputUsername").val());
//  var strTxtPass = sha1(encodeURI($("#inputPassword").val()));
  var strTxtPass = "";
  $('[id="alerts"]').empty();
  $.ajax({
    url: "login_action.cgi",
    type: 'POST',
    dataType: "html",
    data: { inputUsername: strTxtName, inputPassword: strTxtPass },
    success: function (strValue) {
      if (strValue == "Wrong username.")
      {
        $('[id="alerts"]').append('<div class="alert alert-danger fade in"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong>Error!</strong>The username does not exist in system.</div>');
        return true;
      }
      window.location.href = strValue;
    }
  });
});
