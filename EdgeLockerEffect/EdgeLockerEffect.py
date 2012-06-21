import os
from __main__ import vtk, qt, ctk, slicer
import EditorLib
from EditorLib.EditOptions import HelpButton
from EditorLib.EditOptions import EditOptions
from EditorLib import EditUtil
from EditorLib import LabelEffect

#
# The Editor Extension itself.
#
# This needs to define the hooks to be come an editor effect.
#

#
# EdgeLockerEffectOptions - see LabelEffect, EditOptions and Effect for superclasses
#

class EdgeLockerEffectOptions(EditorLib.LabelEffectOptions):
  """ EdgeLockerEffect-specfic gui
  """

  def __init__(self, parent=0):
    super(EdgeLockerEffectOptions,self).__init__(parent)

    # self.attributes should be tuple of options:
    # 'MouseTool' - grabs the cursor
    # 'Nonmodal' - can be applied while another is active
    # 'Disabled' - not available
    self.attributes = ('MouseTool')
    self.displayName = 'EdgeLockerEffect Effect'

  def __del__(self):
    super(EdgeLockerEffectOptions,self).__del__()

  def create(self):
    super(EdgeLockerEffectOptions,self).create()
    self.apply = qt.QPushButton("Apply", self.frame)
    self.apply.setToolTip("Apply the extension operation")
    self.frame.layout().addWidget(self.apply)
    self.widgets.append(self.apply)

    HelpButton(self.frame, "This is a sample with no real functionality.")

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

    labelLogic = self.sliceLogic.GetLabelLayer()
    labelNode = labelLogic.GetVolumeNode()
    labelNodeName = labelNode.GetName()
    labelImage = sitk.ReadImage( sitkUtils.GetSlicerITKReadWriteAddress( labelNodeName ) )


    backgroundLogic = self.sliceLogic.GetBackgroundLayer()
    backgroundNode = backgroundLogic.GetVolumeNode()
    backgroundNodeName = backgroundNode.GetName()
    backgroundImage = sitk.ReadImage( sitkUtils.GetSlicerITKReadWriteAddress( backgroundNodeName ) )


#    ls = sitk.BinaryThreshold( labelImage, 1, 1, 0, 2 )
#    ls = sitk.Cast( ls, sitk.sitkFloat32) - 1

#    feature = sitk.SmoothingRecursiveGaussian( backgroundImage, 1.0 );

#    filter = sitk.LaplacianSegmentationLevelSetImageFilter( )
#    filter.SetNumberOfIterations( 10 )
#    filter.SetMaximumRMSError( 0 )
#    filter.SetPropagationScaling( 1.0 )
#    filter.SetCurvatureScaling( 0.0 )
#    ls = filter.Execute( ls, feature )
#    print filter    
    
#   sitk.WriteImage( sitk.BinaryThreshold( ls, -99999, 0 ), sitkUtils.GetSlicerITKReadWriteAddress( labelNodeName ) )
    
    featureImage = sitk.GradientMagnitudeRecursiveGaussian( backgroundImage, 1.0 );
    f = sitk.MorphologicalWatershedFromMarkersImageFilter()
    f.SetMarkWatershedLine( False )
    f.SetFullyConnected( False )
    sitk.WriteImage( f.Execute( featureImage, labelImage ), sitkUtils.GetSlicerITKReadWriteAddress( labelNodeName ) )
    labelNode.GetImageData().Modified()
    labelNode.Modified()

#
# The EdgeLockerEffectExtension class definition
#

class EdgeLockerEffectExtension(LabelEffect.LabelEffect):
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


