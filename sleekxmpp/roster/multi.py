"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010  Nathanael C. Fritz
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

from sleekxmpp.xmlstream import JID
from sleekxmpp.roster import RosterNode


class Roster(object):

    """
    SleekXMPP's roster manager.

    The roster is divided into "nodes", where each node is responsible
    for a single JID. While the distinction is not strictly necessary
    for client connections, it is a necessity for components that use
    multiple JIDs.

    Rosters may be stored and persisted in an external datastore. An
    interface object to the datastore that loads and saves roster items may
    be provided. See the documentation for the RosterItem class for the
    methods that the datastore interface object must provide.

    Attributes:
        xmpp           -- The main SleekXMPP instance.
        db             -- Optional interface object to an external datastore.
        auto_authorize -- Default auto_authorize value for new roster nodes.
                          Defaults to True.
        auto_subscribe -- Default auto_subscribe value for new roster nodes.
                          Defaults to True.

    Methods:
        add -- Create a new roster node for a JID.
    """

    def __init__(self, xmpp, db=None):
        """
        Create a new roster.

        Arguments:
            xmpp -- The main SleekXMPP instance.
            db   -- Optional interface object to a datastore.
        """
        self.xmpp = xmpp
        self.db = db
        self.auto_authorize = True
        self.auto_subscribe = True
        self._rosters = {}

        if self.db:
            for node in self.db.entries(None, {}):
                self.add(node)

    def __getitem__(self, key):
        """
        Return the roster node for a JID.

        A new roster node will be created if one
        does not already exist.

        Arguments:
            key -- Return the roster for this JID.
        """
        if isinstance(key, JID):
            key = key.bare
        if key not in self._rosters:
            self.add(key)
            self._rosters[key].auto_authorize = self.auto_authorize
            self._rosters[key].auto_subscribe = self.auto_subscribe
        return self._rosters[key]

    def keys(self):
        """Return the JIDs managed by the roster."""
        return self._rosters.keys()

    def __iter__(self):
        """Iterate over the roster nodes."""
        return self._rosters.__iter__()

    def add(self, node):
        """
        Add a new roster node for the given JID.

        Arguments:
            node -- The JID for the new roster node.
        """
        if isinstance(node, JID):
            node = node.bare
        if node not in self._rosters:
            self._rosters[node] = RosterNode(self.xmpp, node, self.db)

    def set_backend(self, db=None):
        """
        Set the datastore interface object for the roster.

        Arguments:
            db -- The new datastore interface.
        """
        self.db = db
        for node in self.db.entries(None, {}):
            self.add(node)
        for node in self._rosters:
            self._rosters[node].set_backend(db)

    def reset(self):
        """
        Reset the state of the roster to forget any current
        presence information. Useful after a disconnection occurs.
        """
        for node in self:
            self[node].reset()