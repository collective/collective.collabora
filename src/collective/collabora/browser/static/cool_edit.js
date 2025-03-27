//
// --- host to collabora ---
//


function collabora_postMessage(message_id, values={}) {
  var iframe = document.getElementById("cool-iframe");
  var targetOrigin = iframe.getAttribute("collabora_url");
  var msg = {
    "MessageId": message_id,
    "SendTime": Date.now(),
    "Values": values
  }
  console.log(msg);
  window.frames[0].postMessage(JSON.stringify(msg), targetOrigin);
}


function collabora_action_fullscreen() {
  // Requesting fullscreen works only when the focus is within the iframe.
  // But accessing the iframe to set focus is only allowed when CORS protection
  // is not in play, i.e. when running COOL via a reverse proxy on the same domain
  // and port as Plone itself.
  // FIXME test this in a proper reverse proxy setup
  // window.frames[0].contentWindow.focus();
  collabora_postMessage("Action_Fullscreen");
}


function collabora_action_save() {
  collabora_postMessage("Action_Save", {"DontSaveIfUnmodified": "true"});
}

function collabora_action_close() {
  collabora_postMessage("Action_Close");
}

function collabora_action_save_and_close() {
  collabora_action_save();
  collabora_action_close();
}

//
// --- collabora to host ---
//

function isValidJSON(text) {
  try {
    JSON.parse(text);
    return true;
  } catch {
    return false;
  }
}

function resize_iframe() {
  var iframe = document.getElementById("cool-iframe");
  var plone_version = iframe.getAttribute("plone_version");

  console.log("Resizing iframe on document loaded");
  if (plone_version == "quaive") {
    var offset = iframe.offsetTop + 80;
  } else if (plone_version == "plone6") {
    var offset = iframe.offsetTop + 5;
  } else if (plone_version == "plone5") {
    var offset = window.document.getElementById("main-container").offsetTop + 55;
  } else {
    var offset = window.document.getElementById("content").offsetTop + 210;
  }
  iframe.style.height = 'calc(100vh - ' + offset  + 'px)';
  console.log("Resized cool-iframe");
}

// https://sdk.collaboraonline.com/docs/postmessage_api.html
function handlePostMessage(e) {
  // The actual message is contained in the data property of the event.
  if (! isValidJSON(e.data)) {
    return;
  }
  var msg = JSON.parse(e.data);
  var msgId = msg.MessageId;
  var msgData = msg.Values;
  console.log('Received message: ' + msgId);
  console.log(msgData);
  if (msgData.Status == 'Frame_Ready') {
    collabora_postMessage("Host_PostmessageReady");
  }
  if (msgData.Status == 'Document_Loaded') {
    resize_iframe();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.addEventListener('message', handlePostMessage, false);
});
