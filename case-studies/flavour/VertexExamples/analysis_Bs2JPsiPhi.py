import sys
import ROOT

print ("Load cxx analyzers ... ",)
ROOT.gSystem.Load("libedm4hep")
ROOT.gSystem.Load("libpodio")
ROOT.gSystem.Load("libFCCAnalyses")
ROOT.gSystem.Load("libFCCAnalysesFlavour")

ROOT.gErrorIgnoreLevel = ROOT.kFatal
_edm  = ROOT.edm4hep.ReconstructedParticleData()
_pod  = ROOT.podio.ObjectID()
_fcc  = ROOT.dummyLoader
_bs  = ROOT.dummyLoaderFlavour

print ('edm4hep  ',_edm)
print ('podio    ',_pod)
print ('fccana   ',_fcc)

#
#	This is used to process a file in which the Bs and the Bsbar are forced
#	to decay into Jpsi ( -> mu mu) + Phi ( -> K K )
#	We reconstruct the secondary vertex from the 2 muon and 2 kaon tracks.
#       The example also shows how to retrieve the MC and reco'ed Bs legs,
#       as well as the MC Bs, JP]psi and Phis, with their kinematics.
#
#       Example file: 
#       /eos/experiment/fcc/ee/examples/lowerTriangle/p8_ecm91GeV_Zbb_EvtGen_Bs2JpsiPhi_IDEAtrkCov.root
# 	Note: these events were generated at (0,0,0), i.e.no smearing of the
#	primary vertex.
#
#Filter=""



