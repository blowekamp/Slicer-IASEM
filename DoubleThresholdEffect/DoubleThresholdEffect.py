import os
from __main__ import vtk, qt, ctk, slicer
import EditorLib
from EditorLib.EditOptions import HelpButton
from EditorLib.EditOptions import EditOptions
from EditorLib import EditUtil
from EditorLib import Effect

import SimpleITK as sitk
import sitkUtils

#########################################################
#
# 
comment = """

  DoubleThresholdEffect is a subclass of Effect
  the global threshold operation
  in the slicer editor

# TODO : 
"""
#
#########################################################

#
# DoubleThresholdEffectOptions - see Effect for superclasses
#

class DoubleThresholdEffectOptions(Effect.EffectOptions):
  """ DoubleThresholdEffect-specfic gui
  """

  def __init__(self, parent=0):
    super(DoubleThresholdEffectOptions,self).__init__(parent)

  def __del__(self):
    super(DoubleThresholdEffectOptions,self).__del__()

  def create(self):
    super(DoubleThresholdEffectOptions,self).create()

    self.thresholdLabel = qt.QLabel("DoubleThreshold Inner Range:", self.frame)
    self.thresholdLabel.setToolTip("Set the range of the background values that should will labeled.")
    self.threshold = ctk.ctkRangeWidget(self.frame)
    self.threshold.spinBoxAlignment = 0xff # put enties on top
    self.threshold.singleStep = 0.01

    self.outerThresholdLabel = qt.QLabel("DoubleThreshold Outter Range:", self.frame)
    self.outerThresholdLabel.setToolTip("Set the range of the background values that must be connected to the inner range to be labeled.")
   
    self.outerThreshold = ctk.ctkRangeWidget(self.frame)
    self.outerThreshold.spinBoxAlignment = 0xff # put enties on top
    self.outerThreshold.singleStep = 0.01
    

    # set min/max based on current range
    success, lo, hi = self.getBackgroundScalarRange()
    if success:
      self.threshold.minimum, self.threshold.maximum = lo, hi
      self.threshold.singleStep = (hi - lo) / 1000.
      
      self.outerThreshold.minimum, self.outerThreshold.maximum = lo, hi
      self.outerThreshold.singleStep = (hi - lo) / 1000.

    self.frame.layout().addWidget(self.thresholdLabel)
    self.widgets.append(self.thresholdLabel)
    self.frame.layout().addWidget(self.threshold)
    self.widgets.append(self.threshold)

    self.frame.layout().addWidget(self.outerThresholdLabel)
    self.widgets.append(self.outerThresholdLabel)
    self.frame.layout().addWidget(self.outerThreshold)
    self.widgets.append(self.outerThreshold)

    self.apply = qt.QPushButton("Apply", self.frame)
    self.apply.setToolTip("Apply current threshold settings to the label map.")
    self.frame.layout().addWidget(self.apply)
    self.widgets.append(self.apply)

    self.timer = qt.QTimer()
    self.previewState = 0
    self.previewStep = 1
    self.previewSteps = 5
    self.timer.start(200)

    self.connections.append( (self.timer, 'timeout()', self.preview) )
    self.connections.append( (self.threshold, 'valuesChanged(double,double)', self.onThresholdValuesChanged) )
    self.connections.append( (self.outerThreshold, 'valuesChanged(double,double)', self.onThresholdValuesChanged) )
    self.connections.append( (self.apply, 'clicked()', self.onApply) )

    EditorLib.HelpButton(self.frame, "TODO: describe double threshold")

    # Add vertical spacer
    self.frame.layout().addStretch(1)

  def onApply(self):
    min = float(self.parameterNode.GetParameter("DoubleThresholdEffect,min"))
    max = float(self.parameterNode.GetParameter("DoubleThresholdEffect,max"))
    outer_min = float(self.parameterNode.GetParameter("DoubleThresholdEffect,outer_min"))
    outer_max = float(self.parameterNode.GetParameter("DoubleThresholdEffect,outer_max"))
    try:
      # only apply in the first tool (the operation is global and will be the same in all)
      tool = self.tools[0]
      tool.min = min
      tool.max = max
      tool.outer_min = outer_min
      tool.outer_max = outer_max
      tool.apply()
    except IndexError:
      # no tools available
      pass
    # trigger the passed in callable that cancels the current effect
    self.defaultEffect()

  def destroy(self):
    super(DoubleThresholdEffectOptions,self).destroy()
    self.timer.stop()

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
    super(DoubleThresholdEffectOptions,self).setMRMLDefaults()
    disableState = self.parameterNode.GetDisableModifiedEvent()
    self.parameterNode.SetDisableModifiedEvent(1)
    defaults = (
      ("min", "1"),
      ("max", "99"),
      ("outer_min", "0"),
      ("outer_max", "100"),
    )
    for d in defaults:
      param = "DoubleThresholdEffect,"+d[0]
      pvalue = self.parameterNode.GetParameter(param)
      if pvalue == '':
        self.parameterNode.SetParameter(param, d[1])
    # override default min/max settings based on current background
    success, lo, hi = self.getBackgroundScalarRange()
    if success:
      self.parameterNode.SetParameter("DoubleThresholdEffect,min", str(lo + 0.25 * (hi-lo)))
      self.parameterNode.SetParameter("DoubleThresholdEffect,max", str(hi))
      self.parameterNode.SetParameter("DoubleThresholdEffect,outer_min", str(lo + 0.20 * (hi-lo)))
      self.parameterNode.SetParameter("DoubleThresholdEffect,outer_max", str(hi))
    self.parameterNode.SetDisableModifiedEvent(disableState)

  def onThresholdValuesChanged(self,min,max):
    self.updateMRMLFromGUI()


  def updateGUIFromMRML(self,caller,event):
    params = ("min", "max","outer_min", "outer_max")
    for p in params:
      if self.parameterNode.GetParameter("DoubleThresholdEffect,"+p) == '':
        # don't update if the parameter node has not got all values yet
        return
    super(DoubleThresholdEffectOptions,self).updateGUIFromMRML(caller,event)
    self.disconnectWidgets()
    min = float(self.parameterNode.GetParameter("DoubleThresholdEffect,min"))
    max = float(self.parameterNode.GetParameter("DoubleThresholdEffect,max"))
    outer_min = float(self.parameterNode.GetParameter("DoubleThresholdEffect,outer_min"))
    outer_max = float(self.parameterNode.GetParameter("DoubleThresholdEffect,outer_max"))

    self.threshold.setMinimumValue( min )
    self.threshold.setMaximumValue( max )
    self.outerThreshold.setMinimumValue( outer_min )
    self.outerThreshold.setMaximumValue( outer_max )

    for tool in self.tools:
      tool.min = min
      tool.max = max
      tool.outer_min = outer_min
      tool.outer_max = outer_max

    self.connectWidgets()

  def updateMRMLFromGUI(self):
    disableState = self.parameterNode.GetDisableModifiedEvent()
    self.parameterNode.SetDisableModifiedEvent(1)
    super(DoubleThresholdEffectOptions,self).updateMRMLFromGUI()
    self.parameterNode.SetParameter( "DoubleThresholdEffect,min", str(self.threshold.minimumValue) )
    self.parameterNode.SetParameter( "DoubleThresholdEffect,max", str(self.threshold.maximumValue) )
    self.parameterNode.SetParameter( "DoubleThresholdEffect,outer_min", str(self.outerThreshold.minimumValue) )
    self.parameterNode.SetParameter( "DoubleThresholdEffect,outer_max", str(self.outerThreshold.maximumValue) )
    self.parameterNode.SetDisableModifiedEvent(disableState)
    if not disableState:
      self.parameterNode.InvokePendingModifiedEvent()

  def preview(self):
    opacity = 0.5 + self.previewState / (2. * self.previewSteps)
    min = float(self.parameterNode.GetParameter("DoubleThresholdEffect,min"))
    max = float(self.parameterNode.GetParameter("DoubleThresholdEffect,max"))
    outer_min = float(self.parameterNode.GetParameter("DoubleThresholdEffect,outer_min"))
    outer_max = float(self.parameterNode.GetParameter("DoubleThresholdEffect,outer_max"))

    for tool in self.tools:
      tool.min = min
      tool.max = max
      tool.outer_min = outer_min
      tool.outer_max = outer_max
      tool.preview(self.editUtil.getLabelColor()[:3] + (opacity,))
    self.previewState += self.previewStep
    if self.previewState >= self.previewSteps:
      self.previewStep = -1
    if self.previewState <= 0:
      self.previewStep = 1

