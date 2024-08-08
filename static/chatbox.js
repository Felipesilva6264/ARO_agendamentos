document.getElementById('chat-icon').addEventListener('click', function() {
    document.getElementById('chat-box').style.display = 'flex';
});

document.getElementById('close-chat').addEventListener('click', function() {
    document.getElementById('chat-box').style.display = 'none';
});

document.getElementById('send').addEventListener('click', function() {
    var message = document.getElementById('message').value;
    var chatBody = document.getElementById('chat-body');
    chatBody.innerHTML += '<div>User: ' + message + '</div>';

    fetch('/webhook', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: 'unique-session-id', // You should use a unique session ID for each user
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        chatBody.innerHTML += '<div>Bot: ' + data.reply + '</div>';
        document.getElementById('message').value = '';
    });
});
