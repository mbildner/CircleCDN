var url = 'http://www.google.com';

var page = require('webpage').create();
page.onConsoleMessage = function (msg) {
    console.log(msg);
};

page.open(url, function (status) {
    page.evaluate(function () {
    	var lstor = window.webkitRTCPeerConnection;
    	console.log(lstor);
    });

    phantom.exit();
});