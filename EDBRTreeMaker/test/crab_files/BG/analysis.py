import FWCore.ParameterSet.Config as cms

process = cms.Process( "TEST" )
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))
#,
#				     SkipEvent = cms.untracked.vstring('ProductNotFound'))
filterMode = False # True                
doAK8reclustering = False # False
doAK8prunedReclustering = False #True # False
doAK8softdropReclustering = False #True # False
 
######## Sequence settings ##########
corrJetsOnTheFly = True
runOnMC =  True
DOHLTFILTERS = True
#useJSON = not (runOnMC)
#JSONfile = 'Cert_246908-258750_13TeV_PromptReco_Collisions15_25ns_JSON.txt'
#****************************************************************************************************#

#process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
if runOnMC:
   process.GlobalTag.globaltag = '80X_mcRun2_asymptotic_v5'#'MCRUN2_74_V9::All'
elif not(runOnMC):
   process.GlobalTag.globaltag = '80X_dataRun2_v6'
   #process.GlobalTag.globaltag = '74X_dataRun2_Prompt_v4' for v4

# https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD2015#ETmiss_filters
# For the RunIISpring15DR74 MC campaing, the process name in PAT.
# For Run2015B PromptReco Data, the process name is RECO.
# For Run2015B re-MiniAOD Data 17Jul2015, the process name is PAT.
hltFiltersProcessName = 'RECO'
if runOnMC:
   hltFiltersProcessName = 'PAT' #'RECO'


######### read JSON file for data ##########					                                                             
'''if not(runOnMC) and useJSON:

  import FWCore.PythonUtilities.LumiList as LumiList
  import FWCore.ParameterSet.Types as CfgTypes
  process.source.lumisToProcess = CfgTypes.untracked(CfgTypes.VLuminosityBlockRange())
  myLumis = LumiList.LumiList(filename = JSONfile).getCMSSWString().split(',')
  process.source.lumisToProcess.extend(myLumis) 
'''

####### Redo Jet clustering sequence ##########

from RecoJets.Configuration.RecoPFJets_cff import ak4PFJetsCHS, ak8PFJetsCHS, ak8PFJetsCHSPruned, ak8PFJetsCHSSoftDrop, ak8PFJetsCHSPrunedMass, ak8PFJetsCHSSoftDropMass# , ak8PFJetsCSTrimmed, ak8PFJetsCSFiltered, ak8PFJetsCHSFilteredMass, ak8PFJetsCHSTrimmedMass


process.chs = cms.EDFilter("CandPtrSelector",
  src = cms.InputTag('packedPFCandidates'),
  cut = cms.string('fromPV')
)

process.NjettinessAK8 = cms.EDProducer("NjettinessAdder",
                   src = cms.InputTag("ak8PFJetsCHS"),
                   Njets = cms.vuint32(1, 2, 3, 4),
                   # variables for measure definition : 
                   measureDefinition = cms.uint32( 0 ), # CMS default is normalized measure
                   beta = cms.double(1.0),          # CMS default is 1
                   R0 = cms.double( 0.8 ),          # CMS default is jet cone size
                   Rcutoff = cms.double( -999.0),       # not used by default
                   # variables for axes definition :
                   axesDefinition = cms.uint32( 6 ),    # CMS default is 1-pass KT axes
                   nPass = cms.int32(-999),         # not used by default
                   akAxesR0 = cms.double(-999.0)        # not used by default
                   )

process.ak4PFJetsCHS = ak4PFJetsCHS.clone(src = 'chs')
process.ak8PFJetsCHS = ak8PFJetsCHS.clone( src = 'chs', jetPtMin = 100.0 )

process.ak8PFJetsCHSPruned = ak8PFJetsCHSPruned.clone( src = 'chs', jetPtMin = 100.0  )
process.ak8PFJetsCHSPrunedMass = ak8PFJetsCHSPrunedMass.clone()

process.ak8PFJetsCHSSoftDrop = ak8PFJetsCHSSoftDrop.clone( src = 'chs', jetPtMin = 100.0  )
process.ak8PFJetsCHSSoftDropMass = ak8PFJetsCHSSoftDropMass.clone()

process.substructureSequence = cms.Sequence()
if doAK8reclustering:
   process.substructureSequence+=process.chs
   process.substructureSequence+=process.ak8PFJetsCHS
   process.substructureSequence+=process.NjettinessAK8


if doAK8prunedReclustering:
   process.substructureSequence+=process.ak8PFJetsCHSPruned
   process.substructureSequence+=process.ak8PFJetsCHSPrunedMass