#
# DoubleThresholdEffectTool
#
 
class DoubleThresholdEffectTool(Effect.EffectTool):
  """
  One instance of this will be created per-view when the effect
  is selected.  It is responsible for implementing feedback and
  label map changes in response to user input.
  This class observes the editor parameter node to configure itself
  and queries the current view for background and label volume
  nodes to operate on.
  """

  def __init__(self, sliceWidget):
    super(DoubleThresholdEffectTool,self).__init__(sliceWidget)
    
    # create a logic instance to do the non-gui work
    self.logic = DoubleThresholdEffectLogic(self.sliceWidget.sliceLogic())
    self.logic.undoRedo = self.undoRedo

    # interaction state variables
    self.min = 0
    self.max = 0
    self.outer_min = 0
    self.outer_max = 0

    # class instances
    self.lut = None
    self.thresh = None
    self.outter_thresh = None
    self.add_thresh = None
    self.map = None

    # feedback actor
    self.cursorDummyImage = vtk.vtkImageData()
    self.cursorDummyImage.AllocateScalars()
    self.cursorMapper = vtk.vtkImageMapper()
    self.cursorMapper.SetInput( self.cursorDummyImage )
    self.cursorActor = vtk.vtkActor2D()
    self.cursorActor.VisibilityOff()
    self.cursorActor.SetMapper( self.cursorMapper )
    self.cursorMapper.SetColorWindow( 255 )
    self.cursorMapper.SetColorLevel( 128 )

    self.actors.append( self.cursorActor )

    self.renderer.AddActor2D( self.cursorActor )

  def cleanup(self):
    """
    call superclass to clean up actors
    """
    super(DoubleThresholdEffectTool,self).cleanup()

  def processEvent(self, caller=None, event=None):
    """
    handle events from the render window interactor
    """

    # TODO: might want to do something special here, like
    # adjust the threshold based on a gesture in the slice
    # view - but for now everything is driven by the options gui
    pass

  def apply(self):

    if not self.editUtil.getBackgroundImage() or not self.editUtil.getLabelImage():
      return
    node = self.editUtil.getParameterNode()

    self.undoRedo.saveState()

    #
    # get the label and background images
    #
    sliceLogic = self.sliceWidget.sliceLogic()
    labelLogic = sliceLogic.GetLabelLayer()
    labelNode = labelLogic.GetVolumeNode()
    labelNodeName = labelNode.GetName()

    backgroundLogic = sliceLogic.GetBackgroundLayer()
    backgroundNode = backgroundLogic.GetVolumeNode()
    backgroundNodeName = backgroundNode.GetName()
    backgroundImage = sitk.ReadImage( sitkUtils.GetSlicerITKReadWriteAddress( backgroundNodeName ) )

    
    filter = sitk.DoubleThresholdImageFilter()
    filter.SetThreshold1( self.outer_min )
    filter.SetThreshold2( self.min )
    filter.SetThreshold3( self.max )
    filter.SetThreshold4( self.outer_max )
    filter.FullyConnectedOn()
    filter.SetInsideValue( self.editUtil.getLabel() )
    filter.SetOutsideValue( 0 )

    # todo
    # cast to output scalar type
    
    sitk.WriteImage( filter.Execute(backgroundImage), sitkUtils.GetSlicerITKReadWriteAddress( labelNodeName ) )

  def preview(self,color=None):

    if not self.editUtil.getBackgroundImage() or not self.editUtil.getLabelImage():
      return

    #
    # make a lookup table where inside the threshold is opaque and colored
    # by the label color, while the background is transparent (black)
    # - apply the threshold operation to the currently visible background
    #   (output of the layer logic's vtkImageReslice instance)
    #

    if not color:
      color = self.getPaintColor

    if not self.lut:
      self.lut = vtk.vtkLookupTable()

    self.lut.SetRampToLinear()
    self.lut.SetNumberOfTableValues( 3 )
    self.lut.SetTableRange( 0, 2 )
    self.lut.SetTableValue( 0,  0, 0, 0,  0 )
    r,g,b,a = color
    self.lut.SetTableValue( 1,  r, g, b,  a/3 )
    self.lut.SetTableValue( 2,  r, g, b,  a )

    if not self.map:
      self.map = vtk.vtkImageMapToRGBA()
    self.map.SetOutputFormatToRGBA()
    self.map.SetLookupTable( self.lut )

    if not self.thresh:
      self.thresh = vtk.vtkImageThreshold()
    sliceLogic = self.sliceWidget.sliceLogic()
    backgroundLogic = sliceLogic.GetBackgroundLayer()

    self.thresh.SetInput( backgroundLogic.GetReslice().GetOutput() )
    self.thresh.ThresholdBetween( self.min, self.max )
    self.thresh.SetInValue( 1 )
    self.thresh.SetOutValue( 0 )
    self.thresh.SetOutputScalarTypeToUnsignedChar()

    if not self.outter_thresh:
      self.outter_thresh = vtk.vtkImageThreshold()

    sliceLogic = self.sliceWidget.sliceLogic()
    backgroundLogic = sliceLogic.GetBackgroundLayer()

    self.outter_thresh.SetInput( backgroundLogic.GetReslice().GetOutput() )
    self.outter_thresh.ThresholdBetween( self.outer_min, self.outer_max )
    self.outter_thresh.SetInValue( 1 )
    self.outter_thresh.SetOutValue( 0 )
    self.outter_thresh.SetOutputScalarTypeToUnsignedChar()

    if not self.add_thresh:
      self.add_thresh = vtk.vtkImageMathematics()

    self.add_thresh.SetInput1( self.thresh.GetOutput() )
    self.add_thresh.SetInput2( self.outter_thresh.GetOutput() )
    self.add_thresh.SetOperationToAdd()

    self.map.SetInput( self.add_thresh.GetOutput() )

    self.map.Update()

    self.cursorMapper.SetInput( self.map.GetOutput() )
    self.cursorActor.VisibilityOn()

    self.sliceView.scheduleRender()

