'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

// For ease of installation across many projects, this does not use handlebars
// This also does not require jquery. See http://youmightnotneedjquery.com/
// When calling bindFeedback(), you m
var bindFeedbackLink = function bindFeedbackLink(linkId, extraData) {
    'use strict';
    // CONSTANTS

    var formUrl = 'https://bip.elitecare.com/feedback';
    var introText = 'I want this page to:';
    var confirmationText = 'Thank you for your feedback!';
    var confirmationButtonText = 'Close';
    var divId = 'feedback-div-3278';
    var submitButtonText = 'Send';
    var acceptMessage = function acceptMessage() {
        var activeElements = [];
        var closeFeedbackDivs = function closeFeedbackDivs() {
            activeElements.forEach(function (element) {
                document.body.removeChild(element);
            });
        };
        var displaySuccess = function displaySuccess() {
            intro.innerHTML = confirmationText;
            sendButton.innerHTML = confirmationButtonText;
            sendButton.removeEventListener('click', sendFeedback);
            sendButton.addEventListener('click', closeFeedbackDivs);
            sendButton.focus();
            holder.removeChild(textarea);
        };
        var textareaClass = 'feedback__textarea';
        var buildFeedbackPayload = function buildFeedbackPayload(message) {
            var payload = { 'feedback': { 'message': message,
                    'page': window.location.toString() } };
            for (var key in extraData) {
                if (extraData.hasOwnProperty(key)) {
                    payload.feedback[key] = extraData[key];
                }
            }
            return payload;
        };
        var sendFeedback = function sendFeedback() {
            var textareaDiv = document.querySelector('.' + textareaClass);
            var textareaValue = textareaDiv.value;
            var request = new XMLHttpRequest();
            var payload = buildFeedbackPayload(textareaValue);
            request.open('POST', formUrl, true);
            request.setRequestHeader('Content-Type', 'application/json');
            request.onload = function () {
                if (request.status >= 200 && request.status < 400) {
                    // Success!
                    var resp = request.responseText;
                    displaySuccess();
                } else {
                    console.log('We reached our target server, but it returned an error');
                }
            };
            request.onerror = function () {
                console.log('There was a connection error of some sort');
            };
            request.send(JSON.stringify(payload));
        };
        var overlay = document.createElement('div');
        var holder = document.createElement('div');
        var intro = document.createElement('div');
        var textarea = document.createElement('textarea');
        var sendButton = document.createElement('button');
        var cancelDiv = document.createElement('div');
        overlay.addEventListener('click', closeFeedbackDivs);
        cancelDiv.addEventListener('click', closeFeedbackDivs);
        sendButton.addEventListener('click', sendFeedback);
        overlay.classList.add('feedback__overlay');
        holder.classList.add('feedback');
        intro.classList.add('feedback__text');
        intro.innerHTML = introText;
        textarea.classList.add(textareaClass);
        sendButton.classList.add('feedback__submit');
        sendButton.innerHTML = submitButtonText;
        cancelDiv.classList.add('feedback__cancel');
        cancelDiv.innerHTML = 'X';
        holder.appendChild(intro);
        holder.appendChild(textarea);
        holder.appendChild(sendButton);
        holder.appendChild(cancelDiv);
        document.body.appendChild(overlay);
        document.body.appendChild(holder);
        activeElements.push(overlay);
        activeElements.push(holder);
        textarea.focus();
    };
    var linkEl = document.getElementById(linkId);
    if ((typeof extraData === 'undefined' ? 'undefined' : _typeof(extraData)) !== 'object') {
        extraData = {};
    }
    linkEl.addEventListener('click', acceptMessage);
};
bindFeedbackLink('feedback__link');
exports.default = bindFeedbackLink;