const roomName = "{{ room.name }}";
const ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
const chatSocket = new WebSocket(
    ws_scheme + '://' + window.location.host +
    '/ws/game/' + roomName + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const message = data['message'];
    const infoType = data['info_type'];
    const infoValue = data['info_value'];
    const playerName = data['player_name'];

    if (message === 'update') {
        $('#players-info').find('tr[data-player="' + playerName + '"]').find('td[data-info="' + infoType + '"]').each(function() {
            $(this).removeClass('locked').addClass('unlocked').text(infoValue);
        });

        if (infoType.includes('special_feature')) {
            $('#special-features-info').find('tr[data-player="' + playerName + '"]').find('td[data-info="' + infoType + '"]').each(function() {
                $(this).removeClass('locked').addClass('unlocked').text(infoValue);
            });
        }
    } else if (message === 'start_voting') {
        $('#voting-section').show();
        $('#start-voting-btn').hide();
        $('#end-voting-btn').show();
    } else if (message === 'end_voting') {
        $('#voting-section').hide();
        $('#end-voting-btn').hide();
        $('#start-voting-btn').show();

        const votes = data['votes'];
        const resultsList = $('#results-list');
        resultsList.empty();
        for (const player in votes) {
            if (votes.hasOwnProperty(player)) {
                const voters = votes[player].join(', ');
                resultsList.append('<li>' + player + ': ' + votes[player].length + ' votes (' + voters + ')</li>');
            }
        }
        $('#voting-results').show();
    }
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

$(document).ready(function() {
    $('.locked').click(function() {
        let $button = $(this);
        let infoType = $button.data('info');
        let infoValue = $button.data('value');
        let playerName = "{{ player.player_name }}";

        if ($button.hasClass('unlocked')) {
            return;
        }

        // Send the data to WebSocket
        chatSocket.send(JSON.stringify({
            'message': 'update',
            'info_type': infoType,
            'info_value': infoValue,
            'player_name': playerName
        }));

        $button.removeClass('locked').addClass('unlocked').text('🔓');

        // Send AJAX request to update the database
        $.ajax({
            url: '{% url "update_player_info" %}',
            method: 'POST',
            data: {
                'player_name': playerName,
                'info_type': infoType,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(response) {
                console.log('Player info updated successfully');
            },
            error: function(response) {
                console.error('Error updating player info');
            }
        });
    });

    $('#start-voting-btn').click(function() {
        chatSocket.send(JSON.stringify({
            'message': 'start_voting'
        }));
    });

    $('#end-voting-btn').click(function() {
        chatSocket.send(JSON.stringify({
            'message': 'end_voting'
        }));
    });

    $('#voting-form').submit(function(e) {
        e.preventDefault();
        const vote = $('input[name="vote"]:checked').val();
        chatSocket.send(JSON.stringify({
            'message': 'vote',
            'vote': vote,
            'voter': "{{ player.player_name }}"
        }));
    });
});