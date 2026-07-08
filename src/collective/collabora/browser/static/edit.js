//
// --- host to collabora ---
//


function collabora_postMessage(message_id, values={}) {
  var iframe = document.getElementById("cool-iframe");
  var targetOrigin = iframe.getAttribute("collabora_server_url");
  var msg = {
    "MessageId": message_id,
    "SendTime": Date.now(),
    "Values": values
  }
  console.log(msg);
  window.frames[0].postMessage(JSON.stringify(msg), targetOrigin);
}


function collabora_action_fullscreen() {
  // Requesting fullscreen works only when CORS protection is not in play, i.e.
  // when running Collabora via a reverse proxy on the same domain and port as
  // Plone itself.
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

// Fix Collabora menu bar overflow in non-English UI, directly via CSS.
// This works around an upstream regression introduced in the 26.x series.
//
// Background: when the Collabora UI language is not English, localized menu
// labels are wider. Since Collabora 26 (which added the "Editing" menu with
// "Viewing Mode" / "Editing Mode" entries) the menu bar can overflow in e.g.
// French: not all entries fit. Collabora apparently computes the menu bar
// layout before the localized strings are applied and does not recompute
// afterwards.
//
// A reflow can be triggered by, in the UI, selecting "Viewing Mode" and then
// "Editing Mode". That fixes the layout issue manually. Trying to force a reflow
// by firing postMessage calls failed.
//
// Instead, sidestep the reflow entirely and fix via CSS. Injecting a stylesheet 
// did not fix the rendering, but setting a hard style attribute does the trick. 
// This requires same-origin access to the iframe, which holds when Collabora is 
// reverse-proxied on the same origin as Plone (the recommended production setup).
function collabora_inject_iframe_css() {
  var iframe = document.getElementById("cool-iframe");
  if (!iframe) {
    return;
  }
  var doc;
  try {
    doc = iframe.contentDocument || iframe.contentWindow.document;
  } catch (err) {
    // Cross-origin: cannot reach into the iframe. Nothing we can do here.
    console.warn("Cannot reach Collabora iframe (cross-origin):", err);
    return;
  }
  if (!doc) {
    return;
  }
  var nav = doc.querySelector("html > body > nav.main-nav");
  if (nav) {
    nav.style.height = "auto";
  }
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
    collabora_inject_iframe_css();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.addEventListener('message', handlePostMessage, false);
});
