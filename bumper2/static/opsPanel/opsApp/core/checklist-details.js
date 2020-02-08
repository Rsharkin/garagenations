/**
 * Created by Indy on 01/03/17.
 */
function ShowChecklistDetailsModalInstanceCtrl($uibModalInstance, items, typeOfChecklist) {
    var self = this;
    self.items = items;
    self.typeOfChecklist = typeOfChecklist;
    console.log('items->', items);
    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}