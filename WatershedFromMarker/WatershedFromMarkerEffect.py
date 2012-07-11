import os
from __main__ import vtk, qt, ctk, slicer
import EditorLib
from EditorLib.EditOptions import HelpButton
from EditorLib.EditOptions import EditOptions
from EditorLib import EditUtil


import math

#
# The Editor Extension itself.
#
# This needs to define the hooks to be come an editor effect.
#

#
# WatershedFromMarkerEffectOptions - see Effect for superclass
#

class WatershedFromMarkerEffectOptions(Effect.EffectOptions):
  """ WatershedFromMarkerEffect-specfic gui
  """

  def __init__(self, parent=0):
    super(WatershedFromMarkerEffectOptions,self).__init__(parent)


  def __del__(self):
    super(WatershedFromMarkerEffectOptions,self).__del__()

  def create(self):
    super(WatershedFromMarkerEffectOptions,self).create()

    labelVolume = self.editUtil.getLabelVolume()
    if labelVolume and labelVolume.GetImageData():
      spacing = labelVolume.GetSpacing()
      self.minimumSigma = 0.1 * min(spacing)
      self.maximumSigma = 100 * self.minimumSigma
    else:
      self.minimumSigma = 0.1
      self.maximumSigma = 10


    self.sigmaFrame = qt.QFrame(self.frame)
    self.sigmaFrame.setLayout(qt.QHBoxLayout())
    self.frame.layout().addWidget(self.sigmaFrame)
    self.widgets.append(self.sigmaFrame)

    self.sigmaLabel = qt.QLabel("Sigma", self.frame)
    self.sigmaLabel.setToolTip("Set the sigma used for edge detection.")
    self.sigmaFrame.layout().addWidget(self.sigmaLabel)
    self.widgets.append(self.sigmaLabel)

    self.sigmaSlider = qt.QSlider( qt.Qt.Horizontal, self.frame )
    self.sigmaFrame.layout().addWidget(self.sigmaSlider)
    self.widgets.append(self.sigmaSlider)

    self.sigmaSpinBox = qt.QDoubleSpinBox(self.frame)
    self.sigmaSpinBox.setToolTip("Set the sigma used for edge detection in millimeters.")
    self.sigmaSpinBox.suffix = "mm"

    self.sigmaFrame.layout().addWidget(self.sigmaSpinBox)
    self.widgets.append(self.sigmaSpinBox)

    self.sigmaSpinBox.minimum = self.minimumSigma
    self.sigmaSlider.minimum = self.minimumSigma
    self.sigmaSpinBox.maximum = self.maximumSigma
    self.sigmaSlider.maximum = self.maximumSigma

    decimals = math.floor(math.log(self.minimumSigma,10))
    if decimals < 0:
      self.sigmaSpinBox.decimals = -decimals + 2


    self.apply = qt.QPushButton("Apply", self.frame)
    self.apply.setToolTip("Apply the extension operation")

    self.frame.layout().addWidget(self.apply)
    self.widgets.append(self.apply)

    # todo
    HelpButton(self.frame, "This will be the best editor effect ever...")



    self.sigmaSlider.connect( 'valueChanged(int)', self.sigmaSpinBox.setValue )
    self.sigmaSpinBox.connect( 'valueChanged(int)', self.sigmaSlider.setValue )

    # if either widget is changed both should change and this should be triggered
    self.connections.append( ( self.sigmaSpinBox, 'valueChanged(double)', self.onSigmaValueChanged ) )

    self.connections.append( (self.apply, 'clicked()', self.onApply) )

    # Add vertical spacer
    self.frame.layout().addStretch(1)

  def destroy(self):
    super(WatershedFromMarkerEffectOptions,self).destroy()

  # note: this method needs to be implemented exactly as-is
  # in each leaf subclass so that "self" in the observer
  # is of the correct type
  def updateParameterNode(self, caller, event):
    node = EditUtil.EditUtil().getParameterNode()
    if node != self.parameterNode:
      if self.parameterNode:
        node.RemoveObserver(self.parameterNodeTag)
      self.parameterNode = node
      self.parameterNodeTag = node.AddObserver(vtk.vtkCommand.ModifiedEvent, self.updateGUIFromMRML)

  def setMRMLDefaults(self):
    super(WatershedFromMarkerEffectOptions,self).setMRMLDefaults()

    disableState = self.parameterNode.GetDisableModifiedEvent()
    self.parameterNode.SetDisableModifiedEvent(1)
    defaults = [
      ("sigma", "1.0")
    ]
    for d in defaults:
      param = "WatershedFromMarkerEffect,"+d[0]
      pvalue = self.parameterNode.GetParameter(param)
      if pvalue == '':
        self.parameterNode.SetParameter(param, d[1])

    self.parameterNode.SetDisableModifiedEvent(disableState)


  def updateGUIFromMRML(self,caller,event):
    self.updatingGUI = True
    super(WatershedFromMarkerEffectOptions,self).updateGUIFromMRML(caller,event)
    self.updatingGUI = False

  def onApply(self):
    logic = WatershedFromMarkerEffectLogic( self.editUtil.getSliceLogic() )
    logic.undoRedo = self.undoRedo

    logic.sigma = float( self.sigmaSpinBox.value )

    logic.doit()

  def onSigmaValueChanged(self, sigma):

    self.updateMRMLFromGUI()

  def updateMRMLFromGUI(self):
    disableState = self.parameterNode.GetDisableModifiedEvent()
    self.parameterNode.SetDisableModifiedEvent(1)
    super(WatershedFromMarkerEffectOptions,self).updateMRMLFromGUI()
    self.parameterNode.SetDisableModifiedEvent(disableState)
    if not disableState:
      self.parameterNode.InvokePendingModifiedEvent()

