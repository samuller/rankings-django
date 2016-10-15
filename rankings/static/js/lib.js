var App = {};

App.Utils = {
    /**
     *
     */
    removeSelectedOptions: function (element) {
        $(element+' option:selected').each( function() {
            $(this).remove();
        });
    },

    /**
     *
     */
    addOption: function (element, value, text) {
        $(element).append("<option value='"+value+"'>"+text+"</option>");
    },

    /**
     *
     */
    pad: function (n, width, z) {
        z = z || '0';
        n = n + '';
        return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
    },
};

App.Matches = {
    invalidateDeleteLink: function (matchId) {
        $("#delete-"+matchId).remove();
    },

    triggerInvalidateDeleteLink: function () {
        $('[id*="delete-"]').each( function() {
            var expireDateStr = $(this).data("expire");
            var nowDate = new Date();
            var expireDate = new Date(expireDateStr);
            var millisLeft = expireDate - nowDate;
            if (millisLeft > 0) {
                window.setTimeout(function () {
                    App.Matches.invalidateDeleteLink($(this).data("id"));
                }, millisLeft);
            } else {
                App.Matches.invalidateDeleteLink($(this).data("id"));
            }
        });
    },
};

App.Validation = {
    validateAllPendingMatches: function() {
        var url = "/api/validate_all";

        $.ajax({
            type: "POST",
            url: url,
            contentType: 'application/json',
            data: JSON.stringify({
                "validated": true
            }),
            dataType: 'json',
            success: function( response ) {
                if(response.valid == 1) {
                    location.reload(false);
                } else {
                    alert("Submission failed.\n");
                }
            },
            error: function( response ) {
                alert("Failed with status code "+response.status+".");
            },
        });
    },

    validateSelectedMatch: function() {
        var matchId = $('#select_pending_match').val();
        App.Validation.submit(matchId, true);
    },

    invalidateSelectedMatch: function() {
        var matchId = $('#select_pending_match').val();
        App.Validation.submit(matchId, false);
    },

    submit: function(matchId, validated) {
        var url = "/"+App.Rankings.current_activity["url"] + "/api/validate_match";

        // submit match results
        $.ajax({
            type: "POST",
            url: url,
            contentType: 'application/json',
            data: JSON.stringify({
                "match-id": matchId,
                "validated": validated
            }),
            dataType: 'json',
            success: function( response ) {
                if(response.valid == 1) {
                    location.reload(false);
                } else {
                    alert("Submission failed.\n");
                }
            },
            error: function( response ) {
                alert("Failed with status code "+response.status+".");
            },
        });

    },

};

/**
 *
 */
$(function() {
  App.Matches.triggerInvalidateDeleteLink();
});
