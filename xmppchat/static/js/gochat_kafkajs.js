//#region Variables and other attributes without HTML container 
var user_name = $('#NameOnlineAvatar').text()
chat_messages = {}
chat_messages[user_name] = {}
var ownMsg
var firstContact = true
//#endregion

//#region get messages DESCRIPTION:
/*
    The region get messages has functions to look for messages on an eventstream, print them to the window or to the preview
    Functions: 
        getMessage, checkSameChatMessages, fillInContactPeers, updatePreview
*/
//#region functions:
var source = new EventSource('/kafkastream/');
source.onmessage = function (event) {
    var result = event.data
    console.log(result)
    result = result.split("data: ").join("");
    var empfangenMsg = JSON.parse(result);
    console.log(empfangenMsg);
    getMessage(empfangenMsg)    
};
function getMessage (empfangenMsg) {
    ownMsg = false
    var from = empfangenMsg.from
    if (from == user_name) {
        // Die Nachricht kam von mir und ging an jemand anderen
        from = empfangenMsg.to
        ownMsg = true
    }
    if (!(from in chat_messages[user_name])) {
        //checkNewContact(from, empfangenMsg.type)
        // Den Contact gibt es noch nicht
        if(!(ownMsg)){
            console.log(`Der Kontaktpartner ${from} wurde noch ned gefunden`)
            chat_messages[user_name][from]= [{"from":from,"timestamp":empfangenMsg.timestamp, "txt":empfangenMsg.msg, "type": "chat"}]
            
        } else {
            chat_messages[user_name][from] = [{"from":user_name,"timestamp":empfangenMsg.timestamp, "txt":empfangenMsg.msg, "type": "chat"}]
        }
        fillInContactPeers(from, empfangenMsg.msg, ownMsg)
        fill_in_chat_msgs_single_chat(user_name, from);
        return        
    }
    //Der Kontakt befindet sich in der Liste
    checkSameChatMessages(user_name,from,empfangenMsg.timestamp,empfangenMsg.msg, ownMsg, empfangenMsg.type)
    
    
    console.log(chat_messages)
}
function checkSameChatMessages (user_name, from, timestamp, msg, ownMsg, type) {
    findSame = false
    for (let index = 0; index < chat_messages[user_name][from].length; index++) {
        // Unterschiedlicher Sender aber bereits in der Liste
        if (((chat_messages[user_name][from][index].txt == msg) && (chat_messages[user_name][from][index].timestamp == timestamp))) {
            findSame = true
        }
    }
    if (!findSame) {
        if (!ownMsg) {
            chat_messages[user_name][from].push({"from": from, "timestamp": timestamp, "txt": msg, "type": "chat"});
        } else {
            chat_messages[user_name][from].push({"from": user_name, "timestamp": timestamp, "txt": msg, "type": "chat"}); 
        }
        fillInContactPeers(from, msg, ownMsg)
        printSingleChatMessage(type, from, msg, timestamp, ownMsg)
    }
}
function fillInContactPeers(from, msg, ownMsg)
{
    var findContact = false
    var contact_ul = $("#contacts_list");
    var contacts = contact_ul.children()
    msg = msg.slice(0,60)
    for (let i = 0; i < contacts.length; i++) {
        if(contacts[i].getElementsByTagName("p")[0].innerText == from) {
            findContact = true
            updatePreview(contacts[i],msg,ownMsg)
            return
        } 
    }
    if (!ownMsg) {
        contact_ul.append(`
            <li class="contact" id="${from}">
                <div class="wrap">
                    <img src="/static/img/usericon2.png" alt="Avatar">
                    <div class="meta">
                    <p class="name">${from}</p>
                    <p class="preview">${msg}</p>
                    </div>
                </div>
                </li>`);
    } else {
        msg = "<span>You:</span> " + msg;
        contact_ul.append(`
            <li class="contact" id="${from}">
                <div class="wrap">
                    <img src="/static/img/usericon2.png" alt="Avatar">
                    <div class="meta">
                    <p class="name">${from}</p>
                    <p class="preview">${msg}</p>
                    </div>
                </div>
                </li>`);
    } 
    if (firstContact) {
        getFirstContactactive()
    }
    firstContact = false
}
function updatePreview(contact, msg, ownMsg) {
    msg = msg.slice(0,60)
    if(ownMsg){
        msg = "<span>You:</span> " + msg;
        contact.getElementsByTagName("p")[1].innerHTML = msg
        return
    }
    contact.getElementsByTagName("p")[1].innerHTML = msg    
}
function checkNewContact(from, msg_type) {
    if(!(msg_type == "roster_agreement_required"))
    {
        return;
    }
    $("#acceptContactModal").modal("show")
    $('#acceptContact').append(`<p>${from}</p><p>Hey I want to be your friend</p>`);
}
//#endregion
//#endregion

