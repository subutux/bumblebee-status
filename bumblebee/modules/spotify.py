# pylint: disable=C0111,R0903

"""Displays the current song being played
Requires the following library:
    * python-dbus
Parameters:
    * spotify.format:   Format string (defaults to "{artist} - {title}")
                        Available values are: {album}, {title}, {artist}, {trackNumber}, {playbackStatus}
    * spotify.previous: Change binding for previous song (default is left click)
    * spotify.next:     Change binding for next song (default is right click)
    * spotify.pause:    Change binding for toggling pause (default is middle click)
    Available options for spotify.previous, spotify.next and spotify.pause are:
        LEFT_CLICK, RIGHT_CLICK, MIDDLE_CLICK, SCROLL_UP, SCROLL_DOWN
"""

import sys

import bumblebee.input
import bumblebee.output
import bumblebee.engine

from bumblebee.output import scrollable

try:
    import dbus
except ImportError:
    pass


class Module(bumblebee.engine.Module):
    def __init__(self, engine, config):
        super(Module, self).__init__(engine, config,
                                     bumblebee.output.Widget(full_text=self.spotify)
                                     )
        buttons = {"LEFT_CLICK":bumblebee.input.LEFT_MOUSE,
                   "RIGHT_CLICK":bumblebee.input.RIGHT_MOUSE,
                   "MIDDLE_CLICK":bumblebee.input.MIDDLE_MOUSE,
                   "SCROLL_UP":bumblebee.input.WHEEL_UP,
                   "SCROLL_DOWN":bumblebee.input.WHEEL_DOWN,
                   }

        self._song = ""
        self._format = self.parameter("format", "{artist} - {title}")
        prev_button = self.parameter("previous", "LEFT_CLICK")
        next_button = self.parameter("next", "RIGHT_CLICK")
        pause_button = self.parameter("pause", "MIDDLE_CLICK")
        player = self.parameter("player", "spotify")
        sessionBus = dbus.SessionBus()
        self.mediaBus = sessionBus.get_object("org.mpris.MediaPlayer2.{player}"
                                              .format(player=player),
                                              "/org/mpris/MediaPlayer2")
        controls = dbus.Interface(self.mediaBus,
                                  "org.mpris.MediaPlayer2.Player")

        engine.input.register_callback(self, button=buttons[prev_button],
                                       cmd=controls.Previous)
        engine.input.register_callback(self, button=buttons[next_button],
                                       cmd=controls.Next)
        engine.input.register_callback(self, button=buttons[pause_button],
                                       cmd=controls.PlayPause)

    @scrollable
    def spotify(self, widget):
        return self.string_song

    def hidden(self):
        return self.string_song == ""

    def update(self, widgets):
        try:
            propertiesBus = dbus.Interface(self.mediaBus,
                                           "org.freedesktop.DBus.Properties")
            props = propertiesBus.Get("org.mpris.MediaPlayer2.Player",
                                      "Metadata")
            status = str(propertiesBus.Get("org.mpris.MediaPlayer2.Player",
                                           "PlaybackStatus"))
            if status == "Playing":
                playbackStatus = u"\u25B6"
            elif status == "Paused":
                playbackStatus = u"\u258D\u258D"
            else:
                playbackStatus = ""

            album = str(props.get('xesam:album'))
            title = str(props.get('xesam:title'))
            artist = ','.join(props.get('xesam:artist'))
            trackNumber = str(props.get('xesam:trackNumber'))
            self._song = self._format.format(album=album,
                                             title=title,
                                             artist=artist,
                                             trackNumber=trackNumber,
                                             playbackStatus=playbackStatus,)

        except Exception:
            self._song = ""

    @property
    def string_song(self):
        if sys.version_info.major < 3:
            return unicode(self._song)
        return str(self._song)


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
