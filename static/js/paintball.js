var DEBUG = false;
var clientURL = $("#masthead-brand").attr('data-clientURL');

$(document).ready(function() {
    $("#getPlayerStatus").on('click', function() {

        $.ajax({
            async: false,
            type: "GET",
            url: clientURL+"/getClientState",
            data: "",
            contentType: 'application/json',
            dataType: 'json',
            success: function(data) {
                //scrumStoriesMetadata = eval(data);
                if(DEBUG) {
                    alert("[Request_Server] Request Successful. Data Received: \n" + JSON.stringify(data));
                }
                var responseData = eval(data);
                var gameStatus = "Not Started";
                var playerLife = "ALIVE";

                if(responseData.gameStarted == true) {
                    if(responseData.gameEnded == true) {
                        gameStatus = "Game over";
                    } else {
                        gameStatus = "In Progress";
                    }
                }

                if(responseData.isPlayerAlive == false) {
                    playerLife = "DEAD";
                }
                $("#matchStatus").html("" +
                    "<table>"+
                                "<thead>"+
                                "<th> </th><th> </th>"+
                                "</thead>"+
                                "<tbody>"+
                                    "<tr><td style='width:200px'>Player ID</td><td>"+responseData.client_id+"</td></tr>"+
                                    "<tr><td>Player Host</td><td>"+responseData.client_host+"</td></tr>"+
                                    "<tr><td>Player Port</td><td>"+responseData.client_port+"</td></tr>"+
                                    "<tr><td>Player Commands Sent out</td><td>"+responseData.responsesProcessed+"</td></tr>"+
                                    "<tr><td>Player Commands Receivd</td><td>"+responseData.requestsProcessed+"</td></tr>"+
                                    "<tr><td>Game status</td><td>"+gameStatus+"</td></tr>"+
                                    "<tr><td>Player Life</td><td>"+playerLife+"</td></tr>"+
                                    "<tr><td>Lives Left</td><td>"+responseData.playerLives+"</td></tr>"+
                                    "<tr><td>Player Bullets</td><td>"+responseData.playerBullets+"</td></tr>"+
                                    "<tr><td>Enemies Hit</td><td>"+responseData.playerLivesTaken+"</td></tr>"+
                                    "<tr><td>Current Action</td><td>"+responseData.playerState+"</td></tr>"+
                                    "<tr><td>Current Position</td><td>["+responseData.targetGridPositionX+","+responseData.targetGridPositionY+"]</td></tr>"+
                                "</tbody>"+
                            "</table>"+
                            "");

            },
            error: function(response) {
                alert('There was a problem connecting to the server. Please try again.\nError details: ' + JSON.stringify(response));
                alert(clientURL);
            }
        });
    });

    $("#initializePlayer").on('click', function() {

        $.ajax({
            async: false,
            type: "GET",
            url: clientURL+"/startclient",
            data: "",
            contentType: 'application/json',
            dataType: 'json',
            success: function(data) {
                //scrumStoriesMetadata = eval(data);
                if(DEBUG) {
                    alert("[Request_Server] Request Successful. Data Received: \n" + JSON.stringify(data));
                }
                $("#initializePlayer").css('display','none');
                $("#getPlayerStatus").show();
                
            },
            error: function(response) {
                alert('There was a problem connecting to the server. Please try again.\nError details: ' + JSON.stringify(response));
            }
        });
        $("#matchStatus").html("<p style='color:black;'>Player is now ready! Waiting for server!</p>");
    });
});