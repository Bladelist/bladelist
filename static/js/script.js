var notyf = new Notyf({position: {x:'right',y:'top'}});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken')

// $("#popover").popover({ trigger: "hover" });
// window.FontAwesomeConfig = {
//     searchPseudoElements: true
// }

const popupCenter = ({url, title, w, h}) => {
// Fixes dual-screen position                             Most browsers      Firefox
const dualScreenLeft = window.screenLeft !==  undefined ? window.screenLeft : window.screenX;
const dualScreenTop = window.screenTop !==  undefined   ? window.screenTop  : window.screenY;

const width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
const height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;

const systemZoom = width / window.screen.availWidth;
const left = (width - w) / 2 / systemZoom + dualScreenLeft
const top = (height - h) / 2 / systemZoom + dualScreenTop
const newWindow = window.open(url, title,
  `
  scrollbars=yes,
  width=${w / systemZoom},
  height=${h / systemZoom},
  top=${top},
  left=${left}
  `
)

if (window.focus) newWindow.focus();
}

$(document).on('click', '.voteBotBtn', function (){
    let bot_id = $(this).attr("bot_id")

    $.ajax({
        url: '/bots/',
        headers: {'X-CSRFToken': csrftoken},
        type: 'PUT',
        data: {bot_id: bot_id},
        success:function (data)
        {
          $("#botVoteCount").text(data["vote_count"]);
          notyf.success("Voted successfully!")
        },
        error:function (response) {
            switch (response.status) {
                case 401:
                    notyf.error("You need to be logged in to vote");
                    break;
                case 403:
                    notyf.error("You can only vote once in 12 hours per bot");
                    break;
                default:
                    notyf.error("Something went wrong.");
            }
        },
    });
})

$(document).on('click', '.voteServerBtn', function (){
    let server_id = $(this).attr("server_id")
    $.ajax({
        url: '/servers/',
        headers: {'X-CSRFToken': csrftoken},
        type: 'PUT',
        data: {server_id: server_id},
        success:function (data)
        {
          $("#serverVoteCount").text(data["vote_count"]);
          notyf.success("Voted successfully!")
        },
        error:function (response) {
            switch (response.status) {
                case 401:
                    notyf.error("You need to be logged in to vote");
                    break;
                case 403:
                    notyf.error("You can only vote once in 12 hours per server");
                    break;
                default:
                    notyf.error("Something went wrong.");
            }
        },
    });
})

$('#report_selector').on('change', ()=>{
    if ($('#report_selector').val() === "Other") {
        $('#customField').css('display', 'block');
    }
})

$('#server_report_selector').on('change', ()=>{
    if ($('#server_report_selector').val() === "Other") {
        $('#serverReportCustomReasonField').css('display', 'block');
    }
})


$(document).on('click', '.reportBotBtn', function (){
    let bot_id = $(this).attr("bot_id")
    let reason = $('#report_selector').val()
    if(reason==="Other"){
        reason = $('#customReason').val()
    }
    $.ajax({
        url: '/bots/edit/',
        headers: {'X-CSRFToken': csrftoken},
        type: 'PUT',
        data: {bot_id: bot_id, reason: reason},
        success:function (data)
        {
          notyf.success("Reported successfully!");
        },
        error:function (response) {
            switch (response.status) {
                case 401:
                    notyf.error("You need to be logged in to report");
                    break;
                case 403:
                    notyf.error("You already have 1 report awaiting review.");
                    break;
                default:
                    notyf.error("Something went wrong.");
            }
        },
    });
})

$(document).on('click', '.reportServerBtn', function (){
    let server_id = $(this).attr("server_id")
    let reason = $('#server_report_selector').val()
    if(reason==="Other"){
        reason = $('#serverReportCustomReason').val()
    }
    $.ajax({
        url: '/servers/edit/',
        headers: {'X-CSRFToken': csrftoken},
        type: 'PUT',
        data: {server_id: server_id, reason: reason},
        success:function (data)
        {
          notyf.success("Reported successfully!");
        },
        error:function (response) {
            switch (response.status) {
                case 401:
                    notyf.error("You need to be logged in to report");
                    break;
                case 403:
                    notyf.error("You already have 1 report awaiting review.");
                    break;
                default:
                    notyf.error("Something went wrong.");
            }
        },
    });
})

