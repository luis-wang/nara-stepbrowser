#!/usr/bin/env python

import gc

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QLabel, QSlider, QComboBox
from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import Qt

import numpy
from numpy import arange, sin, pi

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

import networkx as NX

##user defined
from graphTest import GraphTest
from graphTestNumpy import GraphTestNumPy
from graphHierarchy import GraphHierarchy
from graphHierarchy1 import GraphHierarchy1
from graphCoOccurence import GraphCoOccurence
from graphCoOccurence1 import GraphCoOccurence1
#from graphContext import *


class BrowserMatPlotFrame(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.status_bar = parent.status_bar

        #State
        self.draw_node_labels_tf = False
        self.draw_axis_units_tf = False
        self.draw_grid_tf = False
        self.g = None

        #PATH used in drawing STEP hierarchy, co-occurence, context
        self.step_path = parent.step_path
        
        #MPL figure
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.fig.subplots_adjust(left=0,right=1,top=1,bottom=0)
        
        #QT canvas
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.canvas.mpl_connect('pick_event', self.on_pick) #used when selecting canvas objects
        self.canvas.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding) 
        
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(False) #clear the axes every time plot() is called

        self.mpl_toolbar = NavigationToolbar(self.canvas, self)

        #GUI controls
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Graph Test", 
                                  "Graph Test Numpy", 
                                  "STEP Hierarchy", 
                                  "STEP Hierarchy1", 
                                  "STEP Co-occurence",
                                  "STEP Co-occurence1",
                                  "STEP Context"])
        self.mode_combo.setMinimumWidth(200)
        
        self.draw_button = QPushButton("&Draw")
        self.connect(self.draw_button, QtCore.SIGNAL('clicked()'), self.on_draw)
        
        self.slider_label = QLabel('Node Size (%):')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(50)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        # slider connection set in on_draw() method

        #Horizontal layout
        hbox = QtGui.QHBoxLayout()
    
        #Adding matplotlib widgets
        for w in [self.mode_combo, self.slider_label, self.slider, self.draw_button]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)

        #Vertical layout. Adding all other widgets, and hbox layout.
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        
    def draw_axis_units(self):

        fw = self.fig.get_figwidth()
        fh = self.fig.get_figheight()

        l_margin = .4 / fw #.4in
        b_margin = .3 / fh #.3in

        if self.draw_axis_units_tf == True:
            self.fig.subplots_adjust(left=l_margin,right=1,top=1,bottom=b_margin)
        else: 
            self.fig.subplots_adjust(left=0,right=1,top=1,bottom=0)

        self.canvas.draw()

    def draw_grid(self):
        if self.draw_grid_tf == False:
            self.draw_grid_tf = True
        else:
            self.draw_grid_tf = False
            
        self.axes.grid(self.draw_grid_tf)
        self.canvas.draw()
			
    def on_draw(self): 
        draw_mode = self.mode_combo.currentText()
        
        self.axes.clear()
        if self.g != None:
            if hasattr(self.g, 'destruct'):
                self.g.destruct(self.g)
                self.g = None

        if draw_mode == "Graph Test":
            self.g = GraphTest(self)
        elif draw_mode == "Graph Test Numpy":
            self.g = GraphTestNumPy(self)
        elif draw_mode == "STEP Hierarchy":
            self.g = GraphHierarchy(self)
        elif draw_mode == "STEP Hierarchy1":
            self.g = GraphHierarchy1(self)
        elif draw_mode == "STEP Co-occurence":
            self.g = GraphCoOccurence(self)
        elif draw_mode == "STEP Co-occurence1":
            self.g = GraphCoOccurence1(self)

        self.connect(self.slider, QtCore.SIGNAL('valueChanged(int)'), self.g.set_node_mult)       
        self.axes.grid(self.draw_grid_tf)
        self.canvas.draw()
        
    def on_pick(self, args):
        print "in matplotframe: ", args

    def resizeEvent(self, ev):
        self.draw_axis_units()
        
    def set_step_path(self, path):
        self.step_path = path
        self.parent.set_step_path(path)

    def toggle_axis_units(self):
        if self.draw_axis_units_tf == False: 
            self.draw_axis_units_tf = True
        else:
            self.draw_axis_units_tf = False
        self.draw_axis_units()

    def toggle_node_labels(self):
        if self.draw_node_labels_tf == False: 
            self.draw_node_labels_tf = True
        else:
            self.draw_node_labels_tf = False

        if self.g != None:
            self.g.redraw(self.g)
