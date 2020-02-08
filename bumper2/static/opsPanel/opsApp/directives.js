/**
 * ops
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
                //console.log('Setting title, value in data->',toParams);
                if (toState.data && toState.data.pageTitle){
                    if(toState.data.pageTitle.trim() == 'Edit Booking'){
                        title = toParams.bookingId + ' Booking';
                    }else{
                        title = toState.data.pageTitle;
                    }
                }
                $timeout(function() {
                    element.text(title);
                });
            };
            $rootScope.$on('$stateChangeStart', listener);
        }
    };
}

function checkGroupPermission(UserService){
    return {
        restrict: 'A',
        scope: {
            permission: '='
        },

        link: function (scope, elem, attrs) {
            var allowed_roles = scope.permission;

            // console.log('permissionBookingStatus->', attrs.permissionStatusCheck, allowed_roles);
            // if(attrs.permissionStatusCheck){
            //     console.log('json->', JSON.parse(attrs.permissionStatusCheck));
            // }


            if(UserService.isUserInGroup(allowed_roles)){
                elem.show();
            }else{
                elem.hide();
            }
        }
    };
}
//Binding select to a non-string value via ngModel parsing / formatting
function convertToNumber() {
  return {
    require: 'ngModel',
    link: function(scope, element, attrs, ngModel) {
      ngModel.$parsers.push(function(val) {
        return val !== null ? parseInt(val, 10) : null;
      });
      ngModel.$formatters.push(function(val) {
        return val !== null ? '' + val : null;
      });
    }
  };
}

function bumperGoogleAutocomplete() {
	return {
		replace: true,
		require: 'ngModel',
		scope: {
			ngModel: '=',
			googleModel: '=',
			onSelect: '&?',	// optional callback on selected successfully: 'onPostedBid(googleModel)'
		},
		template: '<input class="form-control" style="margin-top:10px;" placeholder="Search Google Maps" type="text" autocomplete="off">',
		link: function ($scope, element, attrs, model) {
			var googleOptions = {
				types: ['geocode'],  // change or empty it, if you want no restrictions
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

/**
 *
 * Pass all functions into module
 */
angular
    .module('ops')
    .directive('pageTitle', pageTitle)
    .directive('permission', ['UserService', checkGroupPermission])
    .directive('convertToNumber', convertToNumber)
    .directive('bumperGoogleAutocomplete', bumperGoogleAutocomplete);