class RDFanalysis():

    def analysers(df):
        
        df2 = (df

               .Alias("Particle1", "Particle#1.index")
               .Alias("MCRecoAssociations0", "MCRecoAssociations#0.index")
               .Alias("MCRecoAssociations1", "MCRecoAssociations#1.index")


               # MC event primary vertex
               .Define("MC_PrimaryVertex",  "FCCAnalyses::MCParticle::get_EventPrimaryVertex(21)( Particle )" )

               # the recoParticles corresponding  to the tracks that are primaries, according to MC-matching :
               .Define("MC_PrimaryTracks_RP",  "VertexingUtils::SelPrimaryTracks(MCRecoAssociations0,MCRecoAssociations1,ReconstructedParticles,Particle, MC_PrimaryVertex)" )
               # and the corresponding tracks :
               .Define("MC_PrimaryTracks",  "ReconstructedParticle2Track::getRP2TRK( MC_PrimaryTracks_RP, EFlowTrack_1)" )

               # number of tracks in the event
               .Define("ntracks_Primary","ReconstructedParticle2Track::getTK_n(MC_PrimaryTracks)")
               .Define("ntracks","ReconstructedParticle2Track::getTK_n(EFlowTrack_1)")

               # Retrieve the decay vertex of all MC particles
               #.Define("MC_DecayVertices",  "FCCAnalyses::MCParticle::get_endPoint( Particle, Particle1)" )


               # MC indices of the decay Bs (PDG = 531) -> mu+ (PDG = -13) mu- (PDG = 13) K+ (PDG = 321) K- (PDG = -321)
               # Retrieves a vector of int's which correspond to indices in the Particle block
               # vector[0] = the mother, and then the daughters in the order specified, i.e. here
               #       [1] = the mu+, [2] = the mu-, [3] = the K+, [4] = the K-
               # The first boolean below: when set to true, the dsughters specified in the list are looked
               # for among the final, stable particles that come out from the mother, i.e. the decay tree is
	       # explored recursively if needed.
               # The second boolean: when set to true, the charge conjugate decays are included too.
               # If the event contains more than one such decays,only the first one is kept.
	       # get_indices_ExclusiveDecay looks for an exclusive decay: if a mother is found, that decays 
               # into the particles specified in the list plus other particle(s), this decay is not selected.
               .Define("Bs2MuMuKK_indices",  "FCCAnalyses::MCParticle::get_indices_ExclusiveDecay( 531, {-13,13,321,-321}, true, true) ( Particle, Particle1)" )

                # the MC Bs : the Bs is the first particle in the Bs2MuMuKK_indices vector
               .Define("Bs",  "selMC_leg(0) ( Bs2MuMuKK_indices, Particle )")

                # and the MC legs of the Bs : the mu+ is the second particle in the vector, etc.
               .Define("Muplus",  " selMC_leg(1)( Bs2MuMuKK_indices, Particle )")
               .Define("Muminus",  " selMC_leg(2)( Bs2MuMuKK_indices, Particle )")
               .Define("Kplus",  " selMC_leg(3)( Bs2MuMuKK_indices, Particle )")
               .Define("Kminus",  " selMC_leg(4)( Bs2MuMuKK_indices, Particle )")

                # Kinematics of the Bs legs (MC) :
               .Define("Muplus_theta",  "FCCAnalyses::MCParticle::get_theta( Muplus )")
               .Define("Muplus_phi",  "FCCAnalyses::MCParticle::get_phi( Muplus )")
               .Define("Muplus_e",  "FCCAnalyses::MCParticle::get_e( Muplus )")
               .Define("Muminus_theta",  "FCCAnalyses::MCParticle::get_theta( Muminus )")
               .Define("Muminus_phi",  "FCCAnalyses::MCParticle::get_phi( Muminus )")
               .Define("Muminus_e",  "FCCAnalyses::MCParticle::get_e( Muminus )")
               .Define("Kplus_theta",  "FCCAnalyses::MCParticle::get_theta( Kplus )")
               .Define("Kplus_phi",  "FCCAnalyses::MCParticle::get_phi( Kplus )")
               .Define("Kplus_e",  "FCCAnalyses::MCParticle::get_e( Kplus )")
               .Define("Kminus_theta",  "FCCAnalyses::MCParticle::get_theta( Kminus )")
               .Define("Kminus_phi",  "FCCAnalyses::MCParticle::get_phi( Kminus )")
               .Define("Kminus_e",  "FCCAnalyses::MCParticle::get_e( Kminus )")

	       # Kinematics of the mother Bs (MC)
               .Define("Bs_theta",   "FCCAnalyses::MCParticle::get_theta( Bs )")
               .Define("Bs_phi",   "FCCAnalyses::MCParticle::get_phi( Bs )")
               .Define("Bs_e",   "FCCAnalyses::MCParticle::get_e( Bs )")
               .Define("Bs_pt",   "FCCAnalyses::MCParticle::get_pt( Bs )")               
               .Define("n_Bs", "FCCAnalyses::MCParticle::get_n( Bs )" )
               
               # Decay vertex of the Bs (MC)
               # Careful with getMC_decayVertex: if Bs -> Bsbar, this returns the prod vertex of the Bsbar !
               #.Define("BsDecayVertex",   "getMC_decayVertex(531, false)( Particle, Particle1)")
               # Hence, use instead a custom method in Bs2JPsiPhi :
               .Define("BsMCDecayVertex",   "BsMCDecayVertex( Bs2MuMuKK_indices, Particle )")

               # Returns the RecoParticles associated with the four  Bs decay products.
               # The size of this collection is always 4 provided that Bs2MuMuKK_indices is not empty,
               # possibly including "dummy" particles in case one of the legs did not make a RecoParticle.
               # This is done on purpose, in order to maintain the mapping with the indices - i.e. the 1st particle in 
               # the list BsRecoParticles is the mu+, then the mu-, etc.
               # (selRP_matched_to_list ignores the unstable MC particles that are in the input list of indices
 	       # hence the mother particle, which is the [0] element of the Bs2MuMuKK_indices vector).
               .Define("BsRecoParticles",  "ReconstructedParticle2MC::selRP_matched_to_list( Bs2MuMuKK_indices, MCRecoAssociations0,MCRecoAssociations1,ReconstructedParticles,Particle)")

               # the corresponding tracks - here, dummy particles, if any, are removed, i.e. one may have < 4 tracks,
               # e.g. if one muon or kaon was emitted outside of the acceptance
               .Define("BsTracks",   "ReconstructedParticle2Track::getRP2TRK( BsRecoParticles, EFlowTrack_1)" )

               # number of tracks in this BsTracks collection ( = the #tracks used to reconstruct the Bs vertex)
               .Define("n_BsTracks", "ReconstructedParticle2Track::getTK_n( BsTracks )")

               # Now we reconstruct the Bs decay vertex using the reco'ed tracks.
               # First the full object, of type Vertexing::FCCAnalysesVertex
               .Define("BsVertexObject",   "FCCAnalyses::VertexFitterSimple::VertexFitter_Tk( 2, BsTracks)" )
               # from which we extract the edm4hep::VertexData object, which contains the vertex positiob in mm
               .Define("BsVertex",  "VertexingUtils::get_VertexData( BsVertexObject )")


	       # We may want to look at the reco'ed Bs legs: in the BsRecoParticles vector, 
               # the first particle (vector[0]) is the mu+, etc :
               .Define("RecoMuplus",   "selRP_leg(0)( BsRecoParticles )")
               .Define("RecoMuminus",  "selRP_leg(1)( BsRecoParticles )")
               .Define("RecoKplus",    "selRP_leg(2)( BsRecoParticles )")
               .Define("RecoKminus",   "selRP_leg(3)( BsRecoParticles )")
               # and their kinematics :
               .Define("RecoMuplus_theta",  "ReconstructedParticle::get_theta( RecoMuplus )")
               .Define("RecoMuplus_phi",  "ReconstructedParticle::get_phi( RecoMuplus )")
               .Define("RecoMuplus_e",  "ReconstructedParticle::get_e( RecoMuplus )")
               .Define("RecoMuminus_theta",  "ReconstructedParticle::get_theta( RecoMuminus )")
               .Define("RecoMuminus_phi",  "ReconstructedParticle::get_phi( RecoMuminus )")
               .Define("RecoMuminus_e",  "ReconstructedParticle::get_e( RecoMuminus )")
               .Define("RecoKplus_theta",  "ReconstructedParticle::get_theta( RecoKplus )")
               .Define("RecoKplus_phi",  "ReconstructedParticle::get_phi( RecoKplus )")
               .Define("RecoKplus_e",  "ReconstructedParticle::get_e( RecoKplus )")
               .Define("RecoKminus_theta",  "ReconstructedParticle::get_theta( RecoKminus )")
               .Define("RecoKminus_phi",  "ReconstructedParticle::get_phi( RecoKminus )")
               .Define("RecoKminus_e",  "ReconstructedParticle::get_e( RecoKminus )")

	       # Looks at the angular separation (3D angles) between the Bs daughters: among
               # all the pairs of particles in BsRecoParticles, retrieve the minimal angular distance,
               # the maximal distance, and the average distance
               .Define("deltaAlpha_max","ReconstructedParticle::angular_separationBuilder(0)( BsRecoParticles )")
               .Define("deltaAlpha_min","ReconstructedParticle::angular_separationBuilder(1)( BsRecoParticles )")
               .Define("deltaAlpha_ave","ReconstructedParticle::angular_separationBuilder(2)( BsRecoParticles )")

	       # To look at the angular separation between the MC Jpsi and the Phi :

	       # First retrieve the indices of the JPsi and the phi :
               # MC indices of the decay Bs (PDG = 531)  -> JPsi (PDG = 443) Phi (PDG = 333)
               # Retrieves a vector of int's which correspond to indices in the Particle block
               # vector[0] = the mother, and then the daughters in the order specified, i.e. here
               #       [1] = the Jpsi, [2] = the phi
               # The first boolean below (here set to false) means that we look for a JPsi and a Phi
               # among the direct daughters of the mother, i.e. the decay tree is not explored down
               # to the final, stable particles.
               # The second boolean (true) means that the charge conjugate decay isincluded too.
               # If the event contains more than one such decays,only the first one is kept.
               # get_indices_ExclusiveDecay looks for an exclusive decay: if a mother is found, that decays 
               # into the particles specified in the list plus other particle(s), this decay is not selected.
               .Define("Bs2JPsiPhi_indices",   "FCCAnalyses::MCParticle::get_indices_ExclusiveDecay( 531, {443,333}, false, true) ( Particle, Particle1)" )

               # This extracts the MC Jpsi. In list of indices determined above, Bs2JPsiPhi_indices,
               # 1 is the position of the Jpsi in the Bs2JPsiPhi_indices vector.
               .Define("JPsi",   "selMC_leg( 1) ( Bs2JPsiPhi_indices , Particle )")
               # Idem: extract the MC Phi. 2 is the position of the Phi in the Bs2JPsiPhi_indices vector.
               .Define("Phi",   "selMC_leg( 2) ( Bs2JPsiPhi_indices , Particle )")

               # From these two MC particles, determine their angular separation
               .Define("Angle_JpsiPhi",  "FCCAnalyses::MCParticle::AngleBetweenTwoMCParticles( JPsi, Phi)" )



               # the reco'ed legs, with the momenta at the Bs decay vertex - instead of at their
	       # point of dca
               .Define("RecoMuplus_atVertex",  "selRP_leg_atVertex(0) ( BsRecoParticles, BsVertexObject, EFlowTrack_1 )")
               .Define("RecoMuplus_atVertex_theta",   "ReconstructedParticle::get_theta( RecoMuplus_atVertex )")
               .Define("RecoMuplus_atVertex_phi",   "ReconstructedParticle::get_phi( RecoMuplus_atVertex )")
               .Define("RecoMuminus_atVertex",  "selRP_leg_atVertex(1) ( BsRecoParticles, BsVertexObject, EFlowTrack_1 )")
               .Define("RecoMuminus_atVertex_theta",   "ReconstructedParticle::get_theta( RecoMuminus_atVertex )")
               .Define("RecoMuminus_atVertex_phi",   "ReconstructedParticle::get_phi( RecoMuminus_atVertex )")
               .Define("RecoKplus_atVertex",  "selRP_leg_atVertex(2) ( BsRecoParticles, BsVertexObject, EFlowTrack_1 )")
               .Define("RecoKplus_atVertex_theta",   "ReconstructedParticle::get_theta( RecoKplus_atVertex )")
               .Define("RecoKplus_atVertex_phi",   "ReconstructedParticle::get_phi( RecoKplus_atVertex )")
               .Define("RecoKminus_atVertex",  "selRP_leg_atVertex(3) ( BsRecoParticles, BsVertexObject, EFlowTrack_1 )")
               .Define("RecoKminus_atVertex_theta",   "ReconstructedParticle::get_theta( RecoKminus_atVertex )")
               .Define("RecoKminus_atVertex_phi",   "ReconstructedParticle::get_phi( RecoKminus_atVertex )")

               # not so useful here, but for completeness : Bs to JPsi decay ?
               # Returns booleans. e.g. the first one means that the event contains a Bs that decayed to a JPsi (443) + X, 
               # not counting the cases where Bs -> Bsbar -> JPsi + X
               .Define("Bsdecay",  "FCCAnalyses::MCParticle::get_decay(531, 443, false)(Particle, Particle1)")
               .Define("Bsbardecay",  "FCCAnalyses::MCParticle::get_decay(-531, 443, false)(Particle, Particle1)")

	            # to get the distribution of the d0 of the mu+ track
	            .Define("RecoMuplus_d0",  "ReconstructedParticle2Track::getRP2TRK_D0( RecoMuplus, EFlowTrack_1) ")
	            .Define("RecoMuplus_z0",  "ReconstructedParticle2Track::getRP2TRK_Z0( RecoMuplus, EFlowTrack_1) ")







                ### SV stuff ###
#               # jet clustering (ee-kt) before reconstructing SVs in event
               .Define("RP_px",  "ReconstructedParticle::get_px(ReconstructedParticles)")
               .Define("RP_py",  "ReconstructedParticle::get_py(ReconstructedParticles)")
               .Define("RP_pz",  "ReconstructedParticle::get_pz(ReconstructedParticles)")
               .Define("RP_e",   "ReconstructedParticle::get_e(ReconstructedParticles)")
#               #build psedo-jets with the Reconstructed final particles
               .Define("pseudo_jets", "JetClusteringUtils::set_pseudoJets(RP_px, RP_py, RP_pz, RP_e)")
#               #run jet clustering with all reco particles. ee_kt_algorithm, exclusive clustering, exactly 2 jets, E-scheme
               .Define("FCCAnalysesJets_ee_kt", "JetClustering::clustering_ee_kt(2, 2, 1, 0)(pseudo_jets)")
#               #get the jets out of the structure
               .Define("jets_ee_kt", "JetClusteringUtils::get_pseudoJets(FCCAnalysesJets_ee_kt)")
#               #get the jet constituents out of the structure
               .Define("jetconstituents_ee_kt", "JetClusteringUtils::get_constituents(FCCAnalysesJets_ee_kt)")

               ### finding SVs in the event ###
               .Define("VertexObject_allTracks",  "FCCAnalyses::VertexFitterSimple::VertexFitter_Tk ( 1, EFlowTrack_1, true, 4.5, 20e-3, 300)")
               .Define("RecoedPrimaryTracks",  "FCCAnalyses::VertexFitterSimple::get_PrimaryTracks( VertexObject_allTracks, EFlowTrack_1, true, 4.5, 20e-3, 300, 0., 0., 0., 0)")

               .Define("PrimaryVertexObject",   "FCCAnalyses::VertexFitterSimple::VertexFitter_Tk ( 1, RecoedPrimaryTracks, true, 4.5, 20e-3, 300) ")
               .Define("IsPrimary_based_on_reco",  "FCCAnalyses::VertexFitterSimple::IsPrimary_forTracks( EFlowTrack_1, RecoedPrimaryTracks  )")

               # Event level
               .Define("SV", "FCCAnalyses::VertexFinderLCFIPlus::get_SV_event(ReconstructedParticles, EFlowTrack_1, PrimaryVertexObject, IsPrimary_based_on_reco)") # first interface
               #.Define("SV", "FCCAnalyses::VertexFinderLCFIPlus::get_SV_event(ReconstructedParticles, EFlowTrack_1, SecondaryTracks, PrimaryVertexObject)")        # second interface

               # From jets
               #.Define("SV", "FCCAnalyses::VertexFinderLCFIPlus::get_SV_jets(ReconstructedParticles, EFlowTrack_1, PrimaryVertexObject, IsPrimary_based_on_reco, jets_ee_kt, jetconstituents_ee_kt)")

               # SV properties
               .Define("SV_position", "VertexingUtils::get_position_SV( SV )")
               .Define("ntracks_SV", "VertexingUtils::get_VertexNtrk(SV)")
               .Define("n_SV", "VertexingUtils::get_n_SV(SV)")
               .Define("SV_mass", "myUtils::get_Vertex_mass( SV, ReconstructedParticles )")
               .Define("SV_mass_twoPions", "VertexingUtils::get_invM_pairs(SV)")
               .Define("SV_mass_allPions", "VertexingUtils::get_invM(SV)")
               .Define("SV_chi2", "VertexingUtils::get_chi2_SV(SV)")
               .Define("d2PV", "myUtils::get_Vertex_d2PV(FCCAnalyses::VertexingUtils::get_all_vertices(PrimaryVertexObject, SV), 0)")
               .Define("d2PV_min", "myUtils::get_dPV2DV_min(d2PV)")
               .Define("d2PV_max", "myUtils::get_dPV2DV_max(d2PV)")
               .Define("d2PV_ave", "myUtils::get_dPV2DV_ave(d2PV)")


               .Define("reco_chi2", "PrimaryVertexObject.reco_chi2")
               .Define("chi2_2", "PrimaryVertexObject.vertex.chi2")           

               .Define("d_SV_BsMCDecayVertex","VertexingUtils::get_d3d_SV_obj(SV, BsMCDecayVertex)" )
               .Define("dR_SV_BsMCDecayVertex","VertexingUtils::get_dR_SV_obj(SV, BsMCDecayVertex)" )
               .Define("dR_min_SV_BsMCDecayVertex","myFinalSel::get_abs_min(dR_SV_BsMCDecayVertex)")

               .Define("d_min_SV_BsMCDecayVertex","myFinalSel::get_abs_min(d_SV_BsMCDecayVertex)")
#               .Filter(Filter)
            )
        return df2

    def output():
        # select branches for output file
        branchList = [
                "IsPrimary_based_on_reco",
                "SV",
                "SV_position",
                "n_SV",
                "SV_mass",
                "SV_mass_twoPions",
                "SV_mass_allPions",
                "SV_chi2",
                "d2PV",
                "d2PV_min",
                "d2PV_max",
                "d2PV_ave",
                "MC_PrimaryVertex",
                "ntracks",
                "ntracks_Primary",
                "MC_PrimaryTracks_RP",
                "MC_PrimaryTracks",
                "d_SV_BsMCDecayVertex",
                "d_min_SV_BsMCDecayVertex",
                "dR_SV_BsMCDecayVertex",
                "dR_min_SV_BsMCDecayVertex",
                "FCCAnalysesJets_ee_kt",
                #"Bs2JPsiPhi_indices",
                #"Bs2MuMuKK_indices",
                #"Muplus",
                #"Muminus",
                #"Kplus",
                #"Kminus",

	        # Kinematics of the MC particles:
                "Muplus_theta",
                "Muplus_phi",
                "Muplus_e",
                "Muminus_theta",
                "Muminus_phi",
                "Muminus_e",
                "Kplus_theta",
                "Kplus_phi",
                "Kplus_e",
                "Kminus_theta",
                "Kminus_phi",
                "Kminus_e",
                "Bs_theta",
				"n_Bs",
                "Bs_phi",
                "Bs_e",
                "Bs_pt",
                "Bsdecay",
                "Bsbardecay",

                # MC Bs decay vertex :
                "BsMCDecayVertex",
		# Reco'ed Bs vertex :
                "BsVertex",
                #"BsTracks",
                "n_BsTracks",

                "deltaAlpha_max",
                "deltaAlpha_min",
                "deltaAlpha_ave",
                #"BsRecoParticles",

	        # Kinematics of the Reco'ed particles:
                "RecoMuplus_theta",
                "RecoMuplus_phi",
                "RecoMuplus_e",
                "RecoMuminus_theta",
                "RecoMuminus_phi",
                "RecoMuminus_e",
                "RecoKplus_theta",
                "RecoKplus_phi",
                "RecoKplus_e",
                "RecoKminus_theta",
                "RecoKminus_phi",
                "RecoKminus_e",

                "RecoMuplus_atVertex_theta",
                "RecoMuplus_atVertex_phi",
                "RecoMuminus_atVertex_theta",
                "RecoMuminus_atVertex_phi",
                "RecoKplus_atVertex_theta",
                "RecoKplus_atVertex_phi",
                "RecoKminus_atVertex_theta",
                "RecoKminus_atVertex_phi",

                "Angle_JpsiPhi",

		"RecoMuplus_d0",
		"RecoMuplus_z0"
                ]
        return branchList
