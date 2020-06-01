//#region Variables and functions without HTML-Content
$("#loaderContentbox").attr("style", "display:flex;");
var chat_messages = {};
pull_chat_hisotry($('#NameOnlineAvatar').text());
var source = new EventSource('/stream'); 
//#endregion

//#region chat-history 
function pull_chat_hisotry(username)
{
  var URL = "/get_chathistory";
  const post_data = {"username": username};
  $.ajax({url: URL, type: "post",
    data: JSON.stringify(post_data),
    processData: false,
    dataType: "json",
    contentType: "application/json",
    success: function(response_data){
      chat_messages = response_data;
      console.log(chat_messages)
      fillInContactPeers();
  },
    error: function(error_data){
      console.log(error_data.responseJSON);
    }
  });
}
function fillInContactPeers()
{
  var contact_ul = $("#contacts_list");
  var user_name = $('#NameOnlineAvatar').text();
  for (const peer of Object.keys(chat_messages[user_name]))
  {
    var position_last_message_object = chat_messages[user_name][peer].length - 1;
    var last_message_dict = chat_messages[user_name][peer][position_last_message_object];
    var message_string = last_message_dict.txt;
    if (last_message_dict.from == user_name)
    {
      message_string = "<span>You:</span> " + message_string;
    }
    
    contact_ul.append(`
    <li class="contact" id="${peer}">
          <div class="wrap">
            <img src="/static/img/usericon2.png" alt="Avatar">
            <div class="meta">
              <p class="name">${peer}</p>
              <p class="preview">${message_string}</p>
            </div>
          </div>
        </li>`);
  }
  $("#loaderContentbox").attr("style", "display:none!important;");
}
//#endregion

//#region get messages DESCRIPTION:
/*
    The region get messages, has functions to look for messages on an eventstream, print them to the window or to the preview
    Functions: 
       source.onmessage, printSingleChatMessage(), newContact()
*/
//#region 
//begin event stream for chat messages  
source.onmessage = function (event) {
  var result = event.data
  console.log(result)
 if ($.trim(result) != "1")
 {
   result = result.split("data: ").join("");
   var json_obj = JSON.parse(result);
   console.log(json_obj);
   printSingleChatMessage(json_obj);
 }
};
function printSingleChatMessage(JSON_DATA)
{
    var from = JSON_DATA.from.split("@")[0];
    var msg_timestamp = JSON_DATA.timestamp;
    var msg = JSON_DATA.msg;
    var msg_type = JSON_DATA.type;
    var user_name = $('#NameOnlineAvatar').text(); 
    if (!(msg_type == "chat" || msg_type == "normal"))
    {
      return;
    }

    if (!(from in chat_messages[user_name])) {
      newContact(user_name, from, msg, msg_timestamp)
      return
    }

    if($('.contact.active').attr("id") == from) //print msg only if contact tap of from is active
    {
        $('#chat-list').append(`<li class="clearfix">
          <div class="message-data align-right">
            <span class="message-data-name">${from}</span> <i class="fa fa-circle me"></i>
          </div>
          <div class="message me-message float-right">${msg}
            <div class="timestamp">
              <p>${msg_timestamp}</p>
            </div>
          </div></li>`);
        var objDiv = document.getElementById("messages-container");
        objDiv.scrollTop = objDiv.scrollHeight;
    }
    
    //update chat_msgs object
    chat_messages[user_name][from].push({"from": from, "timestamp": msg_timestamp, "txt": msg, "type": "chat"});

    updateLastMessageInContactView(user_name, from, from, msg);

}
function newContact(user_name, peer, message_string, timestamp){
  chat_messages[user_name][peer]= [{"from":peer,"timestamp":timestamp, "txt":message_string, "type": "chat"}]
  console.log(chat_messages)
  var contact_ul = $('#contacts_list');
  contact_ul.append(`
    <li class="contact" id="${peer}">
          <div class="wrap">
            <img src="/static/img/usericon2.png" alt="Avatar">
            <div class="meta">
              <p class="name">${peer}</p>
              <p class="preview">${message_string}</p>
            </div>
          </div>
        </li>`);
}
//#endregion
//#endregion

