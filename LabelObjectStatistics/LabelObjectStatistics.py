import unittest
from __main__ import vtk, qt, ctk, slicer
import SimpleITK as sitk
import sitkUtils

#
# LabelObjectStatistics
#

class LabelObjectStatistics:
  def __init__(self, parent):
    import string
    parent.title = "Label Object Statistics"
    parent.categories = ["Microscopy"]
    parent.contributors = ["Bradley Lowekamp (MSC/NLM)"]
    parent.helpText = string.Template("""
Use this module to calculate counts and volumes for different labels of a label map plus statistics on the grayscale background volume.  Note: volumes must have same dimensions.  See <a href=\"$a/Documentation/$b.$c/Modules/LabelObjectStatistics\">$a/Documentation/$b.$c/Modules/LabelObjectStatistics</a> for more information.
    """).substitute({ 'a':parent.slicerWikiUrl, 'b':slicer.app.majorVersion, 'c':slicer.app.minorVersion })
    parent.acknowledgementText = """
    This module is derived from the "Label Statistics" module implemented by Steve Pieper supported by NA-MIC, NAC, BIRN, NCIGT, and the Slicer Community. See http://www.slicer.org for details.
    """
    self.parent = parent

#
# qSlicerPythonModuleExampleWidget
#

class LabelObjectStatisticsWidget:
  def __init__(self, parent=None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.logic = None
    self.grayscaleNode = None
    self.labelNode = None
    self.fileName = None
    self.fileDialog = None
    if not parent:
      self.setup()
      self.grayscaleSelector.setMRMLScene(slicer.mrmlScene)
      self.labelSelector.setMRMLScene(slicer.mrmlScene)
      self.parent.show()

  def setup(self):
    #
    # the grayscale volume selector
    #
    self.grayscaleSelectorFrame = qt.QFrame(self.parent)
    self.grayscaleSelectorFrame.setLayout(qt.QHBoxLayout())
    self.parent.layout().addWidget(self.grayscaleSelectorFrame)

    self.grayscaleSelectorLabel = qt.QLabel("Grayscale Volume: ", self.grayscaleSelectorFrame)
    self.grayscaleSelectorLabel.setToolTip( "Select the grayscale volume (background grayscale scalar volume node) for statistics calculations")
    self.grayscaleSelectorFrame.layout().addWidget(self.grayscaleSelectorLabel)

    self.grayscaleSelector = slicer.qMRMLNodeComboBox(self.grayscaleSelectorFrame)
    self.grayscaleSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.grayscaleSelector.selectNodeUponCreation = False
    self.grayscaleSelector.addEnabled = False
    self.grayscaleSelector.removeEnabled = False
    self.grayscaleSelector.noneEnabled = True
    self.grayscaleSelector.showHidden = False
    self.grayscaleSelector.showChildNodeTypes = False
    self.grayscaleSelector.setMRMLScene( slicer.mrmlScene )
    # TODO: need to add a QLabel
    # self.grayscaleSelector.SetLabelText( "Master Volume:" )
    self.grayscaleSelectorFrame.layout().addWidget(self.grayscaleSelector)

    #
    # the label volume selector
    #
    self.labelSelectorFrame = qt.QFrame()
    self.labelSelectorFrame.setLayout( qt.QHBoxLayout() )
    self.parent.layout().addWidget( self.labelSelectorFrame )

    self.labelSelectorLabel = qt.QLabel()
    self.labelSelectorLabel.setText( "Label Map: " )
    self.labelSelectorFrame.layout().addWidget( self.labelSelectorLabel )

    self.labelSelector = slicer.qMRMLNodeComboBox()
    self.labelSelector.nodeTypes = ( "vtkMRMLLabelMapVolumeNode", "" )
    # todo addAttribute
    self.labelSelector.selectNodeUponCreation = False
    self.labelSelector.addEnabled = False
    self.labelSelector.noneEnabled = True
    self.labelSelector.removeEnabled = False
    self.labelSelector.showHidden = False
    self.labelSelector.showChildNodeTypes = False
    self.labelSelector.setMRMLScene( slicer.mrmlScene )
    self.labelSelector.setToolTip( "Pick the label map to edit" )
    self.labelSelectorFrame.layout().addWidget( self.labelSelector )

    # Apply button
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Calculate Statistics."
    self.applyButton.enabled = False
    self.parent.layout().addWidget(self.applyButton)

    # model and view for stats table
    self.view = qt.QTableView()
    self.view.sortingEnabled = True
    self.parent.layout().addWidget(self.view)

    # Chart button
    self.chartFrame = qt.QFrame()
    self.chartFrame.setLayout(qt.QHBoxLayout())
    self.parent.layout().addWidget(self.chartFrame)
    self.chartButton = qt.QPushButton("Chart")
    self.chartButton.toolTip = "Make a chart from the current statistics."
    self.chartFrame.layout().addWidget(self.chartButton)
    self.chartOption = qt.QComboBox()
    self.chartFrame.layout().addWidget(self.chartOption)
    self.chartIgnoreZero = qt.QCheckBox()
    self.chartIgnoreZero.setText('Ignore Zero')
    self.chartIgnoreZero.checked = False
    self.chartIgnoreZero.setToolTip('Do not include the zero index in the chart to avoid dwarfing other bars')
    self.chartFrame.layout().addWidget(self.chartIgnoreZero)
    self.chartFrame.enabled = False


    # Save button
    self.saveButton = qt.QPushButton("Save")
    self.saveButton.toolTip = "Calculate Statistics."
    self.saveButton.enabled = False
    self.parent.layout().addWidget(self.saveButton)

    # Add vertical spacer
    self.parent.layout().addStretch(1)

    # connections
    self.applyButton.connect('clicked()', self.onApply)
    self.chartButton.connect('clicked()', self.onChart)
    self.saveButton.connect('clicked()', self.onSave)
    self.grayscaleSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onGrayscaleSelect)
    self.labelSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onLabelSelect)

  def onGrayscaleSelect(self, node):
    self.grayscaleNode = node
    self.applyButton.enabled = bool(self.grayscaleNode) and bool(self.labelNode)

  def onLabelSelect(self, node):
    self.labelNode = node
    self.applyButton.enabled = bool(self.grayscaleNode) and bool(self.labelNode)

  def onApply(self):
    """Calculate the label statistics
    """

    self.applyButton.text = "Working..."
    # TODO: why doesn't processEvents alone make the label text change?
    self.applyButton.repaint()
    slicer.app.processEvents()
    volumesLogic = slicer.modules.volumes.logic()
    warnings = volumesLogic.CheckForLabelVolumeValidity(self.grayscaleNode, self.labelNode)
    resampledLabelNode = None
    if warnings != "":
      if 'mismatch' in warnings:
        resampledLabelNode = volumesLogic.ResampleVolumeToReferenceVolume(self.labelNode, self.grayscaleNode)
        self.logic = LabelObjectStatisticsLogic(self.grayscaleNode, resampledLabelNode)
      else:
        qt.QMessageBox.warning(slicer.util.mainWindow(),
            "Label Statistics", "Volumes do not have the same geometry.\n%s" % warnings)
        return
    else:
      self.logic = LabelObjectStatisticsLogic(self.grayscaleNode, self.labelNode)
    self.populateStats()
    self.populateChartOption()
    if resampledLabelNode:
      slicer.mrmlScene.RemoveNode(resampledLabelNode)
    self.chartFrame.enabled = True
    self.saveButton.enabled = True
    self.applyButton.text = "Apply"

  def onChart(self):
    """chart the label statistics
    """
    valueToPlot = self.chartOption.currentText
    ignoreZero = self.chartIgnoreZero.checked
    if not valueToPlot is None:
      self.logic.createStatsChart(self.labelNode,valueToPlot,ignoreZero)
    else:
      print "Selected item is unexpectedly None!"

  def onSave(self):
    """save the label statistics
    """
    if not self.fileDialog:
      self.fileDialog = qt.QFileDialog(self.parent)
      self.fileDialog.options = self.fileDialog.DontUseNativeDialog
      self.fileDialog.acceptMode = self.fileDialog.AcceptSave
      self.fileDialog.defaultSuffix = "csv"
      self.fileDialog.setNameFilter("Comma Separated Values (*.csv)")
      self.fileDialog.connect("fileSelected(QString)", self.onFileSelected)
    self.fileDialog.show()

  def onFileSelected(self,fileName):
    self.logic.saveStats(fileName)

  def populateStats(self):
    if not self.logic:
      return
    displayNode = self.labelNode.GetDisplayNode()
    colorNode = displayNode.GetColorNode()
    lut = colorNode.GetLookupTable()
    self.items = []
    self.model = qt.QStandardItemModel()
    self.view.setModel(self.model)
    self.view.verticalHeader().visible = False
    row = 0
    for i in self.logic.labelStats["Labels"]:
      color = qt.QColor()
      rgb = lut.GetTableValue(i)
      color.setRgb(rgb[0]*255,rgb[1]*255,rgb[2]*255)
      item = qt.QStandardItem()
      item.setData(color,qt.Qt.DecorationRole)
      item.setToolTip(colorNode.GetColorName(i))
      item.setEditable(False)
      self.model.setItem(row,0,item)
      self.items.append(item)
      col = 1
      for k in self.logic.keys:
        item = qt.QStandardItem()
        # set data as float with Qt::DisplayRole
        try:
          v = float(self.logic.labelStats[i,k])
        except (KeyError, TypeError):
          v = float('inf')
        item.setData(v,qt.Qt.DisplayRole)
        item.setToolTip(colorNode.GetColorName(i))
        item.setEditable(False)
        self.model.setItem(row,col,item)
        self.items.append(item)
        col += 1
      row += 1

    self.view.setColumnWidth(0,30)
    self.model.setHeaderData(0,1," ")
    col = 1
    for k in self.logic.keys:
      self.view.setColumnWidth(col,15*len(k))
      self.model.setHeaderData(col,1,k)
      col += 1

  def populateChartOption(self):
    self.chartOption.clear()
    self.chartOption.addItems(self.logic.keys)

