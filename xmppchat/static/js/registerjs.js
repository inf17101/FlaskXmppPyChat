$('#register-form-button').click(function(event){
    event.preventDefault()
    var form = $('#register-form');
    var url = form.prop('action');
    var type = form.prop('method');
    var form_data = {
        username: document.getElementById("username").value.toLowerCase(),
        eMail: document.getElementById("eMail").value,
        password: document.getElementById("password").value,
        confirmPassword: document.getElementById("confirmPassword").value
    }

    removePreviousErrorMsgs();

    if((checkFormIsFilled(form_data) && formIsValid(form_data)) == true)
    {
        //console.log("form is valid")
        document.getElementById("username").value = ""
        document.getElementById("eMail").value = ""
        document.getElementById("password").value = ""
        document.getElementById("confirmPassword").value = ""

        $("#loaderContentbox").attr("style", "display:flex;");
        $("#formularContent").attr("style", "display:none;");
        modular_ajax(url, type, form_data)
    }

});

function checkFormIsFilled(form_data)
{
    var valid = true
   for(const [key, value] of Object.entries(form_data))
   {
       if(!$.trim(value))
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

function removePreviousErrorMsgs()
{
    $("#form-response").text("")
    $("#username-invalid").text("")
    $("#eMail-invalid").text("")
    $("#password-invalid").text("")
    $("#confirmPassword-invalid").text("")
}


function formIsValid(form_data)
{
    //var form_error = false
    if(!form_data.hasOwnProperty("username") && !form_data.hasOwnProperty("eMail") && !form_data.hasOwnProperty("password") && !form_data.hasOwnProperty("confirmPassword"))
    {
        return false
    }

    var usernameError = validateUsername(form_data.username, "username")
    var emailError = validateEmail(form_data.eMail, "eMail")
    var passwdError = validatePassword(form_data.password, "password")
    var confirmPasswdError = validateConfirm(form_data.password, form_data.confirmPassword, "confirmPassword")
    //console.log(emailError && passwdError && confirmPasswdError)
    return usernameError && emailError && passwdError && confirmPasswdError
}

function validateUsername(username, id_key){
    var re = /^[A-Za-z]+[0-9]*$/;
    if(!username.match(re))
    {
        var item = document.getElementById(id_key)
        item.className += " is-invalid"
        var error_item = document.getElementById(id_key+"-invalid")
        error_item.innerText = "Invalid username. The username have to start with a letter. Please try again."
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
        },
        error: function(data) {//console.log("error. see details below.");
            $("#loaderContentbox").attr("style", "display:none!important;");
            $("#formularContent").attr("style", "display:;");
            data = data.responseJSON
            printMessageWithCategory("Upps!", data.feedback, data.category);
        },
    }).done(function() {
        $("#loaderContentbox").attr("style", "display:none!important;");
        $("#formularContent").attr("style", "display:;");
        $(".content-section").html('<div class="modal" tabindex="-1" role="dialog" style="margin-top: 10%"> \
    <div class="modal-dialog" role="document"> \
      <div class="modal-content"> \
        <div class="modal-header"> \
          <h5 class="modal-title">Registration Success</h5> \
        </div> \
        <div class="modal-body"> \
        <i class="fa fa-check fa-2x" style="float: right; color: green; display: inline-block; border-radius: 50%; border: 5px solid green; padding: 20px;"></i> \
          <p style="margin-top: 30px">Thank you for creating an account!</p> \
        </div> \
        <div class="modal-footer"> \
          <button id="goToSignInButton" type="button" class="btn btn-primary">Sign In</button> \
        </div> \
      </div> \
    </div> \
  </div>')
  $(".modal").show()
    document.getElementById("goToSignInButton").onclick = function () {
        location.href = "/login";
    };
    });
};


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