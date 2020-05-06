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