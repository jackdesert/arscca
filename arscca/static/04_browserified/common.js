(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
'use strict';

require('./on_error');
},{"./on_error":2}],2:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});
var on_error = function on_error() {
    // SENDING ERROR MESSAGES TO ENGINEERS
    //
    // A. When an unexpected exception is raised
    //    When a legitimate error is found, the definition of window.onerror
    //    below calls "sendDataToEngineers" for you, including pertinent information
    //
    // B. When your code identifies something amiss, AND YOU WANT EVERYTHING TO STOP
    //    To send data to engineers AND STOP EXECUTION,
    //    just call an unknown method right in your code.
    //
    // C. When your code identifies something amiss, AND YOU WANT TO CONTINUE
    //    If, for example, you notice that the number of divs does not match
    //    your expectation, you probably want to alertEngineersAndContinue().
    // C. (tell engineers and halt execution)
    var alertEngineersAndHalt = function alertEngineersAndHalt(message) {
        'use strict';

        alertEngineersCommon(message, true);
    };
    // C. (tell engineers, but continue execution)
    var alertEngineersAndContinue = function alertEngineersAndContinue(message) {
        'use strict';

        alertEngineersCommon(message);
    };
    // Consider this method private.
    // Only call it from the other methods defined on this page
    var alertEngineersCommon = function alertEngineersCommon(message, haltExecution) {
        'use strict';

        var details = { message: message,
            path: window.location.href,
            user_agent: navigator.userAgent
            //story: story.read()
        };
        sendDataToEngineers(details);
        if (haltExecution) {
            throw message;
        }
    };
    // A. (Covers unexpected exceptions)
    //    This is called automatically when an unexpected error occurs
    window.onerror = function (message, fileName, lineNumber, columnNumber, error) {
        // Source: https://stackoverflow.com/questions/951791/javascript-global-error-handling
        // In development, url is the page you visited.
        // In production, url is the location of the javascript file that was run.
        'use strict';

        var details = { message: message,
            file_name: fileName,
            path: window.location.href,
            line_number: lineNumber,
            column_number: columnNumber,
            error: error,
            user_agent: navigator.userAgent
            //story: story.read()
        };
        // Return value matters for IE
        return sendDataToEngineers(details);
    };
    // Consider this method private.
    // Only call it from the other methods defined on this page
    var sendDataToEngineers = function sendDataToEngineers(details) {
        'use strict';

        var url = '/javascript_errors',
            data_json = JSON.stringify(details),
            request = new XMLHttpRequest();
        request.open('POST', url, true);
        request.setRequestHeader('Content-Type', 'application/json');
        request.onload = function () {
            if (request.status >= 200 && request.status < 400) {
                // Success!
                var respJson = request.responseText,
                    resp = JSON.parse(respJson),
                    alertUser = resp.alert_user;
                console.log('SUCCESSFULLY sent the following error to server:');
                if (alertUser) {
                    // Server tells us whether to alert user
                    alert(details.message);
                }
            } else {
                // We reached our target server, but it returned an error
                console.log('UNABLE to send the following error to server:');
            }
            console.log(details.message + '.  Line: ' + details.line_number);
        };
        request.onerror = function () {
            // There was a connection error of some sort
        };
        request.send(data_json);
        var suppressErrorAlert = true;
        // If you return true, then error alerts (like in older versions of
        // Internet Explorer) will be suppressed.
        return suppressErrorAlert;
    };
};
on_error();
exports.default = on_error;
},{}]},{},[1]);