#
# WatershedFromMarkerEffectTool
#

class WatershedFromMarkerEffectTool(LabelEffect.LabelEffectTool):
  """
  One instance of this will be created per-view when the effect
  is selected.  It is responsible for implementing feedback and
  label map changes in response to user input.
  This class observes the editor parameter node to configure itself
  and queries the current view for background and label volume
  nodes to operate on.
  """

  def __init__(self, sliceWidget):
    super(WatershedFromMarkerEffectTool,self).__init__(sliceWidget)

  def cleanup(self):
    super(WatershedFromMarkerEffectTool,self).cleanup()

  def processEvent(self, caller=None, event=None):
    """
    handle events from the render window interactor
    """
    pass


#
# WatershedFromMarkerEffectLogic
#

class WatershedFromMarkerEffectLogic(LabelEffect.LabelEffectLogic):
  """
  This class contains helper methods for a given effect
  type.  It can be instanced as needed by an WatershedFromMarkerEffectTool
  or WatershedFromMarkerEffectOptions instance in order to compute intermediate
  results (say, for user feedback) or to implement the final
  segmentation editing operation.  This class is split
  from the WatershedFromMarkerEffectTool so that the operations can be used
  by other code without the need for a view context.
  """

  def __init__(self,sliceLogic):
    self.sliceLogic = sliceLogic

    self.sigma = 1.0

  def apply(self,xy):
    pass


  def doit(self):

    print(" running with sigma parameter ", self.sigma )

    labelLogic = self.sliceLogic.GetLabelLayer()
    labelNode = labelLogic.GetVolumeNode()
    labelNodeName = labelNode.GetName()
    labelImage = sitk.ReadImage( sitkUtils.GetSlicerITKReadWriteAddress( labelNodeName ) )


    backgroundLogic = self.sliceLogic.GetBackgroundLayer()
    backgroundNode = backgroundLogic.GetVolumeNode()
    backgroundNodeName = backgroundNode.GetName()
    backgroundImage = sitk.ReadImage( sitkUtils.GetSlicerITKReadWriteAddress( backgroundNodeName ) )

    # store a backup copy of the label map for undo
    # (this happens in it's own thread, so it is cheap)
    if self.undoRedo:
      self.undoRedo.saveState()

    featureImage = sitk.GradientMagnitudeRecursiveGaussian( backgroundImage, float(self.sigma) );
    f = sitk.MorphologicalWatershedFromMarkersImageFilter()
    f.SetMarkWatershedLine( False )
    f.SetFullyConnected( False )
    sitk.WriteImage( sitk.Cast( f.Execute( featureImage, labelImage ), sitk.sitkUInt16 ), sitkUtils.GetSlicerITKReadWriteAddress( labelNodeName ) )
    labelNode.GetImageData().Modified()
    labelNode.Modified()

#
# The WatershedFromMarkerEffectExtension class definition
#

class WatershedFromMarkerEffectExtension(Effect.Effect):
  """Organizes the Options, Tool, and Logic classes into a single instance
  that can be managed by the EditBox
  """

  def __init__(self):
    # name is used to define the name of the icon image resource (e.g. WatershedFromMarkerEffect.png)
    self.name = "WatershedFromMarkerEffect"
    # tool tip is displayed on mouse hover
    self.toolTip = "Paint: circular paint brush for label map editing"

    self.options = WatershedFromMarkerEffectOptions
    self.tool = WatershedFromMarkerEffectTool
    self.logic = WatershedFromMarkerEffectLogic

""" Test:

sw = slicer.app.layoutManager().sliceWidget('Red')
import EditorLib
pet = EditorLib.WatershedFromMarkerEffectTool(sw)

"""

#
# WatershedFromMarkerEffect
#

class WatershedFromMarkerEffect:
  """
  This class is the 'hook' for slicer to detect and recognize the extension
  as a loadable scripted module
  """
  def __init__(self, parent):
    parent.title = "Editor WatershedFromMarkerEffect Effect"
    parent.categories = ["Developer Tools.Editor Extensions"]
    parent.contributors = ["Bradley Lowekamp"]
    parent.helpText = """
    Grow labels to distinguishing boundaries. This used ITK's MorphologicalWatershedFromMarkersImageFilter.
    """
    parent.acknowledgementText = """
    This editor extension was developed by
    Bradley Lowekamp, National Library of Medicine (C)
    based on work by:
    Steve Pieper, Isomics, Inc.
    based on work by:
    Jean-Christophe Fillion-Robin, Kitware Inc.
    and was partially funded by NIH grant 3P41RR013218.
    """

    # Add this extension to the editor's list for discovery when the module
    # is created.  Since this module may be discovered before the Editor itself,
    # create the list if it doesn't already exist.
    try:
      slicer.modules.editorExtensions
    except AttributeError:
      slicer.modules.editorExtensions = {}
    slicer.modules.editorExtensions['WatershedFromMarkerEffect'] = WatershedFromMarkerEffectExtension

#
# WatershedFromMarkerEffectWidget
#

class WatershedFromMarkerEffectWidget:
  def __init__(self, parent = None):
    self.parent = parent

  def setup(self):
    # don't display anything for this widget - it will be hidden anyway
    pass

  def enter(self):
    pass

  def exit(self):
    pass