//#region send messages DESCRIPTION:
/*
    Region has functions to send messages and the attributes which they need
    Functions: 
        send_message, getSendingInformations, updateChatwindowOnSending, clearInputFieldOnSending, updateChatMessageObject
*/
//#region functions:
$('#send-submit-button').click(function(event){
    var informations = getSendingInformations()
    if(!informations){return}
    var sending_informations = {"to":informations.to, "from":informations.from, "msg_subject":informations.msg_subject, "msg_body":informations.msg_body,"msg_type":"chat"}
    var update_data =  {"to":informations.to,"from":informations.from, "msg_body":informations.msg_body, "msg_timestamp":informations.msg_timestamp}
    console.log(sending_informations)
    send_message(sending_informations);
    updateChatMessageObject(update_data, informations)
    updateChatwindowOnSending(informations.msg_body, informations.msg_timestamp)
    clearInputFieldOnSending()
});
function getSendingInformations(){
    var informations = {}
    var msg = $('#input-message').val().trim();
    if (msg == "") {
        return false;
    }
    var to = $('.contact.active').attr("id");
    var user_name = $('#NameOnlineAvatar').text();
    var dt = new Date();
    var msg_timestamp = dt.toISOString().split("T")[0] + " " + dt.toLocaleTimeString().substring(0,5);
    informations = {"to":to, "from":user_name, "msg_subject":"", "msg_body":msg,"msg_type":"chat", "msg_timestamp":msg_timestamp}
    return informations
}
//request to the server for sending message
function send_message(sending_data)
{
    $.ajax({
        url: "/send_message",
        type: "POST",
        data: JSON.stringify(sending_data),
        processData: false,
        dataType: "json",
        contentType: "application/json",
        error: function(data) {
            data = data.responseJSON
            console.log(data)
        },
    });
}
// make bubble for own msg
function updateChatwindowOnSending(msg, msg_timestamp) {
    print_msg = msg.replace(/(?:\r\n|\r|\n)/g, '<br>');
    $('#chat-list').append(`<li><div class="message-float-left">
    <div class="message-data">
      <span class="message-data-name"><i class="fa fa-circle you"></i>You</span>
    </div>
    <div class="message you-message">${print_msg}
      <div class="timestamp-left">
        <p>${msg_timestamp}</p>
      </div></div></div></li>`);
}
function clearInputFieldOnSending() {
    $('#input-message').val("");
    $('.emojionearea-editor').text(''); 
    var objDiv = document.getElementById("messages-container");
    objDiv.scrollTop = objDiv.scrollHeight;
}
function updateChatMessageObject(update_data) {
    user_name = update_data.from
    to = update_data.to
    msg_timestamp = update_data.msg_timestamp
    msg_txt = update_data.msg_body
    msg = msg_txt.replace(/(?:\r\n|\r|\n)/g, '<br>');
    //update chat_msgs object
    chat_messages[user_name][to].push({"from": user_name, "timestamp": msg_timestamp, "txt": msg, "type": "chat"});
    updateLastMessageInContactView(user_name, user_name, to, msg_txt);
}
//#endregion
//#endregion

