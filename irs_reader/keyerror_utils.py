

ignorable_keyerrors = ['/ReturnHeader/BuildTS']

# 2013 vars that no longer exist
discontinued_2013_vars = [ '/IRS990ScheduleA/CertificationInd', '/IRS990ScheduleA/Contribution35ControlledInd', '/IRS990ScheduleA/ContributionControllerInd', '/IRS990ScheduleA/ContributionFamilyInd', '/IRS990ScheduleA/Form990ScheduleAPartIVGrp/ExplanationTxt', '/IRS990ScheduleA/SupportedOrgInformationGrp/SupportedOrgNotifiedInd', '/IRS990ScheduleA/SupportedOrgInformationGrp/USOrganizedInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/AdoptBudgetInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/AdoptImplementationStrategyInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/AllNeedsAddressedInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/AttachedToInvoiceInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/AvailableOnRequestInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/BodyAttachmentsInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/DevelopCommunityWidePlanInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/ExecCommunityWidePlanInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/ExecImplementationStrategyInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/FPGUsedDeterEligFreeCareInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/FPGUsedDetermEligDscntCareInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/IncludeOperationalPlanInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/LawsuitInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/LiensOnResidencesInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/MedicaidMedicareInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/OtherNeedsAddressedInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/PermitBodyAttachmentsInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/PermitLawsuitInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/PermitLienOnResidenceInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/PostedInAdmissionOfficeInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/PostedInEmergencyRoomInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/PrioritizeHealthNeedsInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/PrioritizeServicesInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/ProvidedOnAdmissionInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/StateRegulationInd', '/IRS990ScheduleH/HospitalFcltyPoliciesPrctcGrp/UninsuredDiscountInd']


ignorable = ignorable_keyerrors + discontinued_2013_vars

def ignorable_keyerror(xpath):
    if xpath in ignorable:
        return True

    return False

"""

These are missing:

/IRS990PF/OfficerDirTrstKeyEmplInfoGrp/CompensationOfHghstPdCntrctGrp/BusinessName/BusinessNameLine1Txt
/IRS990PF/OfficerDirTrstKeyEmplInfoGrp/CompensationOfHghstPdCntrctGrp/BusinessName/BusinessNameLine2Txt

/IRS990PF/OfficerDirTrstKeyEmplInfoGrp/OfficerDirTrstKeyEmplGrp/BusinessName/BusinessNameLine1Txt
/IRS990PF/OfficerDirTrstKeyEmplInfoGrp/OfficerDirTrstKeyEmplGrp/BusinessName/BusinessNameLine2Txt

/IRS990EZ/OfficerDirectorTrusteeEmplGrp/BusinessName/BusinessNameLine1Txt
/IRS990EZ/OfficerDirectorTrusteeEmplGrp/BusinessName/BusinessNameLine2Txt


"""