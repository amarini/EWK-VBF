import os, sys
import array
import ROOT
from optparse import OptionParser


#define an entry structure - usefull to do get address correctly
ROOT.gROOT.ProcessLine (\
	"struct Entry{ \
	float var; \
	float weight;\
	};" )
from ROOT import Entry

#options
parser= OptionParser()
parser.add_option("-v","--varName"   ,dest='varName'    ,type='string',default="mj1j2")
parser.add_option("-w","--weightName",dest='weightName' ,type='string',default="weight")
parser.add_option("-d","--dirName"   ,dest='dirName'    ,type='string',default="vbfAnalysis")
parser.add_option("-f","--fileName"  ,dest='fileName'   ,type='string',default="root://eoscms///store/user/amarini/histograms_Vbf_v4.root")
parser.add_option(""  ,"--xMin"      ,dest='xMin'       ,type='float' ,default=0)
parser.add_option(""  ,"--xMax"      ,dest='xMax'       ,type='float' ,default=1000)
parser.add_option(""  ,"--nBins"     ,dest='nBins'      ,type='int'   ,default=250)

(options,args)=parser.parse_args()
#options.varName


#make configurable - ? -
treeNames=[
 'PhRunB',
 'DY',
 'GJets20-40_pf',
 'GJet_Pt40_pf',
 'GJets20-40_pp',
 'GJet_Pt40_pp',
 'QCD30_40_ff',
 'QCD40_ff',
 'QCD30_40_pf',
 'QCD40_pf',
 'DiPhotonJets_sherpa',
 'DiPhotonBornPt_10_25',
 'DiPhotonBoxPt_10_25',
 'DiPhotonBoxPt_250',
 'DiPhotonBoxPt_25_250',
 'DiPhotonJets_madgraph',
 'GGToH125',
 'VBFH125',
 'WHZH125',
 'EWK']

###################### START ANALYSIS ########################

#open File
File = ROOT.TFile.Open(options.fileName)

#Get Trees
trees=[]
for iTreeName in treeNames:
	trees.append( File.Get(options.dirName+"/"+iTreeName)  )

#Loop and get Branches
print >>sys.stderr, "Begin Loop"
histos=[]
for iL in range(0,len(treeNames)):
	print >>sys.stderr, "Going to Process tree: " + treeNames[iL]
	nEntries=trees[iL].GetEntries()	
	entry= Entry()
	trees[iL].SetBranchAddress(options.varName,ROOT.AddressOf(entry,'var'))
	trees[iL].SetBranchAddress(options.weightName,ROOT.AddressOf(entry,'weight'))
	histos.append( ROOT.TH1F(treeNames[iL],treeNames[iL],options.nBins,options.xMin,options.xMax) )  
	for iEntry in range(0,nEntries):
		trees[iL].GetEntry(iEntry)
		histos[iL].Fill(entry.var,entry.weight)

#color and stuff		
for iL in range(0,len(treeNames)):
	histos[iL].SetLineColor(ROOT.kBlack)
	histos[iL].SetLineWidth(2)
	if "DY"    in treeNames[iL]: histos[iL].SetFillColor(ROOT.kYellow)
	if "GJets" in treeNames[iL]: histos[iL].SetFillColor(ROOT.kMagenta+2)
	if "QCD"   in treeNames[iL]: histos[iL].SetFillColor(ROOT.kBlue-4)
	if "DiPhoton"   in treeNames[iL]: histos[iL].SetFillColor(ROOT.kRed-4)
	if "EWK"   in treeNames[iL]: histos[iL].SetFillColor(ROOT.kGreen-4)
	if "H125"   in treeNames[iL]: histos[iL].SetFillColor(ROOT.kOrange)
	if "Run"   in treeNames[iL] or "Data" in treeNames[iL]: histos[iL].SetMarkerStyle(20)
	#SCALE
	#if "sherpa"   in treeNames[iL]: histos[iL].Scale(1.0/1.2)

#prepare Legend and style
L    = ROOT.TLegend(0.75,0.75,.89,.89)
L.SetFillStyle(0)
L.SetBorderSize(0)
L.AddEntry(histos[0],"data","P");
#fill comulative histo and stack and legend
S    = ROOT.THStack("stack","stack")
hAll = ROOT.TH1F("all","all",options.nBins,options.xMin,options.xMax )  
for iL in range(0,len(treeNames)):
	if ("DY" in treeNames[iL] ) or ("GJets" in  treeNames[iL])or ("QCD" in  treeNames[iL])or ("EWK" in  treeNames[iL])or ("H125" in  treeNames[iL])or ("sherpa" in  treeNames[iL]):
		S.Add( histos[iL] )
		hAll.Add( histos[iL] )
	#want to do only one for splitted samples
	if "DY" in treeNames[iL]:
		L.AddEntry(histos[iL],"DY","F");
	if "GJet_Pt40_pf" in treeNames[iL]:
		L.AddEntry(histos[iL],"GJets","F");
	if "EWK" in treeNames[iL]:
		L.AddEntry(histos[iL],"EWK","F");
	if "sherpa" in treeNames[iL]:
		L.AddEntry(histos[iL],"DiPhotonSherpa","F");
	if "VBFH125" in treeNames[iL]:
		L.AddEntry(histos[iL],"H125","F");
	if "QCD40_ff" in treeNames[iL]:
		L.AddEntry(histos[iL],"QCD","F");


#draw canvas
C   = ROOT.TCanvas("c","c",800,800)
Pup = ROOT.TPad("up","up",0,0.3,1.0,1.0)
Pdn = ROOT.TPad("dn","dn",0,0.0,1.0,0.3)
Pup.Draw()
Pdn.Draw()

#draw up plot
Pup.cd()
S.Draw("HIST ")
histos[0].Draw("P SAME")
L.Draw("SAME")

#draw ratio
Pdn.cd()
Pdn.SetGridy()
h = histos[0].Clone("ratio")
h.Divide(hAll)
h.Draw("P")

C.SaveAs("canvas.pdf");
