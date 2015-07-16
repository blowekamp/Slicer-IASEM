import os
from __main__ import vtk, qt, ctk, slicer
import EditorLib
from EditorLib.EditOptions import HelpButton
from EditorLib.EditUtil import EditUtil
from EditorLib import Effect

HAVE_SIMPLEITK=True
try:
  import SimpleITK as sitk
  import sitkUtils
except ImportError:
  HAVE_SIMPLEITK=False

__all__ = [
  "BinaryWatershedEffectOptions",
  "BinaryWatershedEffectTool",
  "BinaryWatershedEffectLogic",
  "BinaryWatershedEffectExtension",
  "BinaryWatershedEffect"
  ]

#
# The Editor Extension itself.
#
# This needs to define the hooks to be come an editor effect.
#

#
# BinaryWatershedEffectOptions - see LabelEffect, EditOptions and Effect for superclasses
#

class BinaryWatershedEffectOptions(Effect.EffectOptions):
  """ BinaryWatershedEffect-specfic gui
  """

  def __init__(self, parent=0):
    super(BinaryWatershedEffectOptions,self).__init__(parent)

  def __del__(self):
    super(BinaryWatershedEffectOptions,self).__del__()

  def create(self):

    super(BinaryWatershedEffectOptions,self).create()

    if not HAVE_SIMPLEITK:
      self.warningLabel = qt.QLabel()
      self.warningLabel.text = "BinaryWatershed is not available because\nSimpleITK is not available in this build"
      self.widgets.append(self.warningLabel)
      self.frame.layout().addWidget(self.warningLabel)
      return

    self.apply = qt.QPushButton("Apply", self.frame)
    self.apply.setToolTip("Apply the binary watershed operation")
    self.frame.layout().addWidget(self.apply)
    self.widgets.append(self.apply)

    helpDoc = """This is a sample with no real functionality."""

    HelpButton(self.frame, helpDoc)

    self.apply.connect('clicked()', self.onApply)

    # Add vertical spacer
    self.frame.layout().addStretch(1)

  def destroy(self):
    super(BinaryWatershedEffectOptions,self).destroy()

  # note: this method needs to be implemented exactly as-is
  # in each leaf subclass so that "self" in the observer
  # is of the correct type
  def updateParameterNode(self, caller, event):
    node = self.editUtil.getParameterNode()
    if node != self.parameterNode:
      if self.parameterNode:
        node.RemoveObserver(self.parameterNodeTag)
      self.parameterNode = node
      self.parameterNodeTag = node.AddObserver(vtk.vtkCommand.ModifiedEvent, self.updateGUIFromMRML)

  def setMRMLDefaults(self):
    super(BinaryWatershedEffectOptions,self).setMRMLDefaults()

  def updateGUIFromMRML(self,caller,event):
    self.updatingGUI = True
    super(BinaryWatershedEffectOptions,self).updateGUIFromMRML(caller,event)
    self.updatingGUI = False

  def onApply(self):
    logic = BinaryWatershedEffectLogic( EditUtil.getSliceLogic() )
    logic.undoRedo = self.undoRedo

    logic.doit()

  def updateMRMLFromGUI(self):
    if self.updatingGUI:
      return
    disableState = self.parameterNode.GetDisableModifiedEvent()
    self.parameterNode.SetDisableModifiedEvent(1)
    super(BinaryWatershedEffectOptions,self).updateMRMLFromGUI()
    self.parameterNode.SetDisableModifiedEvent(disableState)
    if not disableState:
      self.parameterNode.InvokePendingModifiedEvent()


#
# BinaryWatershedEffectTool
#

class BinaryWatershedEffectTool(Effect.EffectTool):
  """
  One instance of this will be created per-view when the effect
  is selected.  It is responsible for implementing feedback and
  label map changes in response to user input.
  This class observes the editor parameter node to configure itself
  and queries the current view for background and label volume
  nodes to operate on.
  """

  def __init__(self, sliceWidget):
    super(BinaryWatershedEffectTool,self).__init__(sliceWidget)

  def cleanup(self):
    super(BinaryWatershedEffectTool,self).cleanup()

  def processEvent(self, caller=None, event=None):
    """
    handle events from the render window interactor
    """
    pass


#
# BinaryWatershedEffectLogic
#

