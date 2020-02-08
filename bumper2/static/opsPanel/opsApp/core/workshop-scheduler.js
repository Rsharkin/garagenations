/**
 * Created by Indy on 12/07/17.
 */
angular.module('ops.views.workshopScheduler',[
    'ops.services.common',
    'ops.services.data'
]).controller('WSCtrl', function($scope, CommonService, DataService){
    var self = this;
    self.today = moment().format('YYYY-MM-DD');
    self.ajax_loading = false;
    self.inputs={
        removeList: DataService.getRemovedBookings(),
        useCurrentStatus:0,
        workshop: '17' // KG2,3
    };

    function generateSchedule(){
        self.ajax_loading = true;
        //console.log('inputs',self.inputs);

        self.summaryDates = [];
        self.workshopWiseSummary = {
            'tot_num_bookings': 0,
            'tot_num_bookings_delay_sla': 0,
            'tot_num_bookings_delay_eta': 0
        };

        CommonService.getWorkshopSchedule(self.inputs).then(function(response){
            self.ajax_loading = false;
            DataService.saveRemovedBookings(self.inputs.removeList);
            //console.log('response->', response);

            self.daysToPlanFor = response.days_to_plan_for;
            self.allBookingsWithEOD = response.all_bookings_with_eod;
            self.resource_schedule = response.bumper_workshop_resources;
            self.dateWiseWork = response.datewise_booking_allocation;
            self.projectedDelayedBookings = response.projected_delayed_bookings;

            self.sequenceForToday = {
                "Denter": [],
                "Painter": [],
                "PainterHelper": [],
                "Paintbooth": [],
                "Polisher": [],
                "WashingBay": [],
                "Batman": []
            };
            self.workSequenceForToday = {};
            self.workSequenceForTodayOrdered = {};

            var i=0,
                j=0,
                processingDate = moment().format('YYYY-MM-DD'),
                bookingObj={},
                workDetails={},
                taskListForDate=[],
                isWorkDoneToday=false;

            for(i=0; i < 4; i++){
                self.summaryDates.push(moment().add(i, 'days').format('YYYY-MM-DD'));
            }

            // console.log('self.projectedDelayedBookings->', self.projectedDelayedBookings);
            for(i=0; i < self.projectedDelayedBookings.length; i++){
                var delay_detail = self.projectedDelayedBookings[i].split('_');
                self.workshopWiseSummary.tot_num_bookings_delay_sla += 1;
            }

            if(self.inputs.useCurrentStatus && moment().hours() >= 19){
                processingDate = moment().add(1, 'days').format('YYYY-MM-DD');
            }
            self.processingDate = processingDate;
            //console.log("Processing Date->", processingDate, self.allBookingsWithEOD);
            for(j=0; j< self.allBookingsWithEOD.length; j++){
                self.workshopWiseSummary.tot_num_bookings += 1;
                if(self.allBookingsWithEOD[j].cannot_meet_workshop_eta){
                    self.workshopWiseSummary.tot_num_bookings_delay_eta += 1;
                }

                if(self.allBookingsWithEOD[j].work_to_done_in_day_datewise[processingDate]){
                    //console.log(processingDate,self.allBookingsWithEOD[j].booking_id);
                    workDetails = self.allBookingsWithEOD[j].work_to_done_in_day_datewise[processingDate].total_time_used_for_date;
                    if(workDetails.Denter > 0){
                        self.sequenceForToday.Denter.push({'id':self.allBookingsWithEOD[j].booking_id, 'hrs':workDetails.Denter});
                    }
                    if(workDetails.PainterHelper > 0){
                        self.sequenceForToday.PainterHelper.push({'id':self.allBookingsWithEOD[j].booking_id, 'hrs':workDetails.PainterHelper});
                    }
                    if(workDetails.Paintbooth > 0){
                        self.sequenceForToday.Paintbooth.push({'id':self.allBookingsWithEOD[j].booking_id, 'hrs':workDetails.Paintbooth});
                    }
                    if(workDetails.Polisher > 0){
                        self.sequenceForToday.Polisher.push({'id':self.allBookingsWithEOD[j].booking_id, 'hrs':workDetails.Polisher});
                    }
                    if(workDetails.WashingBay > 0){
                        self.sequenceForToday.WashingBay.push({'id':self.allBookingsWithEOD[j].booking_id, 'hrs':workDetails.WashingBay});
                    }
                    if(workDetails.Painter > 0){
                        self.sequenceForToday.Painter.push({'id':self.allBookingsWithEOD[j].booking_id, 'hrs':workDetails.Painter});
                    }
                    if(workDetails.Batman > 0){
                        self.sequenceForToday.Batman.push({'id':self.allBookingsWithEOD[j].booking_id, 'hrs':workDetails.Batman});
                    }
                }

                if(self.allBookingsWithEOD[j].work_to_done_in_day_datewise[processingDate]){
                    taskListForDate = self.allBookingsWithEOD[j].work_to_done_in_day_datewise[processingDate].tasks_done_for_date;
                    for(var x=0; x<taskListForDate.length; x++){
                        var task_group = '';
                        if(taskListForDate[x].seq_num <= 315){
                            task_group = "1_Till_BF_Sanding";
                        }else if(taskListForDate[x].seq_num <= 317){
                            task_group = "2_Till_Putty_Sanding";
                        }else if(taskListForDate[x].seq_num <= 320){
                            task_group = "3_Till_Primer_Sanding";
                        }else if(taskListForDate[x].seq_num <= 322){
                            task_group = "4_Till_Painting_process_done";
                        }else if(taskListForDate[x].seq_num === 323){
                            task_group = "5_Till_Paint_drying";
                        }else if(taskListForDate[x].seq_num <= 328){
                            task_group = "6_Till_Polishing_washing";
                        }
                        if(self.workSequenceForToday[task_group]){
                            self.workSequenceForToday[task_group].push({"id":self.allBookingsWithEOD[j].booking_id, "hrs":taskListForDate[x].time, "task":taskListForDate[x].seq});
                        }else{
                            self.workSequenceForToday[task_group] = [{"id":self.allBookingsWithEOD[j].booking_id, "hrs":taskListForDate[x].time, "task":taskListForDate[x].seq}];
                        }
                        /*if(self.workSequenceForToday[taskListForDate[x].seq_num + taskListForDate[x].seq]){
                            self.workSequenceForToday[taskListForDate[x].seq_num + taskListForDate[x].seq].push({"id":self.allBookingsWithEOD[j].booking_id, "hrs":taskListForDate[x].time});
                        }else{
                            self.workSequenceForToday[taskListForDate[x].seq_num + taskListForDate[x].seq] = [{"id":self.allBookingsWithEOD[j].booking_id, "hrs":taskListForDate[x].time}];
                        }*/
                    }

                }
            }
            Object.keys(self.workSequenceForToday).sort().forEach(function(key) {
              self.workSequenceForTodayOrdered[key] = self.workSequenceForToday[key];
            });
        });
    }

    self.generateSchedule = generateSchedule;
});