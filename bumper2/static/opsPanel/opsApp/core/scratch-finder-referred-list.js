/**
 * Created by Indy on 06/03/17.
 */
function ScratchFinderReferredListCtrl($uibModalInstance, CommonService, referrerId, referrerName, sfStatuses){
    var self = this;

    self.ajax_loading = false;
    self.referrerName = referrerName;
    self.sfStatuses = sfStatuses;

    CommonService.getScratchFinderLeadsByReferrer(referrerId).then(function(referredList){
        self.referredList = referredList;
    });

    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}