# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PegelOnlineDisplayer
                                 A QGIS plugin
 Show information about different measurement stations
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-08-22
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Benedikt Lüken-Winkels
        email                : s4beluek@uni-trier.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import (QSettings, QTranslator,
                              QCoreApplication, Qt)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QInputDialog
# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .pegel_online_displayer_dockwidget import PegelOnlineDisplayerDockWidget
import os.path

from .po_runner import PoRunner


class PegelOnlineDisplayer:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PegelOnlineDisplayer_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Pegel Online Displayer')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PegelOnlineDisplayer')
        self.toolbar.setObjectName(u'PegelOnlineDisplayer')

        #print "** INITIALIZING PegelOnlineDisplayer"

        self.pluginIsActive = False
        self.dockwidget = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PegelOnlineDisplayer', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        assets_path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "assets")

        # Add Widget
        self.add_action(
            os.path.join(assets_path, "icon.png"),
            text=self.tr(u'Dock-Widget anzeigen'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # Add How To Dialog
        self.add_action(
            os.path.join(assets_path, "iconHowTo.png"),
            text=self.tr(u'How To'),
            callback=self.showHowTo,
            parent=self.iface.mainWindow())

        # Add About dialog
        self.add_action(
            os.path.join(assets_path, "iconAbout.png"),
            text=self.tr(u'Über'),
            callback=self.showAbout,
            parent=self.iface.mainWindow())
    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD PegelOnlineDisplayer"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Pegel Online Displayer'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:

            # Select position of Dockwidget
            options = ("links", "rechts", "oben", "unten")
            posString, ok = QInputDialog.getItem(None,
                                                "Pegel Online Dock-Widget",
                                                "Wo soll angedockt werden?",
                                                options, 0, False)

            # If Abbrechen is chosen, then abort
            if ok == False:
                return


            self.pluginIsActive = True

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = PegelOnlineDisplayerDockWidget()
                self.runner = PoRunner(self.dockwidget, self.iface)


            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            pos = Qt.LeftDockWidgetArea

            if posString == "links":
                pos = Qt.LeftDockWidgetArea
            elif posString == "rechts":
                pos = Qt.RightDockWidgetArea
            elif posString == "oben":
                pos = Qt.TopDockWidgetArea
            elif posString == "unten":
                pos = Qt.BottomDockWidgetArea

            # show the dockwidget
            self.iface.addDockWidget(pos, self.dockwidget)
            self.dockwidget.show()

    def showHowTo(self):
        """Shows a message box with usage instructions"""

        content = """<h3>How To Pegel Online Displayer</h3>
            Im Pegel Online Displayer Widget gibt es drei Sektionen:
            <h4>Toolbox</h4>
            Auf der linken Seite finden sich verschiedene <strong>Auswahl- und Zoomtools</strong>
            für das jeweils ausgewählte Layer. <br/> Nachdem in einem der Tabs des Layermanagement
            entweder die Wasserstände oder die Stationen geladen wurden und eines dieser
            Layer ausgewählt ist, ist die <strong>Suchleiste</strong> auf der rechten Seite
            verfügbar. Hier können Stationen nach ihrem Namen gesucht werden. Nachdem eine
            der vorgeschlagenen Stationen ausgewählt wurde, kann mit ENTER bestätigt werden
            und es wird auf die ausgewählte Station gezoomt und diese ist in der
            Graphanzeige verfügbar.
            <hr>
            <h4>Layermanagement</h4>
            Das Layermanagement ist in Tabs aufgeteilt, in denen jeweils verschiedene
            Funktionen für die Layer verfügbar sind:
            <br><strong>Allgemein</strong><br>
            An- und Ausschalten der Basiskarte deutscher Gewässer
            <br><strong>Wasserstände</strong><br>
            Laden der Daten der Wasserstände von Pegel Online, Anzeigen verschiedener
            Datensätze und Entwicklung des Wasserstandes, An- und Ausschalten und Auswahl
            verschiedener Labels
            <br><strong>Stationen</strong><br>
            Laden von Stationen von Pegel Online
            <hr>
            <h4>Graphanzeige</h4>
            Im Stationen Dropdown können zunächst alle, dann die aktuell im Layer markierten
            Stationen ausgewählt werden. Zu diesen Stationen kann dann der Verlaufsgraph
            des Wasserstandes der letzte 1-30 Tage geladen werden.
            <hr>
        """
        howto = QMessageBox.information(None, "How To", content)


    def showAbout(self):
        """Shows a message box with information about the plugin"""

        content = """<h3>Über</h3>
            Mit dem Pegel Online Displayer können Daten der Messstationen an
            deutschen Gewässern werden. Die Daten werden von der
            <a href="https://www.pegelonline.wsv.de">Wasserstraßen- und Schifffahrtsverwaltung des Bundes </a>
            über eine Rest-API bereitgestellt und sind frei verfügbar. <br/>
            Der Code für das Plugin kann <a href="https://github.com/BeneLuWi/gis">hier</a>
            eingesehen werden.
        """
        howto = QMessageBox.information(
                    None,
                    "Über Pegel Online Displayer",
                    content)