//#region send-functions DESCRIPTION:
/*
  The region has functions to send messgaes if the Send-Button was clicked
  Functions:
    onclick-Function, send_msg_single_chat()
*/
//#region Functions:
$('#send-submit-button').click(function(event){
  send_msg_single_chat();
});
function send_msg_single_chat()
{
  var msg = $('#input-message').val().trim();
  if (msg == "") {
    return;
  }
  console.log(msg)
  var to = $('.contact.active').attr("id");
  var user_name = $('#NameOnlineAvatar').text();
  var dt = new Date();
  var timestampdetails = dt.toISOString().split("T")[0] + " " + dt.toLocaleTimeString().substring(0,8); // replace all . with - in date and concate with time hours:min
  msg_timestamp = timestampdetails.slice(0,timestampdetails.length-3)
  if(!to in Object.keys(chat_messages[user_name]))
  {
    throw new Error("to is not a valid recipient.");
  }
  modular_ajax("/send_message", "post", {"to": to, "from": user_name, "msg_subject": "", "msg_body": msg, "msg_type": "chat"});
  print_msg = msg.replace(/(?:\r\n|\r|\n)/g, '<br>');
  $('#chat-list').append(`<li><div class="message-float-left">
              <div class="message-data">
                <span class="message-data-name"><i class="fa fa-circle you"></i>You</span>
              </div>
              <div class="message you-message">${print_msg}
                <div class="timestamp-left">
                  <p>${msg_timestamp}</p>
                </div></div></div></li>`);

  $('#input-message').val("");

  $('.emojionearea-editor').text(''); 

  var objDiv = document.getElementById("messages-container");
  objDiv.scrollTop = objDiv.scrollHeight;

  //update chat_msgs object
  chat_messages[user_name][to].push({"from": user_name, "timestamp": timestampdetails, "txt": msg, "type": "chat"});

  updateLastMessageInContactView(user_name, user_name, to, msg);
  console.log(chat_messages)
}
//#endregion
//#endregion

