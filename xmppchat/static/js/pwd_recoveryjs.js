//#region click event
$('#pwdRecovery-form-button').click(function(event){
    removePreviousErrorMsgs()
    event.preventDefault()
    var form = $('#pwdRecovery-form');
    var url = window.location.href
    console.log(url)
    var type = form.prop('method');
    
    var form_data = {
        password: document.getElementById("password").value,
        confirmed_password: document.getElementById("confirmPassword").value
    }

    if ((checkFormIsFilled(form_data) && formIsValid(form_data)) == true)
    {
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
function checkFormIsFilled(form_data)
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
function formIsValid(form_data)
{
    if(!form_data.hasOwnProperty("password") && !form_data.hasOwnProperty("confirmPassword"))
    {
        return false
    }

    var passwdError = validatePassword(form_data.password, "password")
    var confirmPasswdError = validateConfirm(form_data.password, form_data.confirmed_password, "confirmPassword")

    return passwdError && confirmPasswdError
}
function validatePassword(passwd, id_key)
{
    if(passwd.length < 8)
    {
        var item = document.getElementById(id_key)
        item.className += " is-invalid"
        var error_item = document.getElementById(id_key+"-invalid")
        error_item.innerText = "Password length has to be at least 8. Please try again."
        return false
    }
    return true
}

function validateConfirm(password, confirmPassword, id_key)
{
    if(password != confirmPassword)
    {
        var item = document.getElementById(id_key)
        item.className += " is-invalid"
        var error_item = document.getElementById(id_key+"-invalid")
        error_item.innerText = "Passwords has to be the same. Please try again."
        return false
    }
    return true
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
            pwdrecoverymsg("fa-check","green","Now you can sign in with your new passeord!")
        },
        error: function(data) {//console.log("error. see details below.");
            data = data.responseJSON
            printMessageWithCategory("Upps!", data.feedback, data.category);
        },
    }).done(function() {});
};


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

function removePreviousErrorMsgs()
{
    $("#password-invalid").text("")
    $("#confirmPassword-invalid").text("")
    $('#password').removeClass('is-invalid');
    $('#confirmPassword').removeClass('is-invalid');
}
//#endregion

