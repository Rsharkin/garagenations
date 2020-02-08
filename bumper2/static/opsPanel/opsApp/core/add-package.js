/**
 * Created by rishisharma on 08/06/16.
 */
angular.module('ops.views.addPackage', [
    'ops.services.booking',
    'ops.services.user',
    'ops.services.common',
    'ops.services.data'
])
    .controller('AddPackageController', function AddPackageController($state,DataService){
        var self=this;
        self.bookingId=DataService.newBooking.bookingID;
    });