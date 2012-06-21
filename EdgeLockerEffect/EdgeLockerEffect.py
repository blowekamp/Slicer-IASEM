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
# EdgeLockerEffectOptions - see Effect for superclass
#

class EdgeLockerEffectOptions(Effect.EffectOptions):
  """ EdgeLockerEffect-specfic gui
  """

  def __init__(self, parent=0):
    super(EdgeLockerEffectOptions,self).__init__(parent)


  def __del__(self):
    super(EdgeLockerEffectOptions,self).__del__()

  def create(self):
    super(EdgeLockerEffectOptions,self).create()

    self.minimumSigma = .1
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

    self.apply.connect('clicked()', self.onApply)

    # Add vertical spacer
    self.frame.layout().addStretch(1)

  def destroy(self):
    super(EdgeLockerEffectOptions,self).destroy()

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
    super(EdgeLockerEffectOptions,self).setMRMLDefaults()

  def updateGUIFromMRML(self,caller,event):
    self.updatingGUI = True
    super(EdgeLockerEffectOptions,self).updateGUIFromMRML(caller,event)
    self.updatingGUI = False

  def onApply(self):
    logic = EdgeLockerEffectLogic( self.editUtil.getSliceLogic() )
    logic.undoRedo = self.undoRedo
    logic.doit()

  def updateMRMLFromGUI(self):
    if self.updatingGUI:
      return
    disableState = self.parameterNode.GetDisableModifiedEvent()
    self.parameterNode.SetDisableModifiedEvent(1)
    super(EdgeLockerEffectOptions,self).updateMRMLFromGUI()
    self.parameterNode.SetDisableModifiedEvent(disableState)
    if not disableState:
      self.parameterNode.InvokePendingModifiedEvent()

#
# EdgeLockerEffectTool
#

class EdgeLockerEffectTool(LabelEffect.LabelEffectTool):
  """
  One instance of this will be created per-view when the effect
  is selected.  It is responsible for implementing feedback and
  label map changes in response to user input.
  This class observes the editor parameter node to configure itself
  and queries the current view for background and label volume
  nodes to operate on.
  """

  def __init__(self, sliceWidget):
    super(EdgeLockerEffectTool,self).__init__(sliceWidget)

  def cleanup(self):
    super(EdgeLockerEffectTool,self).cleanup()

  def processEvent(self, caller=None, event=None):
    """
    handle events from the render window interactor
    """
    if event == "LeftButtonPressEvent":
      xy = self.interactor.GetEventPosition()
      sliceLogic = self.sliceWidget.sliceLogic()
      logic = EdgeLockerEffectLogic(sliceLogic)
      logic.apply(xy)
      print("Got a %s at %s in %s", (event,str(xy),self.sliceWidget.sliceLogic().GetSliceNode().GetName()))
      self.abortEvent(event)
    else:
      pass


#
# EdgeLockerEffectLogic
#

class EdgeLockerEffectLogic(LabelEffect.LabelEffectLogic):
  """
  This class contains helper methods for a given effect
  type.  It can be instanced as needed by an EdgeLockerEffectTool
  or EdgeLockerEffectOptions instance in order to compute intermediate
  results (say, for user feedback) or to implement the final
  segmentation editing operation.  This class is split
  from the EdgeLockerEffectTool so that the operations can be used
  by other code without the need for a view context.
  """

  def __init__(self,sliceLogic):
    self.sliceLogic = sliceLogic

  def apply(self,xy):
    pass


  def doit(self):

    sigma = 1.0

    labelLogic = self.sliceLogic.GetLabelLayer()
    labelNode = labelLogic.GetVolumeNode()
    labelNodeName = labelNode.GetName()
    labelImage = sitk.ReadImage( sitkUtils.GetSlicerITKReadWriteAddress( labelNodeName ) )


    backgroundLogic = self.sliceLogic.GetBackgroundLayer()
    backgroundNode = backgroundLogic.GetVolumeNode()
    backgroundNodeName = backgroundNode.GetName()
    backgroundImage = sitk.ReadImage( sitkUtils.GetSlicerITKReadWriteAddress( backgroundNodeName ) )

    featureImage = sitk.GradientMagnitudeRecursiveGaussian( backgroundImage, sigma );
    f = sitk.MorphologicalWatershedFromMarkersImageFilter()
    f.SetMarkWatershedLine( False )
    f.SetFullyConnected( False )
    sitk.WriteImage( f.Execute( featureImage, labelImage ), sitkUtils.GetSlicerITKReadWriteAddress( labelNodeName ) )
    labelNode.GetImageData().Modified()
    labelNode.Modified()

#
# The EdgeLockerEffectExtension class definition
#

class EdgeLockerEffectExtension(Effect.Effect):
  """Organizes the Options, Tool, and Logic classes into a single instance
  that can be managed by the EditBox
  """

  def __init__(self):
    # name is used to define the name of the icon image resource (e.g. EdgeLockerEffect.png)
    self.name = "EdgeLockerEffect"
    # tool tip is displayed on mouse hover
    self.toolTip = "Paint: circular paint brush for label map editing"

    self.options = EdgeLockerEffectOptions
    self.tool = EdgeLockerEffectTool
    self.logic = EdgeLockerEffectLogic

""" Test:

sw = slicer.app.layoutManager().sliceWidget('Red')
import EditorLib
pet = EditorLib.EdgeLockerEffectTool(sw)

"""

#
# EdgeLockerEffect
#

class EdgeLockerEffect:
  """
  This class is the 'hook' for slicer to detect and recognize the extension
  as a loadable scripted module
  """
  def __init__(self, parent):
    parent.title = "Editor EdgeLockerEffect Effect"
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
    slicer.modules.editorExtensions['EdgeLockerEffect'] = EdgeLockerEffectExtension

#
# EdgeLockerEffectWidget
#

class EdgeLockerEffectWidget:
  def __init__(self, parent = None):
    self.parent = parent

  def setup(self):
    # don't display anything for this widget - it will be hidden anyway
    pass

  def enter(self):
    pass

  def exit(self):
    pass
