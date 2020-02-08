/**
 * Created by Indy on 06/03/17.
 */
function EditScratchFinderLead($uibModalInstance, CommonService, leadId, currentStatus , sfStatuses){
    var self = this;

    self.ajax_loading = false;

    self.leadId = leadId;
    self.sfStatuses = sfStatuses;
    self.modalItem = {
        'status': currentStatus
    };

    self.ok = function () {
        self.ajax_loading = true;
        self.errorMsgs = [];

        CommonService.updateScratchFinderLead(leadId, self.modalItem)
            .success(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "Lead Updated", "success");
                $uibModalInstance.close('saved');
            })
            .error(function(response){
                self.ajax_loading = false;
                var status = response.status;
                if(status == '401'){
                    self.errorMsgs.push("You don't have permission required to do this action.");
                }else if(status == '400'){
                    self.errorMsgs.push('Please make sure all values are correctly filled: ' + response.data.data[0]);
                }else{
                    self.errorMsgs.push("Errors: Server Error");
                }
            });
    };

    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}