//#region Login and the first important actions
// Get first contact active
function getFirstContactactive(){
    var ul_tag, li
    $(".contact.active").removeClass('active');
    ul_tag = document.getElementById('contacts_list');
    li = ul_tag.getElementsByTagName("li")[0];
    $(li).addClass("active")
    firstactiveContact(li);  
}
// To make the mainWindow to the active contact 
function firstactiveContact(li) {
    var name = li.getElementsByTagName('p')[0].innerHTML
    var contactImageSrc = li.getElementsByTagName('img')[0].src
    $(".contact-profile").children()[1].innerHTML = name;
    $(".contact-profile").children()[0].src = contactImageSrc;
    document.getElementById("send-submit-button").disabled = false; 
}
//#endregion

//#region functions for multiusing
function updateLastMessageInContactView(user_name, peer_name, update_id, message_string)
{
  if (user_name == peer_name)
  {
    message_string = "<span>You:</span> " + message_string;
  }
  message_string = message_string.slice(0,50)
  var li_contact = $('#' + update_id).html(`
  <div class="wrap">
            <img src="/static/img/usericon2.png" alt="Avatar">
            <div class="meta">
              <p class="name">${update_id}</p>
              <p class="preview">${message_string}</p>
            </div>
          </div>
  `);
}
function fill_in_chat_msgs_single_chat(user_name, peer_name)
{
    var contactAtwindow = $(".contact-profile").children()[1].innerText
    if (peer_name != contactAtwindow) {
        return
    }
    $('#chat-list').empty();
    for (var i=0; i<chat_messages[user_name][peer_name].length; i++ )
    {
        var msg_timestamp = chat_messages[user_name][peer_name][i].timestamp;
        if (chat_messages[user_name][peer_name][i].from == user_name)
        {
            $('#chat-list').append(`
            <li><div class="message-float-left">
                <div class="message-data">
                    <span class="message-data-name"><i class="fa fa-circle you"></i>You</span>
                </div>
                <div class="message you-message">${chat_messages[user_name][peer_name][i].txt}
                    <div class="timestamp-left">
                    <p>${msg_timestamp}</p>
                    </div></div></div></li>
            `);
        }
        else if(chat_messages[user_name][peer_name][i].from == peer_name)
        {
        $('#chat-list').append(`
        <li class="clearfix">
            <div class="message-data align-right">
            <span class="message-data-name">${peer_name}</span> <i class="fa fa-circle me"></i>
            </div>
            <div class="message me-message float-right">${chat_messages[user_name][peer_name][i].txt}
            <div class="timestamp">
                <p>${msg_timestamp}</p>
            </div>
            </div></li>
            `);
        }

        var objDiv = document.getElementById("messages-container");
        objDiv.scrollTop = objDiv.scrollHeight;
    }
}
function printSingleChatMessage(msg_type, from, msg, msg_timestamp, ownMsg)
{
  if (!(msg_type == "chat" || msg_type == "normal"))
  {
    return;
  }
  if($('.contact.active').attr("id") == from) //print msg only if contact tap of from is active
  {
      if (ownMsg) {
        $('#chat-list').append(`
            <li><div class="message-float-left">
                <div class="message-data">
                    <span class="message-data-name"><i class="fa fa-circle you"></i>You</span>
                </div>
                <div class="message you-message">${msg}
                    <div class="timestamp-left">
                    <p>${msg_timestamp}</p>
                    </div></div></div></li>
            `);
        } else {
        $('#chat-list').append(`<li class="clearfix">
            <div class="message-data align-right">
            <span class="message-data-name">${from}</span> <i class="fa fa-circle me"></i>
            </div>
            <div class="message me-message float-right">${msg}
            <div class="timestamp">
                <p>${msg_timestamp}</p>
            </div>
            </div></li>`);
        }
        var objDiv = document.getElementById("messages-container");
        objDiv.scrollTop = objDiv.scrollHeight;
        
  }
}
//#endregion