class LabelObjectStatisticsLogic:
  """Implement the logic to calculate label statistics.
  Nodes are passed in as arguments.
  Results are stored as 'statistics' instance variable.
  """

  def __init__(self, grayscaleNode, labelNode, fileName=None):
    #import numpy

    self.keys = ["Label", "Count", "Volume mm^3", "Volume cc", "Min", "Max", "Mean", "StdDev"]
    cubicMMPerVoxel = reduce(lambda x,y: x*y, labelNode.GetSpacing())
    ccPerCubicMM = 0.001

    # TODO: progress and status updates
    # this->InvokeEvent(vtkLabelStatisticsLogic::StartLabelStats, (void*)"start label stats")

    self.labelStats = {}
    self.labelStats['Labels'] = []

    labelNodeName = labelNode.GetName()
    labelImage = sitk.ReadImage(sitkUtils.GetSlicerITKReadWriteAddress(labelNodeName))

    grayscaleNodeName = grayscaleNode.GetName();
    grayscaleImage = sitk.ReadImage(sitkUtils.GetSlicerITKReadWriteAddress(grayscaleNodeName))

    sitkStats = sitk.LabelStatisticsImageFilter()

    sitkStats.Execute(grayscaleImage, labelImage)

    for l in sitkStats.GetLabels():

        # add an entry to the LabelStats list
        self.labelStats["Labels"].append(l)
        self.labelStats[l,"Label"] = l
        self.labelStats[l,"Count"] = sitkStats.GetCount(l)
        self.labelStats[l,"Volume mm^3"] = self.labelStats[l,"Count"] * cubicMMPerVoxel
        self.labelStats[l,"Volume cc"] = self.labelStats[l,"Volume mm^3"] * ccPerCubicMM
        self.labelStats[l,"Min"] = sitkStats.GetMinimum(l)
        self.labelStats[l,"Max"] = sitkStats.GetMaximum(l)
        self.labelStats[l,"Mean"] = sitkStats.GetMean(l)
        self.labelStats[l,"StdDev"] = sitkStats.GetSigma(l)
        self.labelStats[l,"Sum"] = sitkStats.GetSum(l)

    del sitkStats

    sitkShapeStats = sitk.LabelShapeStatisticsImageFilter()
    sitkShapeStats.ComputeFeretDiameterOff()
    sitkShapeStats.ComputePerimeterOn()


    sitkShapeStats.Execute( labelImage )


    # use a set to accumulate attributes to make sure they are unuque
    shapeAttributes = [
#      'Number Of Pixels',
#      'Physical Size',
#      'Centroid',
#      'Bounding Box',
      'Number Of Pixels On Border',
      'Perimeter On Border',
      'Perimeter On Border Ratio',
#      'Principal Moments',
      'Principal Axes',
      'Elongation',
      'Perimeter',
      'Roundness',
      'Equivalent Spherical Radius',
      'Equivalent Spherical Perimeter',
#      'Equivalent Ellipsoid Diameter',
      'Flatness',
      'Feret Diameter'
    ]


    if not sitkShapeStats.GetComputeFeretDiameter():
        shapeAttributes.remove( 'Feret Diameter' )

    if not sitkShapeStats.GetComputePerimeter():
        shapeAttributes.remove( 'Perimeter' )

    # We don't have a good way to show
    shapeAttributes.remove( 'Principal Axes' )

    self.keys += shapeAttributes

    for l in sitkShapeStats.GetLabels():
       # add attributes form the Shape label object
        for name in shapeAttributes:
            attr = getattr(sitkShapeStats,"Get"+name.replace(' ', '') )(l)

            self.labelStats[l, name] = attr

    for l in sitkShapeStats.GetLabels():
      attr =  getattr(sitkShapeStats,"Get"+"PrincipalMoments" )(l)
      for i in range(1,4):
        self.labelStats[l, "Principal Moments "+str(i) ] = attr[i-1]

    self.keys += ["Principal Moments "+str(i) for i in range(1,4)]


        # this.InvokeEvent(vtkLabelStatisticsLogic::LabelStatsInnerLoop, (void*)"1")

    # this.InvokeEvent(vtkLabelStatisticsLogic::EndLabelStats, (void*)"end label stats")

  def createStatsChart(self, labelNode, valueToPlot, ignoreZero=False):
    """Make a MRML chart of the current stats
    """
    layoutNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLLayoutNode')
    layoutNodes.SetReferenceCount(layoutNodes.GetReferenceCount()-1)
    layoutNodes.InitTraversal()
    layoutNode = layoutNodes.GetNextItemAsObject()
    layoutNode.SetViewArrangement(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalQuantitativeView)

    chartViewNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLChartViewNode')
    chartViewNodes.SetReferenceCount(chartViewNodes.GetReferenceCount()-1)
    chartViewNodes.InitTraversal()
    chartViewNode = chartViewNodes.GetNextItemAsObject()

    arrayNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
    array = arrayNode.GetArray()
    samples = len(self.labelStats["Labels"])
    tuples = samples
    if ignoreZero and self.labelStats["Labels"].__contains__(0):
      tuples -= 1
    array.SetNumberOfTuples(tuples)
    tuple = 0
    for i in xrange(samples):
        index = self.labelStats["Labels"][i]
        if not (ignoreZero and index == 0):
          array.SetComponent(tuple, 0, index)
          try:
            v = float(self.labelStats[index,valueToPlot])
          except (KeyError, TypeError):
            v = float(0)
          array.SetComponent(tuple, 1, v)
          array.SetComponent(tuple, 2, 0)
          tuple += 1

    chartNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())

    state = chartNode.StartModify()

    chartNode.AddArray(valueToPlot, arrayNode.GetID())

    chartViewNode.SetChartNodeID(chartNode.GetID())

    chartNode.SetProperty('default', 'title', 'Label Statistics')
    chartNode.SetProperty('default', 'xAxisLabel', 'Label')
    chartNode.SetProperty('default', 'yAxisLabel', valueToPlot)
    chartNode.SetProperty('default', 'type', 'Bar');
    chartNode.SetProperty('default', 'xAxisType', 'categorical')
    chartNode.SetProperty('default', 'showLegend', 'off')

    # series level properties
    if labelNode.GetDisplayNode() != None and labelNode.GetDisplayNode().GetColorNode() != None:
      chartNode.SetProperty(valueToPlot, 'lookupTable', labelNode.GetDisplayNode().GetColorNodeID());

    chartNode.EndModify(state)

  def statsAsCSV(self):
    """
    print comma separated value file with header keys in quotes
    """
    csv = ""
    header = ""
    for k in self.keys[:-1]:
      header += "\"%s\"" % k + ","
    header += "\"%s\"" % self.keys[-1] + "\n"
    csv = header

    for i in self.labelStats["Labels"]:

      valuesAsStr = [ str(self.labelStats[i,k]) if (i,k) in self.labelStats else '' for k in self.keys ]
      line = ",".join(valuesAsStr)
      line += "\n"
      csv += line
    return csv

  def saveStats(self,fileName):
    fp = open(fileName, "w")
    fp.write(self.statsAsCSV())
    fp.close()