$(document).on('click', '.deleteBotBtn', function(e){
    let bot_id = $('#deleteBotId').val()
    $.ajax({
        url: `/bots/edit/` + '?' + $.param({"bot_id": bot_id,}) ,
        headers: {'X-CSRFToken': csrftoken},
        type: 'DELETE',
        success:function (data)
        {
          notyf.success("Bot deleted successfully!");
        },
        error:function (response) {
            switch (response.status) {
                case 401:
                    notyf.error("You need to be logged in to delete");
                    break;
                case 404:
                    notyf.error("Bot object not found!");
                    break;
                default:
                    notyf.error("Something went wrong.");
            }
        },
    });
})

$(document).on('click', '.deleteServerBtn', function(e){
    let server_id = $('#deleteServerId').val()
    $.ajax({
        url: `/servers/edit/` + '?' + $.param({"server_id": server_id,}) ,
        headers: {'X-CSRFToken': csrftoken},
        type: 'DELETE',
        success:function (data)
        {
          notyf.success("Server deleted successfully!");
        },
        error:function (response) {
            switch (response.status) {
                case 401:
                    notyf.error("You need to be logged in to delete");
                    break;
                case 404:
                    notyf.error("Server object not found!");
                    break;
                default:
                    notyf.error("Something went wrong.");
            }
        },
    });
})

$(document).on('click', '.reapplyBotBtn', function(e){
    let bot_id = $(this).attr("bot_id")
    $.ajax({
        url: `/bots/${bot_id}`,
        headers: {'X-CSRFToken': csrftoken},
        type: 'PUT',
        data: {bot_id: bot_id},
        success:function (data)
        {
          notyf.success("Successfully reapplied for review");
        },
        error:function (response) {
            switch (response.status) {
                case 401:
                    notyf.error("You need to be logged in to reapply");
                    break;
                case 403:
                    notyf.error("This bot is banned and cannot apply for verification");
                    break;
                case 404:
                    notyf.error("Bot object not found!");
                    break;
                case 503:
                    notyf.error("You have already reapplied for verification");
                    break;
                default:
                    notyf.error("Something went wrong.");
            }
        },
    });
})


$(document).on('click', '.reapplyServerBtn', function(e){
    let server_id = $(this).attr("server_id")
    $.ajax({
        url: `/servers/${server_id}`,
        headers: {'X-CSRFToken': csrftoken},
        type: 'PUT',
        data: {server_id: server_id},
        success:function (data)
        {
          notyf.success("Successfully reapplied for review");
        },
        error:function (response) {
            switch (response.status) {
                case 401:
                    notyf.error("You need to be logged in to reapply");
                    break;
                case 403:
                    notyf.error("This server is banned and cannot apply for verification");
                    break;
                case 404:
                    notyf.error("Server object not found!");
                    break;
                case 503:
                    notyf.error("You have already reapplied for verification");
                    break;
                default:
                    notyf.error("Something went wrong.");
            }
        },
    });
})


$(document).on('click', '.botReviewBtn', function(e){
    e.preventDefault();
    let bot_id = $(this).attr("bot_id")
    $.ajax({
        url: '/staff/bots/',
        headers: {'X-CSRFToken': csrftoken},
        type: 'POST',
        data: {bot_id: bot_id},
        success:function (data)
        {
          $('#botVerificationQueue').html(data)
          notyf.success("Queued for review");
        },
        error:function (response) {
            switch (response.status) {
                case 401:
                    notyf.error("You need to be logged in to review");
                    break;
                case 403:
                    notyf.error("You already have 1 bot awaiting review.");
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
        },
    });
})

$(document).on('click', '.serverReviewBtn', function(e){
    e.preventDefault();
    let server_id = $(this).attr("server_id")
    $.ajax({
        url: '/staff/servers/',
        headers: {'X-CSRFToken': csrftoken},
        type: 'POST',
        data: {server_id: server_id},
        success:function (data)
        {
          $('#serverVerificationQueue').html(data)
          notyf.success("Queued for review");
        },
        error:function (response) {
            switch (response.status) {
                case 401:
                    notyf.error("You need to be logged in to review");
                    break;
                case 403:
                    notyf.error("You already have 1 server awaiting review.");
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
        },
    });
})

$(document).on('click', '#refreshAdminServers', function (e){
    $('#refreshAdminServers').prop('disabled', true);
    $.ajax({
        url: '/servers/refresh/',
        headers: {'X-CSRFToken': csrftoken},
        type: 'GET',
        success:function(data)
        {
          $('#serverRefreshSection').html(data);
          notyf.success("Sync successful");
          $('#refreshAdminServers').prop('disabled', false);
        },
        error:function (response) {
           notyf.error("Something went wrong.");
           $('#refreshAdminServers').prop('disabled', false);

        },
    });
});