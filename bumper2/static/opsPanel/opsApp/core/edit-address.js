/**
 * Created by Indy on 06/02/17.
 */
function UserAddressModalInstanceCtrl($uibModalInstance, $timeout, userId, bookingId, addressType, BookingService,
                                      UserService, $scope) {
    var self = this;
    self.ajax_loading = false;
    self.showEditAddress = false;

    UserService.getUserAddressByUserId(userId).then(function (data) {
        if(data){
            self.existingAddresses = data.results;
        }
    });

    function editAddress(userAddressId){
        self.showEditAddress = true;
        if(userAddressId){
            self.userAddress = _.find(self.existingAddresses,{id:userAddressId});
        }else{
            self.userAddress = {
                "user": userId,
                "alias": null,
                "address": {
                    "address1": null,
                    "address2": null,
                    "pin_code": null,
                    "area": null,
                    "city": null,
                    "state": null,
                    "country": null,
                    "latitude": null,
                    "longitude": null
                }
            };
        }
        $timeout(function () {
            angular.element('#addressLine1').focus();
        },500);
    }

    function saveAddress() {
        angular.forEach(self.userAddress.address, function (value, key) {
            if (value === "") {
                self.userAddress.address[key] = null;
            }
            self.showEditAddress = false;
        });

        UserService.saveUserAddress(self.userAddress).success(function (result) {
            setAddressAsUserAddress(result.id);
        }).error(function (result) {
            sweetAlert("Error", "Error in saving new address", "error");
        });
    }

    function setAddressAsUserAddress(addressId) {
        self.updatedFor = {"booking": bookingId, "useraddress_id": addressId, "type": addressType};
        var res = BookingService.updateBookingAddress(self.updatedFor);
        res.success(function (result) {
            $uibModalInstance.close('saved');
        }).error(function(result){
            sweetAlert("Error", "error in updating Booking address", "error");
        });
    }

    function onSelectGoogleAddress(googleMapData){
        // console.log('googleMapData->', googleMapData);
        if(googleMapData){
            self.userAddress.address.area = googleMapData.formattedAddress ? googleMapData.formattedAddress: self.userAddress.address.area;
            self.userAddress.address.city = googleMapData.cityName;
            self.userAddress.address.country = googleMapData.countryCode;
            self.userAddress.address.state = googleMapData.regionName;
            self.userAddress.address.pin_code = googleMapData.zipCodeId ? googleMapData.zipCodeId:self.userAddress.address.pin_code;
            self.userAddress.address.latitude = googleMapData.latitude;
            self.userAddress.address.longitude = googleMapData.longitude? googleMapData.longitude.toFixed(7):self.userAddress.address.longitude;
        }
    }

    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    self.setAddressAsUserAddress = setAddressAsUserAddress;
    self.saveAddress = saveAddress;
    self.editAddress = editAddress;
    self.onSelectGoogleAddress = onSelectGoogleAddress;
}