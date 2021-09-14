class EmbedHandler:
    @staticmethod
    def bot_verification(bot, status):
        embed = {
                "type": "rich",
                "title": "New Bot",
                "description": "New bot added and is currently awaiting verification.",
                "color": 0xffcd03,
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
                      "value": bot.date_added.strftime("%m/%d/%Y")
                    }

                ],
                "thumbnail": {
                    "url": bot.avatar_url,
                },
                "footer": {
                    "text": "The verification of your bot can take anywhere between 1 day to 1 week.\n "\
                    "Please don't ping staff unless its beyond that period."
                }
                }

        if status == "verified":
            embed["title"] = "Bot Verified"
            embed["description"] = "Your bot is verified and public!"
            embed["footer"]["text"] = ""
            embed["color"] = 0x18B745
        elif status == "added":
            pass
        elif status == "rejected":
            embed["title"] = "Bot Rejected"
            embed["description"] = f"Reason: {bot.meta.rejection_reason}"
            embed["footer"]["text"] = f"Please make the necessary corrections and reapply\n "\
                                      f"You have {3-bot.meta.rejection_count} more attempts."
            embed["color"] = 0xf37100
        elif status == "banned":
            embed["title"] = "Bot Banned"
            embed["description"] = f"Reason:  {bot.meta.ban_reason}"
            embed["footer"]["text"] = "If you want to appeal. Contact staff."
            embed["color"] = 0xff0000
        elif status == "unbanned":
            embed["title"] = "Bot Unbanned"
            embed["description"] = "Your bot is unbanned and public!"
            embed["footer"]["text"] = ""
            embed["color"] = 0x18B745

        if status != "added":
            embed["fields"].append(
                {
                    "name": "Moderator",
                    "value": f"[{bot.meta.moderator.user.first_name}#{bot.meta.moderator.tag}]"
                             f"({bot.meta.moderator.web_url})",
                },
            )

        return embed

    @staticmethod
    def server_verification(server, status):
        embed = {
                "type": "rich",
                "title": "New Server",
                "description": "New server added and is currently awaiting verification.",
                "color": 0xffcd03,
                "fields": [
                    {
                      "name": "Server",
                      "value": f"[{server.name}]({server.web_url})",
                      "inline": True
                    },
                    {
                      "name": "Owner",
                      "value": f"[{server.owner.user.first_name}#{server.owner.tag}]({server.owner.web_url})",
                      "inline": True
                    },
                    {
                      "name": "Date",
                      "value": server.date_added.strftime("%m/%d/%Y")
                    }

                ],
                "thumbnail": {
                    "url": server.icon_url,
                },
                "footer": {
                    "text": "The verification of your server can take anywhere between 1 day to 1 week.\n "\
                    "Please don't ping staff unless its beyond that period."
                }
                }

        if status == "verified":
            embed["title"] = "Server Verified"
            embed["description"] = "Your server is verified and public!"
            embed["footer"]["text"] = ""
            embed["color"] = 0x18B745
        elif status == "added":
            pass
        elif status == "rejected":
            embed["title"] = "Server Rejected"
            embed["description"] = f"Reason: {server.meta.rejection_reason}"
            embed["footer"]["text"] = f"Please make the necessary corrections and reapply\n "\
                                      f"You have {3 - server.meta.rejection_count} more attempts."
            embed["color"] = 0xf37100
        elif status == "banned":
            embed["title"] = "Server Banned"
            embed["description"] = f"Reason:  {server.meta.ban_reason}"
            embed["footer"]["text"] = "If you want to appeal. Contact staff."
            embed["color"] = 0xff0000
        elif status == "unbanned":
            embed["title"] = "Server Unbanned"
            embed["description"] = "Your server is unbanned and public!"
            embed["footer"]["text"] = ""
            embed["color"] = 0x18B745

        if status != "added":
            embed["fields"].append(
                {
                    "name": "Moderator",
                    "value": f"[{server.meta.moderator.user.first_name}#{server.meta.moderator.tag}]"
                             f"({server.meta.moderator.web_url})",
                },
            )
        return embed

    @staticmethod
    def bot_vote(bot, member):
        return {
                "type": "rich",
                "title": "Bot Up-voted",
                "color": 0x3366ff,
                "fields": [
                    {
                      "name": "Server",
                      "value": f"[{bot.name}]({bot.web_url})",
                      "inline": True
                    },
                    {
                      "name": "Votes",
                      "value": f"{bot.votes} <:vote:704268098844360714>",
                      "inline": True
                    },
                    {
                      "name": "User",
                      "value": f"[{member.user.first_name}#{member.tag}]({member.web_url})"
                    }

                ],
                "thumbnail": {
                    "url": bot.avatar_url,
                },
                }

    @staticmethod
    def server_vote(server, member):
        return {
                "type": "rich",
                "title": "Server Up-voted",
                "color": 0x3366ff,
                "fields": [
                    {
                      "name": "Server",
                      "value": f"[{server.name}]({server.web_url})",
                      "inline": True
                    },
                    {
                      "name": "Votes",
                      "value": f"{server.votes} <:vote:704268098844360714>",
                      "inline": True
                    },
                    {
                      "name": "User",
                      "value": f"[{member.user.first_name}#{member.tag}]({member.web_url})"
                    }

                ],
                "thumbnail": {
                    "url": server.icon_url,
                },
                }