if doAK8softdropReclustering:
   process.substructureSequence+=process.ak8PFJetsCHSSoftDrop
   process.substructureSequence+=process.ak8PFJetsCHSSoftDropMass

####### Redo pat jets sequence ##########
process.redoPatJets = cms.Sequence()
process.redoPrunedPatJets = cms.Sequence()
process.redoSoftDropPatJets = cms.Sequence()

from ExoDiBosonResonances.EDBRJets.redoPatJets_cff import patJetCorrFactorsAK8, patJetsAK8, selectedPatJetsAK8

# Redo pat jets from ak8PFJetsCHS
process.patJetCorrFactorsAK8 = patJetCorrFactorsAK8.clone( src = 'ak8PFJetsCHS' )
process.patJetsAK8 = patJetsAK8.clone( jetSource = 'ak8PFJetsCHS' )
process.patJetsAK8.userData.userFloats.src = [ cms.InputTag("ak8PFJetsCHSPrunedMass"), cms.InputTag("ak8PFJetsCHSSoftDropMass"), cms.InputTag("NjettinessAK8:tau1"), cms.InputTag("NjettinessAK8:tau2"), cms.InputTag("NjettinessAK8:tau3")]
process.patJetsAK8.jetCorrFactorsSource = cms.VInputTag( cms.InputTag("patJetCorrFactorsAK8") )
process.selectedPatJetsAK8 = selectedPatJetsAK8.clone( cut = cms.string('pt > 20') )

if doAK8reclustering:
   process.redoPatJets+=process.patJetCorrFactorsAK8
   process.redoPatJets+=process.patJetsAK8
   process.redoPatJets+=process.selectedPatJetsAK8

# Redo pat jets ak8PFJetsCHSPruned
process.patJetCorrFactorsAK8Pruned = patJetCorrFactorsAK8.clone( src = 'ak8PFJetsCHSPruned' )
process.patJetsAK8Pruned = patJetsAK8.clone( jetSource = 'ak8PFJetsCHSPruned' )
process.patJetsAK8Pruned.userData.userFloats.src = [ "" ]
#process.patJetsAK8Pruned.userData.userFloats =cms.PSet(src = cms.VInputTag(""))
process.patJetsAK8Pruned.jetCorrFactorsSource = cms.VInputTag( cms.InputTag("patJetCorrFactorsAK8Pruned") )
process.selectedPatJetsAK8Pruned = selectedPatJetsAK8.clone(cut = 'pt > 20', src = "patJetsAK8Pruned")

if doAK8prunedReclustering:
   process.redoPrunedPatJets+=process.patJetCorrFactorsAK8Pruned
   process.redoPrunedPatJets+=process.patJetsAK8Pruned
   process.redoPrunedPatJets+=process.selectedPatJetsAK8Pruned

# Redo pat jets ak8PFJetsCHSSoftDrop
process.patJetCorrFactorsAK8Softdrop = patJetCorrFactorsAK8.clone( src = 'ak8PFJetsCHSSoftDrop' )
process.patJetsAK8Softdrop = patJetsAK8.clone( jetSource = 'ak8PFJetsCHSSoftDrop' )
process.patJetsAK8Softdrop.userData.userFloats.src = [ "" ]
#process.patJetsAK8Softdrop.userData.userFloats =cms.PSet(src = cms.VInputTag(""))
process.patJetsAK8Softdrop.jetCorrFactorsSource = cms.VInputTag( cms.InputTag("patJetCorrFactorsAK8Softdrop") )
process.selectedPatJetsAK8Softdrop = selectedPatJetsAK8.clone(cut = 'pt > 20', src = "patJetsAK8Softdrop")

if doAK8softdropReclustering:
   process.redoSoftDropPatJets+=process.patJetCorrFactorsAK8Softdrop
   process.redoSoftDropPatJets+=process.patJetsAK8Softdrop
   process.redoSoftDropPatJets+=process.selectedPatJetsAK8Softdrop


option = 'RECO'

process.load("ExoDiBosonResonances.EDBRCommon.goodMuons_cff")
process.load("ExoDiBosonResonances.EDBRCommon.goodElectrons_cff")
process.load("ExoDiBosonResonances.EDBRCommon.goodJets_cff")
process.load("ExoDiBosonResonances.EDBRCommon.leptonicW_cff")
process.load("ExoDiBosonResonances.EDBRCommon.hadronicW_cff")

if option == 'RECO':
    process.goodMuons.src = "slimmedMuons"
    process.goodElectrons.src = "slimmedElectrons"
    process.goodJets.src = "slimmedJetsAK8"
