/**
 * Bumper
 *
 */
/**
 * pageTitle - Directive for set Page title - mata title
 */
function pageTitle($rootScope, $timeout) {
    return {
        link: function(scope, element) {
            var listener = function(event, toState, toParams, fromState, fromParams) {
                // Default title - load on Home Page
                var title = 'Bumper';
                // Create your own title pattern
                if (toState.data && toState.data.pageTitle) title = 'Bumper | ' + toState.data.pageTitle;
                $timeout(function() {
                    element.text(title);
                });
            };
            $rootScope.$on('$stateChangeStart', listener);
        }
    }
}
function bumperGoogleAutocomplete(BookingDataService) {
    return {
        replace: true,
        require: 'ngModel',
        scope: {
            ngModel: '=',
            googleModel: '=',
            onSelect: '&?',	// optional callback on selected successfully: 'onPostedBid(googleModel)'
        },
        template: '<input name="address2" style="font-weight:600" type="text" autocomplete="off" required/>',
        link: function ($scope, element, attrs, model) {
            var self = this;
            var city = BookingDataService.getSelectedCityFromLocal();
            if(city.id ==1){
                self.locatn = new google.maps.LatLng(12.9716, 77.5946);
            }
            else {
                self.locatn = new google.maps.LatLng(28.7041, 77.1025);
            }

            var googleOptions = {
                location:self.locatn,
                radius: 50000,
                types: ['geocode'], // change or empty it, if you want no restrictions
                componentRestrictions: { country: 'in' }  // change or empty it, if you want no restrictions
            };

            var autocomplete = new google.maps.places.Autocomplete(element[0], googleOptions);
            google.maps.event.addListener(autocomplete, 'place_changed', function () {

                /**
                 * Search gor the passed 'type' of info into the google place component
                 * @param {type} components
                 * @param {type} type
                 * @returns {type}
                 */
                $scope.extract = function (components, type) {
                    for (var i = 0; i < components.length; i++)
                        for (var j = 0; j < components[i].types.length; j++)
                            if (components[i].types[j] == type) return components[i].short_name;
                    return '';
                };

                $scope.$apply(function () {
                    var place = autocomplete.getPlace();
                    if (!place.geometry) {
                        // User entered the name of a Place that was not suggested and pressed the Enter key, or the Place Details request failed.
                        model.$setValidity('place', false);
                        //console.log("No details available for input: '" + place.name + "'");
                        return;
                    }
                    $scope.googleModel = {};
                    $scope.googleModel.placeId = place.place_id;
                    $scope.googleModel.latitude = place.geometry.location.lat();
                    $scope.googleModel.longitude = place.geometry.location.lng();
                    $scope.googleModel.formattedAddress = place.formatted_address;
                    $scope.googleModel.address_component = place.address_components;
                    if (place.address_components) {
                        $scope.googleModel.address = [
                            $scope.extract(place.address_components, 'route'),
                            $scope.extract(place.address_components, 'street_number')
                        ].join(' ');
                        $scope.googleModel.cityName = $scope.extract(place.address_components, 'locality');
                        $scope.googleModel.provName = $scope.extract(place.address_components, 'administrative_area_level_2');
                        $scope.googleModel.regionName = $scope.extract(place.address_components, 'administrative_area_level_1');
                        $scope.googleModel.zipCodeId = $scope.extract(place.address_components, 'postal_code');
                        $scope.googleModel.countryCode = $scope.extract(place.address_components, 'country');
                    }

                    model.$setViewValue(element.val());
                    model.$setValidity('place', true);
                    if (attrs.onSelect) $scope.onSelect({ $item: $scope.googleModel });
                });
            });
        }
    };
}

angular
    .module('bumper')
    .directive('pageTitle', pageTitle)
    .directive('bumperGoogleAutocomplete', bumperGoogleAutocomplete);



