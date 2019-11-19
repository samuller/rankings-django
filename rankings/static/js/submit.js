App.Rankings.Submit = {

    /**
     *
     */
    setupPlayerChoices: function () {
        // TODO: handle any number of teams and players
        var maxTeams = App.Rankings.current_activity.max_teams_per_match;
        var maxPlayersPerTeam = App.Rankings.current_activity.max_players_per_team;
        var maxPlayers = maxTeams * maxPlayersPerTeam;

	    var players = App.Rankings.player_ids;
	    // add default 'no choice/field name' option
	    $('#p0').append('<option value="-1">[Player 1]</option>');
	    $('#p1').append('<option value="-2">[Player 2]</option>');
	    $('#p2').append('<option value="-3">[Player 3]</option>');
	    $('#p3').append('<option value="-4">[Player 4]</option>');
	    // appends alphabetically
	    players.sort(function(a,b){ return a[1] > b[1] ? 1 : -1 });
	    for (i = 0;i < players.length;i++) {
		    $('#p0').append('<option value="'+players[i][0]+'">'+players[i][1]+'</option>');
		    $('#p1').append('<option value="'+players[i][0]+'">'+players[i][1]+'</option>');
		    $('#p2').append('<option value="'+players[i][0]+'">'+players[i][1]+'</option>');
		    $('#p3').append('<option value="'+players[i][0]+'">'+players[i][1]+'</option>');
	    }
    },

    /**
    *
    */
    updatePlayerChoices: function () {
        // TODO: handle any number of teams and players
        // enabled all entries
        $("#p0 > option").each(function(){$(this).removeAttr("disabled");});
        $("#p1 > option").each(function(){$(this).removeAttr("disabled");});
        $("#p2 > option").each(function(){$(this).removeAttr("disabled");});
        $("#p3 > option").each(function(){$(this).removeAttr("disabled");});
        // disable choices that are selected by any other options
        var selection = $("#p0 option:selected").val();
        $("#p1 option[value='"+selection+"']").attr("disabled", "disabled")
        $("#p2 option[value='"+selection+"']").attr("disabled", "disabled")
        $("#p3 option[value='"+selection+"']").attr("disabled", "disabled")

        var selection = $("#p1 option:selected").val();
        $("#p0 option[value='"+selection+"']").attr("disabled", "disabled")
        $("#p2 option[value='"+selection+"']").attr("disabled", "disabled")
        $("#p3 option[value='"+selection+"']").attr("disabled", "disabled")

        var selection = $("#p2 option:selected").val();
        $("#p0 option[value='"+selection+"']").attr("disabled", "disabled")
        $("#p1 option[value='"+selection+"']").attr("disabled", "disabled")
        $("#p3 option[value='"+selection+"']").attr("disabled", "disabled")

        var selection = $("#p3 option:selected").val();
        $("#p0 option[value='"+selection+"']").attr("disabled", "disabled")
        $("#p1 option[value='"+selection+"']").attr("disabled", "disabled")
        $("#p2 option[value='"+selection+"']").attr("disabled", "disabled")

        App.Rankings.Submit.updateSubmitButtons();
        App.Rankings.RoundRobin.updatePlayerChoices();
    },

    updateSubmitButtons: function () {

    },

    /**
    *
    */
    getSelectedTeams: function () {
        var maxTeams = App.Rankings.current_activity.max_teams_per_match;
        maxTeams = maxTeams ? maxTeams : 2;
        var maxPlayersPerTeam = App.Rankings.current_activity.max_players_per_team;
        // create team setup based on current activity and selected players
        var teams = [];
        var playerCount = 0;
        for(i = 0;i < maxTeams;i++) {
            var team = [];
            for(j = 0;j < maxPlayersPerTeam;j++) {
                var player = parseInt($('#p' + playerCount).val());
                if (player >= 0) {
                    team.push(player);
                }
                playerCount++;
            }
            teams.push(team);
        }
        return teams;
    },

    /**
    *
    */
    getAllMatchPlayers: function () {
        var maxTeams = App.Rankings.current_activity.max_teams_per_match;
        var maxPlayersPerTeam = App.Rankings.current_activity.max_players_per_team;
        // create team setup based on current activity and selected players
        var players = [];
        var playerCount = 0;
        for(i = 0;i < maxTeams*maxPlayersPerTeam;i++) {
            var player = parseInt($('#p' + i).val());
            players.push(player);
        }
        return players;
    },

    toServer: function (teams, wins) {
        var url = "/"+App.Rankings.current_activity["url"] + "/api/add_matches";

        if (wins.length != teams.length) {
            console.log(String.format(
                "Number of teams ({0}) and wins ({1}) did not match. Submission failed.",
                teams.length, wins.length));
            alert("Submission failed due to JavaScript internal error.");
            return;
        }

        // disable all submit buttons
        $('.submit-match').prop('disabled', true);
        // submit match results
        $.ajax({
            type: "POST",
            url: url,
            contentType: 'application/json',
            data: JSON.stringify({
                "teams": teams,
                "wins": wins
            }),
            dataType: 'json',
            success: function( response ) {
                if(response.valid == 1) {
                    $('#modalSubmitMatch').foundation('reveal','close');
                    location.reload(false);
                } else {
                    alert("Submission failed:\n"+
                          "Make sure you selected at least 1 player on each side.\n");
                }
            },
            error: function( response ) {
                alert("Failed with status code "+response.status+".");
            },
            complete: function( response ) {
                // re-enable all submit buttons
                $('.submit-match').prop('disabled', false);
            }
        });
    },

    undoPrevious: function(matchId) {
        var url = "/"+App.Rankings.current_activity["url"] + "/api/undo_submission";

        var choice = confirm("Are you sure you want to delete this match?");
        if (choice == false) {
            return;
        }

        $.ajax({
            type: "POST",
            url: url,
            contentType: 'application/json',
            data: JSON.stringify({
                "match-id": matchId,
            }),
            dataType: 'json',
            success: function( response ) {
                if(response.valid == 1) {
                    location.reload(false);
                } else {
                    if(reason in response){
                        alert("Deletion failed: " + response.reason + ".\n");
                    } else {
                        alert("Deletion failed.\n");
                    }
                }
            },
            error: function( response ) {
                alert("Failed with status code "+response.status+".");
            },
        });
    },
};

