// $(document).ready(function () {
//     function updatePlayerList() {
//         $.ajax({
//             url: '{% url "number_of_people" room.name %}',
//             method: 'GET',
//             success: function(data) {
//                 $('#player-count').text(data.count);
//                 let playersList = $('#playerList');
//                 playersList.empty();
//                 data.players.forEach(function(player) {
//                     let playerItem = '<li>' + player.player_name;
//                     {% if is_creator %}
//                     playerItem += ' <button class="remove-btn" data-player-id="' + player.id + '">Remove</button>';
//                     {% endif %}
//                     playerItem += '</li>';
//                     playersList.append(playerItem);
//                 });
//
//                 if (data.count > 1 && {% if is_creator %}true{% else %}false{% endif %}) {
//                     $('#startGameBtn').show();
//                 } else {
//                     $('#startGameBtn').hide();
//                 }
//             },
//             error: function(error) {
//                 console.error('Error:', error);
//             }
//         });
//     }
//
//     function checkRoomExists() {
//         $.ajax({
//             url: '{% url "game_room" room.name %}',
//             method: 'GET',
//             statusCode: {
//                 404: function() {
//                     window.location.href = '{% url "index" %}';
//                 }
//             }
//         });
//     }
//
//     function checkIfPlayerStillInRoom() {
//         $.ajax({
//             url: '{% url "check_player_in_room" room.name %}',
//             method: 'GET',
//             success: function(data) {
//                 if (data.status === 'removed') {
//                     window.location.href = '{% url "index" %}';
//                 }
//             },
//             error: function(error) {
//                 console.error('Error:', error);
//             }
//         });
//     }
//
//     function checkIfGameStarted() {
//         $.ajax({
//             url: '{% url "check_game_started" room.name %}',
//             method: 'GET',
//             success: function(data) {
//                 if (data.is_game_started) {
//                     window.location.href = '{% url "start_game" room.name %}';
//                 }
//             },
//             error: function(error) {
//                 console.error('Error:', error);
//             }
//         });
//     }
//
//     setInterval(updatePlayerList, 1000);
//     setInterval(checkRoomExists, 1000);
//     setInterval(checkIfPlayerStillInRoom, 1000);
//     setInterval(checkIfGameStarted, 1000);
//
//     $(document).on('click', '.remove-btn', function() {
//         const playerId = $(this).data('player-id');
//         $.ajax({
//             url: '{% url "remove_player" room.name %}',
//             method: 'POST',
//             headers: {
//                 'X-CSRFToken': '{{ csrf_token }}'
//             },
//             data: {
//                 'player_id': playerId
//             },
//             success: function(data) {
//                 if (data.status === 'success') {
//                     updatePlayerList();
//                 } else {
//                     alert(data.message);
//                 }
//             },
//             error: function(error) {
//                 console.error('Error:', error);
//             }
//         });
//     });
//
//     $('#exit-room-btn').click(function() {
//         $.ajax({
//             url: '{% url "exit_room" room.name %}',
//             method: 'POST',
//             headers: {
//                 'X-CSRFToken': '{{ csrf_token }}'
//             },
//             success: function(data) {
//                 if (data.status === 'success') {
//                     window.location.href = '{% url "index" %}';
//                 } else {
//                     alert(data.message);
//                 }
//             },
//             error: function(error) {
//                 console.error('Error:', error);
//             }
//         });
//     });
//
//     $('#close-room-btn').click(function() {
//         $.ajax({
//             url: '{% url "close_room" room.name %}',
//             method: 'POST',
//             headers: {
//                 'X-CSRFToken': '{{ csrf_token }}'
//             },
//             success: function(data) {
//                 if (data.status === 'success') {
//                     window.location.href = '{% url "index" %}';
//                 } else {
//                     alert(data.message);
//                 }
//             },
//             error: function(error) {
//                 console.error('Error:', error);
//             }
//         });
//     });
//
//     $('#startGameBtn').click(function() {
//         $.ajax({
//             url: '{% url "start_game" room.name %}',
//             method: 'POST',
//             headers: {
//                 'X-CSRFToken': '{{ csrf_token }}'
//             },
//             success: function(data) {
//                 if (data.status === 'success') {
//                     window.location.href = '{% url "game_room" room.name %}';
//                 } else {
//                     alert(data.message);
//                 }
//             },
//             error: function(error) {
//                 console.error('Error:', error);
//             }
//         });
//     });
// });
