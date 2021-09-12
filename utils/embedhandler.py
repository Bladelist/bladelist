class EmbedHandler:

    @staticmethod
    def bot_verification(bot, status):
        embed = {
                "type": "rich",
                "color": 0x18b745,
                "fields": [
                    {
                      "name": "Bot",
                      "value": f"[{bot.name}]({bot.web_url})",
                      "inline": True
                    },
                    {
                      "name": "Owner",
                      "value": f"[{bot.owner.user.first_name}#{bot.owner.tag}]({bot.owner.web_url})",
                      "inline": True
                    },
                    {
                      "name": "Date",
                      "value": "Some date"
                    }
                ],
                "thumbnail": {
                    "url": bot.avatar_url,
                },
                }
        if status == "verified":
            embed["title"] = "Bot Verified",
            embed["description"] = "Your bot is verified and public!",
        elif status == "added":
            embed["title"] = "New Bot",
            embed["description"] = "New bot added and is currently awaiting verification.",
            embed["footer"]["text"] = "The verification of your bot can take anywhere between 1 day to 1 week.\n " \
                                      "Please don't ping staff unless its beyond that period."
            embed["color"] = 0xffcd03
        elif status == "rejected":
            embed["title"] = "Bot Rejected",
            embed["description"] = "Reason: " + bot.meta.rejection_reason,
            embed["footer"]["text"] = f"Please make the necessary corrections and reapply\n " \
                                      f"You have {3-bot.meta.rejection_count} more attempts."
            embed["color"] = 0xf37100
        elif status == "banned":
            embed["title"] = "Bot Banned",
            embed["description"] = "Reason: " + bot.meta.ban_reason,
            embed["footer"]["text"] = "If you want to appeal. Contact staff."
            embed["color"] = 0xff0000
        return embed