App.Rankings.SingleMatch = {

    submit: function (winner) {
        App.Rankings.MultiMatches.submit([winner]);
    },
}

App.Rankings.MultiMatches = {

    removeSelectedMatches: function () {
        App.Utils.removeSelectedOptions('#multi-match-list');
    },

    addMatchResult: function (winner) {
        var value = winner;
        var text = 'Team '+winner+' win';
        App.Utils.addOption('#multi-match-list', value, text);
    },

    confirmAndSubmit: function () {
        var wins = [];
        $('#multi-match-list option').each( function() {
            wins.push($(this).val());
        });

        var counts = {};
        counts[1] = 0;
        counts[2] = 0;
        wins.forEach(function(entry) {
            counts[entry] = 1 + (counts[entry] || 0);
        });

        var winner = 0;
        var winnerCount = 0;
        $.each(counts, function(key, value) {
            if (value > winnerCount) {
                winner = key;
                winnerCount = value;
            }
        });

        var result = counts[1] == counts[2] ? "teams tied" :
                     (counts[1] > counts[2] ? "Team 1 won" : "Team 2 won");
        var resultDetailed = counts[1] + " vs " + counts[2];
        var question = 'Confirm that you want to submit a set of '+wins.length+
                       ' matches with results of '+resultDetailed+' ('+result+')?';
        if (confirm(question)) {
            App.Rankings.MultiMatches.submit(wins);
        }
    },

    /**
     * Submits matches for games where the same teams played 1 or more games.
     */
    submit: function (wins) {
        var matchTeams = App.Rankings.Submit.getSelectedTeams();
        var numOfGames = wins.length;
        // create an array of the same value multiple times
        var teams = Array.apply(null, Array(numOfGames)).map(function() { return matchTeams; });

        App.Rankings.Submit.toServer(teams, wins);
    },
};