//#region functions for multiusing
function updateLastMessageInContactView(user_name, peer_name, update_id, message_string)
{
  if (user_name == peer_name)
  {
    message_string = "<span>You:</span> " + message_string;
  }
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
  $('#chat-list').empty();
  for (var i=0; i<chat_messages[user_name][peer_name].length; i++ )
  {
    var msg_timestamp = chat_messages[user_name][peer_name][i].timestamp;  
    if(msg_timestamp.length > 16)
    {
      msg_timestamp = msg_timestamp.slice(0, msg_timestamp.length-3)
    }
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
function modular_ajax(url, type, formData) {
  // Most simple modular AJAX building block
  $.ajax({
      url: url,
      type: type,
      data: JSON.stringify(formData),
      processData: false,
      dataType: "json",
      contentType: "application/json",
      error: function(data) {//console.log("error. see details below.");
          data = data.responseJSON
          printMessageWithCategory("Upps!", data.feedback, data.category);
      },
  });
};
//#endregion

//#region First Login and first Contact acitve
// to set first contact acitve after login
$(document).ready( function() {
  document.getElementById("send-submit-button").disabled = true; 
  var stopIntervall 
  stopIntervall = setInterval(function() {
    checkExistingofElement(stopIntervall)
  }, 1000);
});
// to Check if one contact is exisiting
function checkExistingofElement(stopIntervall){
  $('#contacts_list').each(function(){
      if($(this).children().length > 0){
        filterFirstContact()
        clearInterval(stopIntervall);
      }
  });
}
// To find first Contact to use them for function "firstActiveContact"
function filterFirstContact(){
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
  //var contactImageSrc = li.getElementsByTagName('img')[0].src
  $(".contact-profile").children()[1].innerHTML = name;
  $(".contact-profile").children()[0].src = "/static/img/usericon2.png";
  document.getElementById("send-submit-button").disabled = false; 

  var peer_name = $(".contact-profile").children()[1].innerHTML
  fill_in_chat_msgs_single_chat($('#NameOnlineAvatar').text(), peer_name);
}
//#endregion

//#region Add new Contact DESCRIPTION:
/*
      Functions to add a new contact. We need a request. We have to check that the name is valid.accordion
      Functions: 
        Modal-Functions
*/
//#region Functions:
// to clear inout by closeButton
$('#closeModalButton').click(function(){
  $('#addContactInput').val("");
  $('#addContactInput').removeClass('is-invalid');
  var error_item = document.getElementById("addContactInput-invalid");
  error_item.innerText = "";
});
// function of inout Button to add contacts
$("#addContactButton").click(function(){
  var addContactName = $("#addContactInput").val().trim();
  $("#addContactInput").val("")

  var letters = /^[a-z]+[0-9]*$/;

  if(!addContactName.match(letters)) //check name
  {
    $('#addContactInput').addClass('is-invalid');
    var error_item = document.getElementById("addContactInput-invalid");
    error_item.innerText = "username contains invalid characters. Try again!";
    return false;
  }

  if(addContactName in chat_messages[$('#NameOnlineAvatar').text()])
  {
    $('#addContactInput').addClass('is-invalid');
    var error_item = document.getElementById("addContactInput-invalid");
    error_item.innerText = "username does already exist in your contacts list.";
    return false;
  }

  if(addContactName == $('#NameOnlineAvatar').text())
  {
    $('#addContactInput').addClass('is-invalid');
    var error_item = document.getElementById("addContactInput-invalid");
    error_item.innerText = "you cannot write with yourself. Try again!";
    return false;
  }

  // post request etc.
  var post_data = {"username": addContactName, "requested_platform":"xmpp"};
  $.ajax({url: "/add_contact", type: "post",
  data: JSON.stringify(post_data),
  processData: false,
  dataType: "json",
  contentType: "application/json",
  success: function(response_data){
    $("#staticBackdrop").modal('hide');
    user_name = $('#NameOnlineAvatar').text()
    chat_messages[user_name][addContactName] = [];
    var msg = "Now YOU are my friend"
    modular_ajax("/send_message", "post", {"to": addContactName, "from": user_name, "msg_subject": "", "msg_body": msg, "msg_type": "chat"});
    var dt = new Date();
    var msg_timestamp = dt.toISOString().split("T")[0] + " " + dt.toLocaleTimeString().substring(0,8);
    chat_messages[user_name][addContactName].push({"from": user_name, "timestamp": msg_timestamp, "txt": msg, "type": "chat"}); 
    console.log(chat_messages)
    addContactToList(addContactName, msg);
  },
  error: function(error_data){
    $('#addContactInput').addClass('is-invalid');
    var error_item = document.getElementById("addContactInput-invalid");
    error_item.innerText = error_data.responseJSON.feedback;
    }
  });
    return true;
});
function addContactToList(name, preview_message)
{
  var li_list, lastContact;
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
//#endregion
//#endregion

//#region Emoji
// Bind Emojiarea to textarea
$(document).ready( function() {
  $("#input-message").emojioneArea({ events: { keydown: function (editor, event) { 
    var length = this.getText().length;
    if (length >= 249 && event.which != 8) 
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

//#region Filter DESCRIPTION:
/*
    The region implement the Filter functions
    Functions:
        A function on ready, cleafilter
*/
//#region Functions:
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
//Clear Filter (search field)
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

//#region Link to Privacy Policy
//PrivacyPolicy
$("#PrivacyPolicy").click(function() {
  window.location.href = "/privacy_policy";
});
//#endregion

//#region Contactprofile DESCRIPTION:
/*
  The region has the exercise to get staticstics about the contact
  Functions:
    onclick-Functions
*/
//#region Funtions:
//Profile
$("#profileDd").click(function() {
  var user_name = $('#NameOnlineAvatar').text()
  var chatpartner = $(".contact-profile").children()[1].innerHTML
  if(chatpartner == "No Contact"){
    return
  }
  $("#ContactProfileModal").modal("show")
  var timestamp = chat_messages[user_name][chatpartner][0].timestamp
  timestamp = timestamp.slice(0, timestamp.length-3)
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
$("#closeContactProfileButton").click(function() {
  document.getElementById("ContactProfile").innerText = ""
  document.getElementById("ContactProfileLabel").innerText = ""
});
//#endregion
//#endregion

//#region Single/GroupChats:
/*
  The region implements the functions to change the conatctlist from single to group chats
  Functions:

*/
//#region Functions:
// Informations by click on arrows (Button)
$(".expand-button").click(function() {
  if ($("#status-options").hasClass("active")) {
    $("#status-options").removeClass("active");
    setTimeout(() => {
      $("#profile").toggleClass("single_groupchat_options");
	    $("#contacts").toggleClass("single_groupchat_options");
    }, 200);
  } else {
  $("#profile").toggleClass("single_groupchat_options");
  $("#contacts").toggleClass("single_groupchat_options");
  }
  if ($("#contacts").hasClass("single_groupchat_options")) {
    $("#contacts").css("height","calc(100% - 274px)");
  } else {
    setTimeout(() => {
    $("#contacts").css("height","calc(100% - 177px)");
    }, 120);
  }
});
//Change Button (Single / Group)
function change_button() {
  if ($('#contacts').hasClass("SingleContacts")) {
    $('#Change_Chat-Buttons button').removeClass("Single-Chat");
    $("#Change_Chat-Buttons button").addClass("Group-Chat-Button");
    $("#Change_Chat-Buttons button").html("Group");
  } else if ($('#contacts').hasClass("GroupContacts")) {
    $('#Change_Chat-Buttons button').removeClass("Group-Chat-Button");
    $("#Change_Chat-Buttons button").addClass("Single-Chat");
    $("#Change_Chat-Buttons button").html("Single");
  }
  
}
//#endregion
//#endregion

//#region  Userstatus 
$("#Userstatus").click(function() {
  if ($("#profile").hasClass("single_groupchat_options")) {
    $("#profile").toggleClass("single_groupchat_options");
	  $("#contacts").toggleClass("single_groupchat_options");
  }
	$("#status-options").toggleClass("active");
});
//#endregion

// #region Function to react on dynamic changes of classes
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
    //var contactImageSrc = this.getElementsByTagName('img')[0].src
    $(".contact-profile").children()[1].innerHTML = name;
    $(".contact-profile").children()[0].src = "/static/img/usericon2.png";

    var peer_name = $(".contact-profile").children()[1].innerHTML
    fill_in_chat_msgs_single_chat($('#NameOnlineAvatar').text(), peer_name);

   });
  
  // Get Group-contacts (with Button)
  $( document). on('click', ".Group-Chat-Button" ,function() {
    if ($('#contacts').hasClass("SingleContacts")) {
    $("#contacts").empty();
    $('#contacts').toggleClass("SingleContacts");
    $("#contacts").toggleClass("GroupContacts");
    change_button();
    $("#contacts").append(`<ul id='contacts_list'>
          <li class="contact">
            <div class="wrap">
              <img src="/static/img/usericon2.png" alt="Avatar">
              <div class="meta">
                <p class="name">Group name</p>
                <p class="preview">Musterman: You just got LITT up, Mike.</p>
              </div>
            </div>
          </li>
          <li class="contact active">
            <div class="wrap">
              <img src="/static/img/usericon2.png" alt="Avatar">
              <div class="meta">
                <p id ="name" class="name">Die Bedebberten</p>
                <p class="preview">Peter: Wrong. You take the gun, or you pull out a bigger one. Or, you call their bluff. Or, you do any one of a hundred and forty six other things.</p>
              </div>
            </div>
          </li>
          </ul>`)
  }
  });

  // Get Single-contacts (with Button)
  $(document). on('click', ".Single-Chat" ,function() {
    if( $('#contacts').hasClass("GroupContacts")) {
      $("#contacts").empty();
      $('#contacts').toggleClass("GroupContacts");
      $('#contacts').toggleClass("SingleContacts");
      change_button();
      fillInContactPeers()
    }
  });
});
//#endregion

//#region Sidepanel status and close dorpdown on click (Button)
$("#status-options ul li").click(function() {
	$("#Userstatus").removeClass();
	$("#status-online").removeClass("active");
	$("#status-away").removeClass("active");
	$("#status-busy").removeClass("active");
	$("#status-offline").removeClass("active");
	$(this).addClass("active");
	
	if($("#status-online").hasClass("active")) {
		$("#Userstatus").addClass("online");
	} else if ($("#status-away").hasClass("active")) {
		$("#Userstatus").addClass("away");
	} else if ($("#status-busy").hasClass("active")) {
		$("#Userstatus").addClass("busy");
	} else if ($("#status-offline").hasClass("active")) {
		$("#Userstatus").addClass("offline");
	} else {
		$("#Userstatus").removeClass();
	};
	
	$("#status-options").removeClass("active");
});
//#endregion

//#region scrrensize DESCRIPTION: 
/*
  Function to recognize changes of the screensize every intervall
*/
//#region Function:
(function () {
    var width = screen.width,
        height = screen.height;
    setInterval(function () {
        if (screen.width !== width || screen.height !== height) {
            width = screen.width;
            if (width <= 735) {
              change_button();
            }
            height = screen.height;
            $("#profile").removeClass("single_groupchat_options");
	          $("#contacts").removeClass("single_groupchat_options");
        }
    }, 50);
}());
//#endregion
//#endregion