class LabelObjectStatisticsTest(unittest.TestCase):
  """
  This is the test case.
  """

  def delayDisplay(self,message,msec=1000):
    """This utility method displays a small dialog and waits.
    This does two things: 1) it lets the event loop catch up
    to the state of the test so that rendering and widget updates
    have all taken place before the test continues and 2) it
    shows the user/developer/tester the state of the test
    so that we'll know when it breaks.
    """
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self,scenario=None):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_LabelObjectStatisticsBasic()
    self.test_LabelObjectStatisticsWidget()
    self.test_LabelObjectStatisticsLogic()

  def test_LabelObjectStatisticsBasic(self):
    """
    This tests some aspects of the label statistics
    """

    self.delayDisplay("Starting test_LabelObjectStatisticsBasic")
    #
    # first, get some data
    #
    import SampleData
    sampleDataLogic = SampleData.SampleDataLogic()
    mrHead = sampleDataLogic.downloadMRHead()
    ctChest = sampleDataLogic.downloadCTChest()
    self.delayDisplay('Two data sets loaded')

    volumesLogic = slicer.modules.volumes.logic()

    mrHeadLabel = volumesLogic.CreateAndAddLabelVolume( slicer.mrmlScene, mrHead, "mrHead-label" )

    warnings = volumesLogic.CheckForLabelVolumeValidity(ctChest, mrHeadLabel)

    self.delayDisplay("Warnings for mismatch:\n%s" % warnings)

    self.assertTrue( warnings != "" )

    warnings = volumesLogic.CheckForLabelVolumeValidity(mrHead, mrHeadLabel)

    self.delayDisplay("Warnings for match:\n%s" % warnings)

    self.assertTrue( warnings == "" )

    self.delayDisplay('test_LabelObjectStatisticsBasic passed!')

  def test_LabelObjectStatisticsWidget(self):
    return
    self.delayDisplay("Starting test_LabelObjectStatisticsWidget")
    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('LabelObjectStatistics')


    print dir(slicer.modules)

    testWidget = slicer.modules.LabelObjectStatisticsWidget



  def test_LabelObjectStatisticsLogic(self):


    self.delayDisplay("Starting test_LabelObjectStatisticsLogic")

    import SampleData
    sampleDataLogic = SampleData.SampleDataLogic()
    mrHead = sampleDataLogic.downloadMRHead()

    img = sitkUtils.PullFromSlicer( mrHead.GetName() )

    labelImg = sitk.OtsuMultipleThresholds(img, 3)

    labelNodeName = "OtsuMultipleThresholdLabelMap"
    sitkUtils.PushToSlicer(labelImg, "OtsuMultipleThresholdLabelMap", 2)

    mrHeadLabel = slicer.util.getNode(labelNodeName)


    logic = LabelObjectStatisticsLogic( mrHead, mrHeadLabel )
    print logic.keys
    print logic.labelStats

    logic.saveStats("test_LabelObjectStatisticsLogic.csv")