#    process.goodJets.src = "selectedPatJetsAK8"
    process.Wtoenu.MET  = "slimmedMETs"
    process.Wtomunu.MET = "slimmedMETs"
if doAK8reclustering:
    process.goodJets.src = "selectedPatJetsAK8"

process.goodOfflinePrimaryVertex = cms.EDFilter("VertexSelector",
                                       src = cms.InputTag("offlineSlimmedPrimaryVertices"),
                                       cut = cms.string("chi2!=0 && ndof >= 4.0 && abs(z) <= 24.0 && abs(position.Rho) <= 2.0"),
                                       filter = cms.bool(True)
                                       )
if option == 'RECO':
    process.hadronicV.cut = ' '
if option == 'GEN':
    process.hadronicV.cut = ' '
WBOSONCUT = "pt > 200.0"

process.leptonicVSelector = cms.EDFilter("CandViewSelector",
                                       src = cms.InputTag("leptonicV"),
                                       cut = cms.string( WBOSONCUT ),
                                       filter = cms.bool(True)
                                       )
process.leptonicVFilter = cms.EDFilter("CandViewCountFilter",
                                       src = cms.InputTag("leptonicV"),
                                       minNumber = cms.uint32(1),
                                       filter = cms.bool(True)
                                       )
process.hadronicVFilter = cms.EDFilter("CandViewCountFilter",
                                       src = cms.InputTag("hadronicV"),
                                       minNumber = cms.uint32(1),
                                       filter = cms.bool(True)
                                       )
process.graviton = cms.EDProducer("CandViewCombiner",
                                       decay = cms.string("leptonicV hadronicV"),
                                       checkCharge = cms.bool(False),
                                       cut = cms.string("mass > 180"),
                                       roles = cms.vstring('leptonicV', 'hadronicV'),
                                       )
process.gravitonFilter =  cms.EDFilter("CandViewCountFilter",
                                       src = cms.InputTag("graviton"),
                                       minNumber = cms.uint32(1),
                                       filter = cms.bool(True)
                                       )

process.leptonSequence = cms.Sequence(process.muSequence +
                                      process.eleSequence +
                                      process.leptonicVSequence +
                                      process.leptonicVSelector +
                                      process.leptonicVFilter )

process.jetSequence = cms.Sequence(process.substructureSequence +
                                   process.redoPatJets + 
                                   #process.redoPrunedPatJets+
                                   #process.redoSoftDropPatJets+
                                   process.fatJetsSequence +
                                   process.hadronicV +
                                   process.hadronicVFilter)
if doAK8reclustering:
    process.jetSequence = cms.Sequence(process.substructureSequence +
                                       process.redoPatJets + 
                                       process.redoPrunedPatJets+
                                       process.redoSoftDropPatJets+
                                       process.fatJetsSequence +
                                       process.hadronicV +
                                       process.hadronicVFilter)

process.gravitonSequence = cms.Sequence(process.graviton +
                                        process.gravitonFilter)


if filterMode == False:
    process.goodOfflinePrimaryVertex.filter = False
    process.Wtomunu.cut = ''
    process.Wtoenu.cut = ''
    process.leptonicVSelector.filter = False
    process.leptonicVSelector.cut = ''
    process.hadronicV.cut = ''
    process.graviton.cut = ''
    process.leptonicVFilter.minNumber = 0
    process.hadronicVFilter.minNumber = 0
    process.gravitonFilter.minNumber = 0

######### JEC ########
METS = "slimmedMETs"
jetsAK8 = "slimmedJetsAK8"
jetsAK8pruned = "slimmedJetsAK8"
jetsAK8softdrop = ""

if doAK8reclustering:
   jetsAK8 = "selectedPatJetsAK8"
if doAK8prunedReclustering:
   jetsAK8pruned = "selectedPatJetsAK8Pruned"
if doAK8softdropReclustering:
   jetsAK8softdrop = "selectedPatJetsAK8Softdrop"
 
if runOnMC:
   jecLevelsAK8chs = [
                                   'Spring16_25nsV1_MC_L1FastJet_AK8PFchs.txt',
                                   'Spring16_25nsV1_MC_L2Relative_AK8PFchs.txt',
                                   'Spring16_25nsV1_MC_L3Absolute_AK8PFchs.txt'
     ]
   jecLevelsAK8chsGroomed = [
                                   'Spring16_25nsV1_MC_L2Relative_AK8PFchs.txt',
                                   'Spring16_25nsV1_MC_L3Absolute_AK8PFchs.txt'
     ]
   jecLevelsAK4chs = [
                                   'Spring16_25nsV1_MC_L1FastJet_AK4PFchs.txt',
                                   'Spring16_25nsV1_MC_L2Relative_AK4PFchs.txt',
                                   'Spring16_25nsV1_MC_L3Absolute_AK4PFchs.txt'
     ]