//#region functions to react on dynamic changes of classes
$(document).ready( function () {
    // Change active contact by click
    $( document). on('click', ".contact" ,function() {
      // Clear Search-field by click on a contact
      if (($("#filterContacts").val().length != 0)) {
        document.getElementById('filterContacts').value = '';
        clearfilter();
      }
      $(".contact.active").removeClass('active');
      $(this).toggleClass('contact');
      $(this).toggleClass('contact active');
      var name = this.getElementsByTagName('p')[0].innerHTML
      var contactImageSrc = this.getElementsByTagName('img')[0].src
      $(".contact-profile").children()[1].innerHTML = name;
      $(".contact-profile").children()[0].src = contactImageSrc;
  
      var peer_name = $(".contact-profile").children()[1].innerHTML
      fill_in_chat_msgs_single_chat($('#NameOnlineAvatar').text(), peer_name);
  
     });  
  });
//#endregion

//#region Filter DESCRIPTION:
/*
    The region implement the Filter functions
    Functions:
        A function on ready, cleafilter
*/
//#region 
// Filter for contacts
$(document).ready(function(){
    $("#filterContacts").on("keyup", function() {
      var filtervalue, ul_tag, li, index;
      filtervalue = $(this).val().toLowerCase();
      ul_tag = document.getElementById('contacts_list');
      li = ul_tag.getElementsByTagName("li");
      for (index = 0; index < li.length; index++) {
        contactname = li[index].getElementsByTagName("p")[0].innerHTML;
        if (contactname.toLowerCase().indexOf(filtervalue) > -1) {
          li[index].style.display = "";
        } else {
          li[index].style.display = "none";
        }
      }
    });
  });
  //Clear Filter
  function clearfilter()  {
      var ul_tag, li, index;
      ul_tag = document.getElementById('contacts_list');
      li = ul_tag.getElementsByTagName("li");
      for (index = 0; index < li.length; index++) {
          li[index].style.display = "";
        }
      };
//#endregion
//#endregion

//#region Add new Contact DESCRIPTION:
/*
      Functions to add a new contact. We need a request. We have to check that the name is valid.accordion
      Functions: 
        Modal-Functions, checkletters(name, letters, checkexisting(name), checkOwnName(name), requestToServer (contactName), addContactToList(name, preview_message)
    
*/
//#region Functions:
// Schließen des Kontakt-Hinzufügen Fensters
$('#closeModalButton').click(function(){
    $('#addContactInput').val("");
    $('#addContactInput').removeClass('is-invalid');
    var error_item = document.getElementById("addContactInput-invalid");
    error_item.innerText = "";
});

$("#addContactButton").click(function(){
    var addContactName = $("#addContactInput").val().trim();
    $("#addContactInput").val("")
    var lettercheck, contactexists, ownName
    var valid = true
    var letters = /^[a-z]+[0-9]*$/;

    lettercheck = checkletters(addContactName, letters)
    contactexists = checkexisting(addContactName)
    ownName = checkOwnName(addContactName)
    
    if (lettercheck && contactexists && ownName) {
        requestToServer (addContactName)
    }
}); 

function checkletters(name, letters){
    if(!name.match(letters))
    {
        $('#addContactInput').addClass('is-invalid');
        var error_item = document.getElementById("addContactInput-invalid");
        error_item.innerText = "username contains invalid characters. Try again!";
        return false;
    }
    return true
}

function checkexisting(name){
    if(name in chat_messages[$('#NameOnlineAvatar').text()])
    {
        $('#addContactInput').addClass('is-invalid');
        var error_item = document.getElementById("addContactInput-invalid");
        error_item.innerText = "username does already exist in your contacts list.";
        return false;
    }
    return true
}

function checkOwnName(name){
    if(name == $('#NameOnlineAvatar').text())
    {
        $('#addContactInput').addClass('is-invalid');
        var error_item = document.getElementById("addContactInput-invalid");
        error_item.innerText = "you cannot write with yourself. Try again!";
        return false;
    }
    return true
}

