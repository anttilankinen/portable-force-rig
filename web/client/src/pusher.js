import Pusher from 'pusher-js/react-native';

// Enable pusher logging - don't include this in production
Pusher.logToConsole = true;

var pusher = new Pusher('638c36a2b0fb6d91b3e6', {
  cluster: 'eu',
  forceTLS: true
});

var channel = pusher.subscribe('my-channel');
channel.bind('my-event', function(data) {
  alert(data.message);
});