else:
   jecLevelsAK8chs = [
                                   'Fall15_25nsV2_DATA_L1FastJet_AK8PFchs.txt',
                                   'Fall15_25nsV2_DATA_L2Relative_AK8PFchs.txt',
                                   'Fall15_25nsV2_DATA_L3Absolute_AK8PFchs.txt',
				   'Fall15_25nsV2_DATA_L2L3Residual_AK8PFchs.txt'
     ]
   jecLevelsAK8chsGroomed = [
                                   'Fall15_25nsV2_DATA_L2Relative_AK8PFchs.txt',
                                   'Fall15_25nsV2_DATA_L3Absolute_AK8PFchs.txt',
				   'Fall15_25nsV2_DATA_L2L3Residual_AK8PFchs.txt'
     ]
   jecLevelsAK4chs = [
                                   'Fall15_25nsV2_DATA_L1FastJet_AK4PFchs.txt',
                                   'Fall15_25nsV2_DATA_L2Relative_AK4PFchs.txt',
                                   'Fall15_25nsV2_DATA_L3Absolute_AK4PFchs.txt',
				   'Fall15_25nsV2_DATA_L2L3Residual_AK4PFchs.txt'
     ]
process.treeDumper = cms.EDAnalyzer("EDBRTreeMaker",
                                    originalNEvents = cms.int32(1),
                                    crossSectionPb = cms.double(1),
                                    targetLumiInvPb = cms.double(1.0),
                                    EDBRChannel = cms.string("VW_CHANNEL"),
                                    isGen = cms.bool(False),
				    isJEC = cms.bool(corrJetsOnTheFly),
				    RunOnMC = cms.bool(runOnMC), 
				    generator =  cms.InputTag("generator"),

                                    genSrc =  cms.InputTag("prunedGenParticles"),
                                    pileup  =   cms.InputTag("slimmedAddPileupInfo"),

                                    Dopruned = cms.bool(doAK8prunedReclustering), 
                                    leptonicVSrc = cms.InputTag("leptonicV"),
                                    gravitonSrc = cms.InputTag("graviton"),
				    looseMuonSrc = cms.InputTag("looseMuons"),
                                    looseElectronSrc = cms.InputTag("looseElectrons"),
				    goodMuSrc = cms.InputTag("goodMuons"),
				    MuSrc = cms.InputTag("slimmedMuons"),
                                    EleSrc = cms.InputTag("slimmedElectrons"),
                                    t1muSrc = cms.InputTag("slimmedMuons"),

                                    metSrc = cms.InputTag("slimmedMETs"),
                                    mets = cms.InputTag(METS),
                                    ak4jetsSrc = cms.InputTag("cleanAK4Jets"),      
                                    hadronicVSrc = cms.InputTag("hadronicV"),
                                    hadronicVSrc_raw = cms.InputTag("slimmedJetsAK8"),

				    jets = cms.InputTag("slimmedJets"),
                                    fatjets = cms.InputTag(jetsAK8),
                                    prunedjets = cms.InputTag(jetsAK8pruned),
                                    softdropjets = cms.InputTag(jetsAK8softdrop),
				    jecAK8chsPayloadNames = cms.vstring( jecLevelsAK8chs ),
				    jecAK8chsPayloadNamesGroomed = cms.vstring( jecLevelsAK8chsGroomed ),
				    jecAK4chsPayloadNames = cms.vstring( jecLevelsAK4chs ),
				    jecpath = cms.string(''),
				    rho = cms.InputTag("fixedGridRhoFastjetAll"),
                                    electronIDs = cms.InputTag("heepElectronID-HEEPV50-CSA14-25ns"),
				    muons = cms.InputTag("slimmedMuons"),
				    vertices = cms.InputTag("offlineSlimmedPrimaryVertices"),
                                    hltToken    = cms.InputTag("TriggerResults","","HLT"),
                                    elPaths1     = cms.vstring("HLT_Ele105_CaloIdVT_GsfTrkIdT_v*"),#EXO-15-002
#                                    elPaths1     = cms.vstring("HLT_Ele105_CaloIdVT_GsfTrkIdT_v*"),#EXO-15-002
                                    elPaths2     = cms.vstring("HLT_Ele27_eta2p1_WP75_Gsf_v*", "HLT_Ele27_eta2p1_WPLoose_Gsf_v*"), #B2G-15-005
                                    muPaths1     = cms.vstring("HLT_Mu45_eta2p1_v*"),#EXO-15-002
                                    muPaths2     = cms.vstring("HLT_IsoMu20_v*","HLT_IsoTkMu20_v*"), #B2G-15-005
                                    muPaths3     = cms.vstring("HLT_IsoMu27_v*"), #B2G-15-005
				    noiseFilter = cms.InputTag('TriggerResults','', hltFiltersProcessName),
				    noiseFilterSelection_HBHENoiseFilter = cms.string('Flag_HBHENoiseFilter'),
				    noiseFilterSelection_HBHENoiseIsoFilter = cms.string("Flag_HBHENoiseIsoFilter"),
				    noiseFilterSelection_CSCTightHaloFilter = cms.string('Flag_CSCTightHaloFilter'),
				    noiseFilterSelection_EcalDeadCellTriggerPrimitiveFilter = cms.string('Flag_EcalDeadCellTriggerPrimitiveFilter'),
				    noiseFilterSelection_goodVertices = cms.string('Flag_goodVertices'),
				    noiseFilterSelection_eeBadScFilter = cms.string('Flag_eeBadScFilter'),
                                    )


