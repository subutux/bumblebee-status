"""Displays bluetooth status (Bluez). Left mouse click launches manager app,
right click toggles bluetooth. Needs dbus-send to toggle bluetooth state.

Parameters:
    * bluetooth.device : the device to read state from (default is hci0)
    * bluetooth.manager : application to launch on click (blueman-manager)

"""


import os
import re
import bumblebee.input
import bumblebee.output
import bumblebee.engine
import bumblebee.util
import bumblebee.popup
import logging
import dbus


class Module(bumblebee.engine.Module):
    """Bluetooth module."""

    def __init__(self, engine, config):
        """Initialize."""
        super(Module, self).__init__(engine, config,
                                     bumblebee.output.Widget(
                                         full_text=self.status))

        device = self.parameter("device", "hci0")
        self.manager = self.parameter("manager", "blueman-manager")
        self._status = "Off"

        engine.input.register_callback(self, button=bumblebee.input.LEFT_MOUSE,
                                       cmd=self.manager)
        engine.input.register_callback(self,
                                       button=bumblebee.input.RIGHT_MOUSE,
                                       cmd=self.popup)
        dbusSystem = dbus.SystemBus()
        bluez = dbusSystem.get_object('org.bluez', "/org/bluez/{device}"
                                                   .format(device=device))
        self.dbus = dbus.Interface(bluez, 'org.freedesktop.DBus.Properties')

    def status(self, widget):
        """Get status."""
        return self._status

    def update(self, widgets):
        """Update current state."""
        try:
            status = bool(self.dbus.Get("org.bluez.Adapter1", 'Powered'))
            self._status = "On" if status else "Off"
        except Exception:
            self._status = "?"

    def manager(self, widget):
        """Launch manager."""
        bumblebee.util.execute(self.manager)

    def popup(self, widget):
        """Show a popup menu."""
        menu = bumblebee.popup.PopupMenu()
        if self._status == "On":
            menu.add_menuitem('Disable Bluetooth')
        elif self._status == "Off":
            menu.add_menuitem('Enable Bluetooth')
        else:
            return

        # show menu and get return code
        ret = menu.show(widget)
        if ret == 0:
            logging.debug('bt: toggling bluetooth')
            # first (and only) item selected.
            self._toggle()

    def _toggle(self):
        """Toggle bluetooth state."""
        if self._status == "On":
            state = False
        else:
            state = True

        self.dbus.Set('org.bluez.Adapter1', 'Powered', state)

    def state(self, widget):
        """Get current state."""
        state = []

        if self._status == "?":
            state = ["unknown"]
        elif self._status == "On":
            state = ["ON"]
        else:
            state = ["OFF"]

        return state
