
$(document).ready(function (){
    $.ajaxSetup({
        url: '/staff/servers/',
        headers: {'X-CSRFToken': csrftoken},
        type : 'PUT',
        success: function (data) {
            $('#serverVerificationQueue').html(data)
            notyf.success("Action completed successfully!")
        },
        error: function (response) {
            switch (response.status) {
                case 401:
                    notyf.error("You need to be logged in to review");
                    break;
                case 404:
                    notyf.error("Server object not found!");
                    break;
                case 503:
                    notyf.error("Server is being reviewed by another moderator");
                    break;
                default:
                    notyf.error("Something went wrong.");
            }
        }
    });

    $('.verifyServerBtn').on('click',function() {
            let server_id = $('#verifyServerId').val()
            $.ajax({data: {action: "verify", server_id: server_id}});
    });

    $('.rejectServerBtn').on('click',function() {
            let server_id = $('#rejectServerId').val()
            let reason = $('#rejectServerReason').val()
            $.ajax({data: {action: "reject", server_id: server_id, rejection_reason: reason}});
    });

    $('.unbanServerBtn').on('click',function() {
            let server_id = $('#unbanServerId').val()
            $.ajax({data: {action: "unban", server_id: server_id}});
    });

    $('.banServerBtn').on('click',function() {
            let server_id = $('#banServerId').val()
            let reason = $('#banServerReason').val()
            $.ajax({data: {action: "ban", server_id: server_id, ban_reason: reason}});
    });

});