if option=='GEN':
    process.treeDumper.metSrc = 'genMetTrue'
    process.treeDumper.isGen  = True
 

process.analysis = cms.Path(process.leptonSequence +
                            #process.substructureSequence+
                            #process.redoPatJets+
                            #process.redoPrunedPatJets+
                            #process.redoSoftDropPatJets+
                            process.jetSequence +
                            process.gravitonSequence +
                            process.treeDumper)

if option=='RECO':
    process.analysis.replace(process.leptonSequence, process.goodOfflinePrimaryVertex + process.leptonSequence)

process.load("ExoDiBosonResonances.EDBRCommon.data.RSGravitonToWW_kMpl01_M_1000_Tune4C_13TeV_pythia8")
#process.source.fileNames = ["/store/user/qili/Bulk-1TeV-WWlvqq/test-DR3-v2/150929_023229/0000/EXO-RunIISpring15DR74-01026_3.root"]
#process.source.fileNames = ["file:/afs/cern.ch/user/h/huangh/work/750/BG_700/CMSSW_7_4_14/src/EXO-RunIISpring15MiniAODv2-00020.root"]process.source.fileNames = ["/store/mc/RunIISpring15MiniAODv2/WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/MINIAODSIM/74X_mcRun2_asymptotic_v2-v1/10000/003F1529-D36D-E511-9E33-001E6724816F.root"]
process.source.fileNames = [
"/store/mc/RunIISpring16MiniAODv1/BulkGravToWWToWlepWhad_narrow_M-2000_13TeV-madgraph/MINIAODSIM/PUSpring16RAWAODSIM_80X_mcRun2_asymptotic_2016_v3-v1/50000/7A727385-5311-E611-B1E7-1CC1DE18CEEE.root"
]

#process.source.fileNames = ["/store/mc/RunIISpring15MiniAODv2/BulkGravToWWToWlepWhad_narrow_M-800_13TeV-madgraph/MINIAODSIM/74X_mcRun2_asymptotic_v2-v1/30000/8C28C338-A270-E511-AF5A-002590747DD8.root"]
#process.source.fileNames = ["file:/afs/cern.ch/user/h/huangh/work/qun/CMSSW_7_4_14/src/ExoDiBosonResonances/EDBRTreeMaker/test/pickevents.root"]#E8E53BA6-A56D-E511-A852-0025905A60CA.root"]
#process.source.fileNames = ["/store/mc/RunIISpring15MiniAODv2/WJetsToLNu_HT-2500ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/MINIAODSIM/74X_mcRun2_asymptotic_v2-v1/50000/E8E53BA6-A56D-E511-A852-0025905A60CA.root"]
#BE582D37-D06D-E511-85E5-0025905938B4.root"]
#BC5FF0E1-AD6D-E511-97E2-0025905A6132.root"]
#B025947A-D06D-E511-9152-0026189438DD.root"]
#6E1B2C1C-CF6D-E511-8970-0025905964CC.root"]
#0A65CA08-A06D-E511-ABB4-003048FFCBA4.root"]
#/store/mc/RunIISpring15DR74/ZZ_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/Asympt50ns_MCRUN2_74_V9A-v2/00000/86B0F321-9D0C-E511-9354-002590D9D8D4.root"]


process.maxEvents.input = -1
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 5000
process.MessageLogger.cerr.FwkReport.limit = 99999999

process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string("RStreeEDBR_pickup.root")
                                   )