class BinaryWatershedEffectLogic(Effect.EffectLogic):
  """
  This class contains helper methods for a given effect
  type.  It can be instanced as needed by an BinaryWatershedEffectTool
  or BinaryWatershedEffectOptions instance in order to compute intermediate
  results (say, for user feedback) or to implement the final
  segmentation editing operation.  This class is split
  from the BinaryWatershedEffectTool so that the operations can be used
  by other code without the need for a view context.
  """

  def __init__(self,sliceLogic):
    super(BinaryWatershedEffectLogic,self).__init__(sliceLogic)

  def apply(self,xy):
    pass

  def doit(self):

    labelLogic = self.sliceLogic.GetLabelLayer()
    labelNode = labelLogic.GetVolumeNode()
    labelNodeName = labelNode.GetName()
    labelImage = sitk.ReadImage( sitkUtils.GetSlicerITKReadWriteAddress( labelNodeName ) )

    # store a backup copy of the label map for undo
    # (this happens in it's own thread, so it is cheap)
    if self.undoRedo:
      self.undoRedo.saveState()

    labelID = self.editUtil.getLabel()
    level = 1

    l = sitk.BinaryThreshold( labelImage, labelID, labelID, 1, 0 )

    filled = sitk.BinaryFillhole( l )


    d = sitk.SignedMaurerDistanceMap( filled,
                                      insideIsPositive = False,
                                      squaredDistance = False,
                                      useImageSpacing = True )
    del filled

    d = sitk.Threshold( d, -1e23, 0, 0 )


    ws = sitk.MorphologicalWatershed( d, markWatershedLine=False, level = level )
    del d

    ws = sitk.Mask( sitk.Cast( ws, labelImage.GetPixelIDValue() ), l )
    del l

    sitk.WriteImage( ws, sitkUtils.GetSlicerITKReadWriteAddress( labelNodeName ) )
    labelNode.GetImageData().Modified()
    labelNode.Modified()


#
# The BinaryWatershedEffectExtension class definition
#

class BinaryWatershedEffectExtension(Effect.Effect):
  """Organizes the Options, Tool, and Logic classes into a single instance
  that can be managed by the EditBox
  """

  def __init__(self):
    # name is used to define the name of the icon image resource (e.g. BinaryWatershedEffect.png)
    self.name = "BinaryWatershedEffect"
    # tool tip is displayed on mouse hover
    self.toolTip = "Paint: circular paint brush for label map editing"

    self.options = BinaryWatershedEffectOptions
    self.tool = BinaryWatershedEffectTool
    self.logic = BinaryWatershedEffectLogic

""" Test:

sw = slicer.app.layoutManager().sliceWidget('Red')
import EditorLib
pet = EditorLib.BinaryWatershedEffectTool(sw)

"""

#
# BinaryWatershedEffect
#

class BinaryWatershedEffect:
  """
  This class is the 'hook' for slicer to detect and recognize the extension
  as a loadable scripted module
  """
  def __init__(self, parent):
    parent.title = "Editor BinaryWatershedEffect Effect"
    parent.categories = ["Developer Tools.Editor Extensions"]
    parent.contributors = ["Steve Pieper (Isomics)"] # insert your name in the list
    parent.helpText = """
    Example of an editor extension.  No module interface here, only in the Editor module
    """
    parent.acknowledgementText = """
    This editor extension was developed by
    <Author>, <Institution>
    based on work by:
    Steve Pieper, Isomics, Inc.
    based on work by:
    Jean-Christophe Fillion-Robin, Kitware Inc.
    and was partially funded by NIH grant 3P41RR013218.
    """

    # TODO:
    # don't show this module - it only appears in the Editor module
    #parent.hidden = True

    # Add this extension to the editor's list for discovery when the module
    # is created.  Since this module may be discovered before the Editor itself,
    # create the list if it doesn't already exist.
    try:
      slicer.modules.editorExtensions
    except AttributeError:
      slicer.modules.editorExtensions = {}
    slicer.modules.editorExtensions['BinaryWatershedEffect'] = BinaryWatershedEffectExtension


#
# BinaryWatershedEffectWidget
#

class BinaryWatershedEffectWidget:
  def __init__(self, parent = None):
    self.parent = parent

  def setup(self):
    # don't display anything for this widget - it will be hidden anyway
    pass

  def enter(self):
    pass

  def exit(self):
    pass
