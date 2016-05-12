import FWCore.ParameterSet.Config as cms

def customizeMets(process,coll,**kwargs):
    '''Customize METs'''
    isMC = kwargs.pop('isMC',False)
    metSrc = coll['pfmet']
    jSrc = coll['jets']
    pSrc = coll['photons']
    eSrc = coll['electrons']
    mSrc = coll['muons']
    tSrc = coll['taus']
    pfSrc = coll['packed']

    process.metCustomization = cms.Path()

    #################################
    ### recompute met uncertainty ###
    #################################
    postfix = "New"
    from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
    runMetCorAndUncFromMiniAOD(process,
                               jetCollUnskimmed="slimmedJets",
                               jetColl=jSrc,
                               photonColl=pSrc,
                               electronColl=eSrc,
                               muonColl=mSrc,
                               tauColl=tSrc,
                               pfCandColl=pfSrc,
                               isData=not isMC,
                               jetFlav="AK4PFchs",
                               postfix=postfix)

    # correct things to make it work
    getattr(process,'patPFMetTxyCorr{0}'.format(postfix)).vertexCollection = cms.InputTag('offlineSlimmedPrimaryVertices')
    del getattr(process,'slimmedMETs{0}'.format(postfix)).caloMET

    metSrc = "slimmedMETs{0}".format(postfix)
    
    ####################
    ### embed shifts ###
    ####################
    for shift in ['JetRes','JetEn','MuonEn','ElectronEn','TauEn','UnclusteredEn','PhotonEn']:
        for sign in ['Up','Down']:
            mod = cms.EDProducer(
                "ShiftedMETEmbedder",
                src = cms.InputTag(metSrc),
                label = cms.string('{0}{1}'.format(shift,sign)),
                shiftedSrc = cms.InputTag('patPFMetT1{0}{1}{2}'.format(shift,sign,postfix)),
            )
            modName = 'embed{0}{1}'.format(shift,sign)
            setattr(process,modName,mod)
            metSrc = modName
            process.metCustomization += getattr(process,modName)

    for sign in ['Up','Down']:
        # electrons
        shift = 'ElectronEn'
        mod = cms.EDProducer(
            "ShiftedElectronEmbedder",
            src = cms.InputTag(eSrc),
            label = cms.string('{0}{1}'.format(shift,sign)),
            shiftedSrc = cms.InputTag('shiftedPat{0}{1}{2}'.format(shift,sign,postfix)),
        )
        modName = 'electronEmbed{0}{1}'.format(shift,sign)
        setattr(process,modName,mod)
        eSrc = modName
        process.metCustomization += getattr(process,modName)
        # muons
        shift = 'MuonEn'
        mod = cms.EDProducer(
            "ShiftedMuonEmbedder",
            src = cms.InputTag(mSrc),
            label = cms.string('{0}{1}'.format(shift,sign)),
            shiftedSrc = cms.InputTag('shiftedPat{0}{1}{2}'.format(shift,sign,postfix)),
        )
        modName = 'muonEmbed{0}{1}'.format(shift,sign)
        setattr(process,modName,mod)
        mSrc = modName
        process.metCustomization += getattr(process,modName)
        # taus
        shift = 'TauEn'
        mod = cms.EDProducer(
            "ShiftedTauEmbedder",
            src = cms.InputTag(tSrc),
            label = cms.string('{0}{1}'.format(shift,sign)),
            shiftedSrc = cms.InputTag('shiftedPat{0}{1}{2}'.format(shift,sign,postfix)),
        )
        modName = 'tauEmbed{0}{1}'.format(shift,sign)
        setattr(process,modName,mod)
        tSrc = modName
        process.metCustomization += getattr(process,modName)
        # jets
        shift = 'JetEn'
        mod = cms.EDProducer(
            "ShiftedJetEmbedder",
            src = cms.InputTag(jSrc),
            label = cms.string('{0}{1}'.format(shift,sign)),
            shiftedSrc = cms.InputTag('shiftedPat{0}{1}{2}'.format(shift,sign,postfix)),
        )
        modName = 'jetEmbed{0}{1}'.format(shift,sign)
        setattr(process,modName,mod)
        jSrc = modName
        process.metCustomization += getattr(process,modName)

    process.schedule.append(process.metCustomization)

    coll['pfmet'] = metSrc
    coll['muons'] = mSrc
    coll['electrons'] = eSrc
    coll['taus'] = tSrc
    coll['jets'] = jSrc

    return coll