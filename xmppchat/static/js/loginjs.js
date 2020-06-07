//#region click event
$('#login-form-button').click(function(event){
    event.preventDefault()
    var form = $('#login-form');
    var url = form.prop('action');
    var type = form.prop('method');
    if (document.getElementById("formXmpp").checked) {
        radio = "xmpp"
    } else {
        radio = "kafka"
    }
    var form_data = {
        username: document.getElementById("username").value,
        password: document.getElementById("password").value,
        remember: document.getElementById("formRememberCheck").checked,
        requested_platform: radio
    }

    if (checkformIsFilled(form_data))
    {
        $("#loaderContentbox").attr("style", "display:flex;");
        $("#formularContent").attr("style", "display:none;");
        modular_ajax(url, type, form_data);
    }
});
//#endregion

//#region msg for user
function printMessageWithCategory(msg_title, msg_body, category)
{
    if (category != "success" || category != "warning" || category != "danger")
    {
        $('#form-response').html(`<div class="alert alert-${category}" role="alert">\
    <h4 class="alert-heading">${msg_title}</h4>\
    <p>Invalid argument exception: expected category like [success, warning, danger].</p><hr>`)
    }
    $('#form-response').html(`<div class="alert alert-${category}" role="alert"><h4 class="alert-heading">${msg_title}</h4><p>${msg_body}</p><hr>`)
}
//#endregion

//#region check the form
function checkformIsFilled(form_data)
{
    var valid = true
    for(const [key, value] of Object.entries(form_data))
    {
        if (!$.trim(value) && key != "remember")
        {
            var item = document.getElementById(key)
            item.className += (" is-invalid")
            var error_item = document.getElementById(key + "-invalid")
            error_item.innerText = "Input required! Please enter a proper value."
            valid = false
        }
    }
    return valid
}
//#endregion

//#region request to server
function modular_ajax(url, type, formData) {
    // Most simple modular AJAX building block
    var csrftoken = $('meta[name=csrf-token]').attr('content')
    $.ajax({
        url: url,
        type: type,
        data: JSON.stringify(formData),
        processData: false,
        headers: { "X-CSRF-Token": csrftoken },
        dataType: "json",
        contentType: "application/json",
        beforeSend: function() {
        },
        complete: function () {
        },
        success: function ( data ){
           
            if ( !$.trim( data.feedback )) { // response from Flask is empty
                printMessageWithCategory("Error appeared!", "Empty response of server.", "danger");
            }
            location.href = "/gochat"
        },
        error: function(data) {//console.log("error. see details below.");
            $("#loaderContentbox").attr("style", "display:none!important;");
            $("#formularContent").attr("style", "display:;");
            data = data.responseJSON
            printMessageWithCategory("Upps!", data.feedback, data.category);
        },
    }).done(function() {});
};
//#endregion

//#region PasswordModal
//password
$("#forgotpwd").click(function() {
    $("#PasswordModal").modal("show")
});
//#endregion

//#region ForgotPassword
$("#NewPasswordButton").click(function() {
    removePreviousErrorMsgs()
    var usernamecheck, emailcheck
    username = $("#UsernameInput").val().trim()
    email = $("#EMailInput").val().trim()
    console.log(username)
    console.log(email)
    usernamecheck = usernameValidation(username, "UsernameInput")
    emailcheck = validateEmail(email, "EMailInput")

    if(usernamecheck && emailcheck){
        requestToServer(username,email)
    }

});
function usernameValidation(username, id_key){
    var re = /^[a-z]+[0-9]*$/;
    if(!username.match(re))
    {
        var item = document.getElementById(id_key)
        item.className += " is-invalid"
        var error_item = document.getElementById(id_key+"-invalid")
        error_item.innerText = "Invalid username. Special characters and capital letters are not allowed. Please try again."
        return false
    }
    return true
}
function validateEmail(email, id_key) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if(re.test(String(email).toLowerCase()) == false)
    {
        var item = document.getElementById(id_key)
        item.className += " is-invalid"
        var error_item = document.getElementById(id_key+"-invalid")
        error_item.innerText = "Invalid e-mail address. Please try again."
        return false
    }
    return true
}
function removePreviousErrorMsgs()
{
    $("#UsernameInput-invalid").text("")
    $("#EMailInput-invalid").text("")
    $('#UsernameInput').removeClass('is-invalid');
    $('#EMailInput').removeClass('is-invalid');
}
$("#closePasswordModalButton").click(function() {
    removePreviousErrorMsgs()
    document.getElementById("UsernameInput").value = ""
    document.getElementById("EMailInput").value = ""
}); 

function requestToServer (username, email){
    var post_data = {"username": username, "email":email};
    $.ajax({
    url: "/request_reset",
    type: "post",
    data: JSON.stringify(post_data),
    processData: false,
    dataType: "json",
    contentType: "application/json",
    success: function(response_data){
        pwdrecoverymsg("fa-check","green","Please look for a mail!")
    },
    error: function(error_data){
        pwdrecoverymsg("fa-times","red","Something goes wrong. Please try again!")
    } 
    });
}


function pwdrecoverymsg (iconclass, colour, msg){
    $("#PasswordModal").modal("hide")
    $(".content-section").html(`<div class="modal" tabindex="-1" role="dialog" style="margin-top: 10%"> \
    <div class="modal-dialog" role="document"> \
      <div class="modal-content"> \
        <div class="modal-header"> \
          <h5 class="modal-title">Password Recovery</h5> \
        </div> \
        <div class="modal-body"> \
        <i class="fa ${iconclass} fa-2x" style="float: right; color: ${colour}; display: inline-block; border-radius: 50%; border: 5px solid ${colour}; padding: 20px;"></i> \
          <p style="margin-top: 30px">${msg}</p> \
        </div> \
        <div class="modal-footer"> \
          <button id="goToSignInButton" type="button" class="btn btn-primary">Sign In</button> \
        </div> \
      </div> \
    </div> \
  </div>`)
  $(".modal").show()
    document.getElementById("goToSignInButton").onclick = function () {
        location.href = "/login";
    };
}
//#endregion