function requestToServer (contactName){
    var post_data = {"username": contactName, "requested_platform":"kafka"};
    $.ajax({
    url: "/add_contact", 
    type: "post",
    data: JSON.stringify(post_data),
    processData: false,
    dataType: "json",
    contentType: "application/json",
    success: function(response_data){
        addContactToList(contactName, "");
        chat_messages[$('#NameOnlineAvatar').text()][contactName] = [];
        console.log(chat_messages)
        $("#staticBackdrop").modal('hide');
        sendNewContact(contactName)
        document.getElementById("send-submit-button").disabled = false;     
    },
    error: function(error_data){
        console.log(error_data.responseJSON);
        $('#addContactInput').addClass('is-invalid');
        var error_item = document.getElementById("addContactInput-invalid");
        error_item.innerText = error_data.responseJSON.feedback;
        }
    });
}

function addContactToList(name, preview_message)
{
    var contact_ul = $('#contacts_list');
    contact_ul.append(`
    <li class="contact" id="${name}">
          <div class="wrap">
            <img src="/static/img/usericon2.png" alt="Avatar">
            <div class="meta">
              <p class="name">${name}</p>
              <p class="preview">${preview_message}</p>
            </div>
          </div>
        </li>`);
    li_list = contact_ul.children()
    lastContact = li_list[contact_ul.children().length -1]
    $(".contact.active").removeClass('active');
    $(lastContact).addClass("active")
    firstactiveContact(lastContact)
}

function sendNewContact(contactName){
    var sending_informations = {"to":contactName, "from":user_name, "msg_subject":"", "msg_body":"Now You are my friend!!","msg_type":"chat"}
    var dt = new Date();
    var msg_timestamp = dt.toISOString().split("T")[0] + " " + dt.toLocaleTimeString().substring(0,5);
    send_message(sending_informations)
    chat_messages[user_name][contactName].push({"from": user_name, "timestamp": msg_timestamp, "txt": sending_informations.msg_body, "type": "chat"});
    updateLastMessageInContactView(user_name, user_name, contactName, sending_informations.msg_body)
    fill_in_chat_msgs_single_chat(user_name, contactName)
}
//#endregion
//#endregion

//#region Emoji
$(document).ready( function() {
$("#input-message").emojioneArea({ events: { keydown: function (editor, event) { 
    var length = this.getText().length;
    if (length >= 250 && event.which != 8) 
    { 
        event.preventDefault(); 
        document.getElementById("send-submit-button").disabled = true; 
        document.getElementById("alertFormaxlength").style.display = "block"
        }
    if (length < 250) 
    {
        document.getElementById("alertFormaxlength").style.display = "none"
        document.getElementById("send-submit-button").disabled = false; 
    }
} }} );
});
//#endregion

//#region Link to Privacy Policy
//PrivacyPolicy
$("#PrivacyPolicy").click(function() {
    window.location.href = "/privacy_policy";
});  
//#endregion

//#region Contactprofile
//Profile
$("#profileDd").click(function() {
    var user_name = $('#NameOnlineAvatar').text()
    var chatpartner = $(".contact-profile").children()[1].innerHTML
    if(chatpartner == "No Contact"){
      return
    }
    $("#ContactProfileModal").modal("show")
    var timestamp = chat_messages[user_name][chatpartner][0].timestamp
    var messageCounter = chat_messages[user_name][chatpartner].length
    $('#ContactProfileLabel').append(`<p>${chatpartner}</p>`);
    $('#ContactProfile').append(`
      <p>Statistics:</p>
      <div class="d-flex justify-content-center">
        <p>Kontakt hinzugefügt am: ${timestamp}<br>
        Anzahl an Nachrichten : ${messageCounter}</p>
      </div
      `);
  });
  //Profile
  $("#closeContactProfileButton").click(function() {
    document.getElementById("ContactProfile").innerText = ""
    document.getElementById("ContactProfileLabel").innerText = ""
  });
//#endregion

//#region disable Send-Button
$(document).ready( function() {
    document.getElementById("send-submit-button").disabled = true; 
});
//#endregion