App.Rankings.RoundRobin = {

    setup: function() {
        $("#all_players_won").on('change', function(event) {
            App.Rankings.RoundRobin.updateSelectedOptions(event);
        });
        $("#all_players_lost").on('change', function(event) {
            App.Rankings.RoundRobin.updateSelectedOptions(event);
        });
        App.Rankings.RoundRobin.updatePlayerChoices();
    },

    updatePlayerChoices: function () {
        // remove all options
        $('#all_players_won').find('option').remove();
        $('#all_players_lost').find('option').remove();

	    // add default 'no choice/field name' option
	    $('#all_players_won').append('<option value="-1">(None)</option>');
	    $('#all_players_lost').append('<option value="-1">(None)</option>');

        var matchPlayers = App.Rankings.Submit.getAllMatchPlayers();

	    // append alphabetically
	    var players = App.Rankings.player_ids;
	    players.sort(function(a,b){ return a[1] > b[1] ? 1 : -1 });
	    for (i = 0;i < matchPlayers.length;i++) {
            // search through array of tuples for player with correct id
            var idx = $.map(players, function(obj, index) {
                if (obj[0] == matchPlayers[i]) {
                    return index;
                }
            })[0];

            if (idx > -1) {
		        $('#all_players_won').append('<option value="'+players[idx][0]+'">'+players[idx][1]+'</option>');
		        $('#all_players_lost').append('<option value="'+players[idx][0]+'">'+players[idx][1]+'</option>');
            }
	    }
    },

    updateSelectedOptions: function(event) {
        if(event.target.id == "all_players_won") {
            $("#all_players_lost").val(-1);
        } else if(event.target.id == "all_players_lost") {
            $("#all_players_won").val(-1);
        } else {
            console.log("Unknown element triggered App.Rankings.RoundRobin.updateSelectedOptions: " +
                JSON.stringify(event.target));
        }
    },

    submit: function () {
        // TODO: handle non-2v2 cases
        var matchPlayers = App.Rankings.Submit.getAllMatchPlayers();

        var teamsGame1 = [[matchPlayers[0], matchPlayers[1]],
                          [matchPlayers[2], matchPlayers[3]]];
        var teamsGame2 = [[matchPlayers[0], matchPlayers[2]],
                          [matchPlayers[1], matchPlayers[3]]];
        var teamsGame3 = [[matchPlayers[0], matchPlayers[3]],
                          [matchPlayers[2], matchPlayers[1]]];

        var teams = [teamsGame1, teamsGame2, teamsGame3];
        var wins = [];
        if ($("#all_players_lost").val() >= 0) {
            var player = parseInt($("#all_players_lost").val(), 10);

            $.map(teams, function (teamsPerGame, j) {
                teamsPerGame.map( function(players, i) {
                    // if it doesn't contain loser
                    if ($.inArray(player, players) < 0) {
                        wins.push(i + 1);
                    }
                });
            });
        } else if ($("#all_players_won").val() >= 0) {
            var player = parseInt($("#all_players_won").val(), 10);

            $.map(teams, function (teamsPerGame, j) {
                teamsPerGame.map( function(players, i) {
                    // if it does contain winner
                    if ($.inArray(player, players) >= 0) {
                        wins.push(i + 1);
                    }
                });
            });
        } else {
            alert('Submission failed: no winner/loser option selected.');
            return;
        }

        App.Rankings.Submit.toServer(teams, wins);
    },
};

/**
 *
 */
$(function() {
  App.Rankings.Submit.setupPlayerChoices();
  App.Rankings.RoundRobin.setup();
});
