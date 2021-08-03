
$(document).ready(function (){
    $.ajaxSetup({
        url: '/staff/bots/',
        headers: {'X-CSRFToken': csrftoken},
        type : 'PUT',
        success: function (data) {
            $('#botVerificationQueue').html(data)
            notyf.success("Action completed successfully!")
        },
        error: function (response) {
            switch (response.status) {
                case 401:
                    notyf.error("You need to be logged in to review");
                    break;
                case 404:
                    notyf.error("Bot object not found!");
                    break;
                case 503:
                    notyf.error("Bot is being reviewed by another moderator");
                    break;
                default:
                    notyf.error("Something went wrong.");
            }
        }
    });

    $('.verifyBotBtn').on('click',function() {
            let bot_id = $('#verifyBotId').val()
            $.ajax({data: {action: "verify", bot_id: bot_id}});
    });

    $('.rejectBotBtn').on('click',function() {
            let bot_id = $('#rejectBotId').val()
            let reason = $('#rejectBotReason').val()
            $.ajax({data: {action: "reject", bot_id: bot_id, rejection_reason: reason}});
    });

    $('.unbanBotBtn').on('click',function() {
            let bot_id = $('#unbanBotId').val()
            $.ajax({data: {action: "unban", bot_id: bot_id}});
    });

    $('.banBotBtn').on('click',function() {
            let bot_id = $('#banBotId').val()
            let reason = $('#banBotReason').val()
            $.ajax({data: {action: "ban", bot_id: bot_id, ban_reason: reason}});
    });
});

