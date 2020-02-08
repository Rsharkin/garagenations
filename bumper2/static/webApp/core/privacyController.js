/**
 * Created by rishisharma on 01/03/17.
 */

angular.module('bumper.view.privacy', [
    'bumper.services.common',
    'bumper.services.user'
])
    .controller('privacyController', function privacyController($location,$anchorScroll) {
        var old = $location.hash();
        $location.hash('headerTop');
        $anchorScroll();
        $location.hash(old);
        var self =this;
    });