/**
 * Created by rishisharma on 06/06/16.
 */
angular.module('ops.views.createUserCar', [
    'ops.services.booking',
    'ops.services.user',
    'ops.services.common',
    'ops.services.data'
])
    .controller('UserCarController', function UserCarController($state,$scope, $stateParams, DataService,
                                                                BookingService, CommonService, UserService){
        var self=this;
        self.selectedYear = null;
        self.years = {
            '2017':'2017',
            '2016':'2016',
            '2015':'2015',
            '2014':'2014',
            '2013':'2013',
            '2012':'2012',
            '2011':'2011',
            '2010':'2010',
            '2009':'2009',
            '2008':'2008',
            '2007':'2007',
            '2006':'2006',
            '2005':'2005',
            '2004':'2004',
            '2003':'2003',
            '2002':'2002',
            '2001':'2001',
            '2000':'2000',
            '1999':'1999',
            '1998':'1998',
        };
        var current_ops_user = UserService.getCurrentUser();

        self.bookingSource = DataService.newBooking.userSource;
        self.bookingCity = ''+DataService.newBooking.userCity;

        CommonService.getMasterData(self.bookingCity).then(function(res){
            self.bookingSources = res.new_sources;
        });

        CommonService.getCities().then(function(res){
            self.cities = res;
        });

        BookingService.getModel()
            .then( function (data) {
                if (data.data.results) {
                    self.popular_cars = data.data.results;
                }
            });

        function getModel(searchText) {
            if(searchText) {
                BookingService.getModel( searchText )
                    .then( function (data) {
                        if (data.data.results) {
                            self.models = data.data.results;
                        }
                    } );
            }
        }
        function setSelectedCar(selected_car) {
            self.selectedCar=selected_car;
            if(selected_car) {
                jQuery('#search_car_text').val(selected_car.brand.name+'-'+selected_car.name);
            }
        }
        function saveSelectedCar() {
            if(self.selectedCar){
                if(self.selectedYear){
                    BookingService.getModelByYear(self.selectedCar.id,self.selectedYear).then(function (data) {
                        if(data){
                            self.selectedCar = data.data;
                            saveUserCar();
                        }
                    });
                }
                else {
                    saveUserCar();
                }
            }else{
                sweetAlert("Error", "Select car from search result at bottom of page.", "error");
            }
        }
        function saveUserCar() {
            var res=BookingService.saveUserCar(DataService.newBooking.userId,self.selectedCar.id,self.selectedYear);
            res.success(function (result) {
                sweetAlert("user car saved");
                DataService.newBooking.userCar=result.id;

                //create empty booking
                var obj=BookingService.createBooking({
                        'user_id': DataService.newBooking.userId,
                        'usercar': result.id,
                        'source': self.bookingSource,
                        'city': self.bookingCity,
                        //'rework_booking': self.reworkBookingId? self.reworkBookingId: null,
                        'assigned_to': current_ops_user.id,
                        'caller': current_ops_user.id
                    }
                );
                obj.success(function (result) {
                    DataService.newBooking.bookingID= result.id;
                    $state.go('base.createUser.addPackage');
                }).error(function (result) {
                    sweetAlert("oops error in getting details contact admin");
                });
            });
        }

        self.getModel=getModel;
        self.setSelectedCar=setSelectedCar;
        self.saveSelectedCar=saveSelectedCar;
    });