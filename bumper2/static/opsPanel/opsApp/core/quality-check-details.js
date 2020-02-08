/**
 * Created by Indy on 28/02/17.
 */
function QualityChecksModalInstanceCtrl($uibModalInstance, bookingId, BookingService,version){
    var self = this;

    self.ajax_loading = false;
    self.bookingId = bookingId;

    if(version ===1){
        BookingService.getQualityChecks(bookingId).then(function(res){
            self.testedQualityChecks = res;
        });
    }
    if(version===2){
        BookingService.getOldQualityChecks(bookingId).then(function(res){
            self.testedQualityChecksOld = res;
        });
    }
    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}