#
# DoubleThresholdEffectLogic
#
 
class DoubleThresholdEffectLogic(Effect.EffectLogic):
  """
  This class contains helper methods for a given effect
  type.  It can be instanced as needed by an DoubleThresholdEffectTool
  or DoubleThresholdEffectOptions instance in order to compute intermediate
  results (say, for user feedback) or to implement the final 
  segmentation editing operation.  This class is split
  from the DoubleThresholdEffectTool so that the operations can be used
  by other code without the need for a view context.
  """

  def __init__(self,sliceLogic):
    super(DoubleThresholdEffectLogic,self).__init__(sliceLogic)


#
# The DoubleThresholdEffectExtension class definition 
#

class DoubleThresholdEffectExtension(Effect.Effect):
  """Organizes the Options, Tool, and Logic classes into a single instance
  that can be managed by the EditBox
  """

  def __init__(self):
    # name is used to define the name of the icon image resource (e.g. DoubleThresholdEffect.png)
    self.name = "DoubleThresholdEffect"
    # tool tip is displayed on mouse hover
    self.toolTip = "Paint: circular paint brush for label map editing"

    self.options = DoubleThresholdEffectOptions
    self.tool = DoubleThresholdEffectTool
    self.logic = DoubleThresholdEffectLogic

""" Test:

sw = slicer.app.layoutManager().sliceWidget('Red')
import EditorLib
pet = EditorLib.DoubleThresholdEffectTool(sw)

"""

#
# DoubleThresholdEffect
#

class DoubleThresholdEffect:
  """
  This class is the 'hook' for slicer to detect and recognize the extension
  as a loadable scripted module
  """
  def __init__(self, parent):
    parent.title = "Editor DoubleThreshold Effect"
    parent.categories = ["Developer Tools.Editor Extensions"]
    parent.contributors = ["Bradley Lowekamp"]
    parent.helpText = """
    Double Threshold editor extension.
    """
    parent.acknowledgementText = """
    This editor extension was developed by 
    Bradley Lowekamp
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
    slicer.modules.editorExtensions['DoubleThresholdEffect'] = DoubleThresholdEffectExtension

#
# DoubleThresholdEffectWidget
#

class DoubleThresholdEffectWidget:
  def __init__(self, parent = None):
    self.parent = parent
    
  def setup(self):
    # don't display anything for this widget - it will be hidden anyway
    pass

  def enter(self):
    pass
    
  def exit(self):
    pass

