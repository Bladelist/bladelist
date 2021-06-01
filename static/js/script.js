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

$("#popover").popover({ trigger: "hover" });
window.FontAwesomeConfig = {
    searchPseudoElements: true
}

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

$('#report_selector').on('change', ()=>{
    if ($('#report_selector').val() === "Other") {
        $('#customField').css('display', 'block');
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


$(document).on('click', '.reviewBtn', function(e){
    e.preventDefault();
    let bot_id = $(this).attr("bot_id")
    $.ajax({
        url: '/staff/',
        headers: {'X-CSRFToken': csrftoken},
        type: 'POST',
        data: {bot_id: bot_id},
        success:function (data)
        {
          $('#verificationQueue').html(data)
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

$(document).ready(function (){

    $.ajaxSetup({
        url: '/staff/',
        headers: {'X-CSRFToken': csrftoken},
        type : 'PUT',
        success: function (data) {
            $('#verificationQueue').html(data)
            notyf.success("Success!")
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

    $('.banBotBtn').on('click',function() {
            let bot_id = $('#banBotId').val()
            let reason = $('#banBotReason').val()
            $.ajax({data: {action: "ban", bot_id: bot_id, ban_reason: reason}});
    });
});
