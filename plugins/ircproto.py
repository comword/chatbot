#!/usr/bin/env /usr/bin/python3
import main
import lang
import config
m_conf=config.get_plgconf("ircproto")

from irc3.plugins.command import command
import irc3

@irc3.plugin
class MyPlugin:
    requires = [
        'irc3.plugins.core',
        'irc3.plugins.userlist',
        'irc3.plugins.command',
        'irc3.plugins.human',
    ]
    def __init__(self, bot):
        self.bot = bot
        self.log = self.bot.log
#    def connection_made(self):
#        """triggered when connection is up"""

#    def server_ready(self):
#        """triggered after the server sent the MOTD (require core plugin)"""

#    def connection_lost(self):
#        """triggered when connection is lost"""

    @irc3.event(irc3.rfc.JOIN)
    def welcome(self, mask, channel, **kw):
        """Welcome people who join a channel"""
        if mask.nick != self.bot.nick:
            self.bot.call_with_human_delay(
                self.bot.privmsg, channel, 'Welcome %s!' % mask.nick)
        else:
            self.bot.call_with_human_delay(
                self.bot.privmsg, channel, "Hi guys!")

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_privmsg(self, mask=None, data=None, **kw):
        print(self.chater, mask, data)
        if self.chater:
            self.chater.privmsg(self.chater.config.channel,'{0}: {1}'.format(mask.nick, data))

#    @command
#    def echo(self, mask, target, args):
#        """Echo command
#            %%echo <words>...
#        """
#        self.bot.privmsg(mask.nick, ' '.join(args['<words>']))

#    @command
#    def stats(self, mask, target, args):
#        """Show stats of the channel using the userlist plugin
#            %%stats [<channel>]
#        """
#        if args['<channel>']:
#            channel = args['<channel>']
#            target = mask.nick
#        else:
#            channel = target
#        if channel in self.bot.channels:
#            channel = self.bot.channels[channel]
#            message = '{0} users'.format(len(channel))
#            for mode, nicknames in sorted(channel.modes.items()):
#                message += ' - {0}({1})'.format(mode, len(nicknames))
#            self.bot.privmsg(target, message)

#    @irc3.extend
#    def my_usefull_method(self):
#        """The extend decorator will allow you to call::
#            bot.my_usefull_method()
#        """

def main():
    # instanciate a bot
    config = dict(
        nick=m_conf["nick"], autojoins=m_conf["autojoins"],
        host=m_conf["host"], port=m_conf["port"], ssl=m_conf["ssl"],
        includes=[
            'irc3.plugins.core',
            'irc3.plugins.command',
            'irc3.plugins.human',
            __name__,  # this register MyPlugin
            ]
    )
    bot = irc3.IrcBot.from_config(config)
    bot.run(forever=True)

if __name__ == '__main__':
    main()
