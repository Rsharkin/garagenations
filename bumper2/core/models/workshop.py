from django.conf import settings
from core.models.master import Workshop
from django.db import models
from core.models.common import CreatedAtAbstractBase
from core.models.master import BookingOpsStatus
import logging
logger = logging.getLogger('__name__')


class WorkshopResources(CreatedAtAbstractBase):
    TYPE_OF_RECORD_DAILY = 1
    TYPE_OF_RECORD_EXPECTED = 2

    TYPE_OF_RECORDS = (
        (TYPE_OF_RECORD_DAILY, 'Daily'),
        (TYPE_OF_RECORD_EXPECTED, 'Expected'),
    )

    workshop = models.ForeignKey(Workshop, related_name='workshopresource')
    on_date = models.DateField()
    denters = models.IntegerField()
    painters = models.IntegerField()
    painter_helpers = models.IntegerField()
    paint_booth = models.IntegerField(default=1, null=True, blank=True)
    washing_bay = models.IntegerField(default=1, null=True, blank=True)
    polishers = models.IntegerField(default=1)
    type_of_record = models.IntegerField(default=TYPE_OF_RECORD_DAILY, choices=TYPE_OF_RECORDS)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, help_text="Person who punched this entry")

    def __unicode__(self):
        return "%s: D:%s, P:%s, PH:%s" % (self.on_date, self.denters, self.painters, self.painter_helpers)


class WorkshopStepsOfWork(CreatedAtAbstractBase):
    """
        Table to hold steps of works for type of damage per panel.
    """
    TYPE_OF_DAMAGE_D1 = 'D1'
    TYPE_OF_DAMAGE_D2 = 'D2'
    TYPE_OF_DAMAGE_D3 = 'D3'
    TYPE_OF_DAMAGE_S = 'S'
    TYPE_OF_DAMAGE_R1 = 'R1'
    TYPE_OF_DAMAGE_R2 = 'R2'
    TYPE_OF_DAMAGE_R3 = 'R3'

    TYPE_OF_DAMAGES = (
        (TYPE_OF_DAMAGE_D1, TYPE_OF_DAMAGE_D1),
        (TYPE_OF_DAMAGE_D2, TYPE_OF_DAMAGE_D2),
        (TYPE_OF_DAMAGE_D3, TYPE_OF_DAMAGE_D3),
        (TYPE_OF_DAMAGE_S, TYPE_OF_DAMAGE_S),
        (TYPE_OF_DAMAGE_R1, TYPE_OF_DAMAGE_R1),
        (TYPE_OF_DAMAGE_R2, TYPE_OF_DAMAGE_R2),
        (TYPE_OF_DAMAGE_R3, TYPE_OF_DAMAGE_R3),
    )
    type_of_damage = models.CharField(max_length=3, choices=TYPE_OF_DAMAGES)
    ops_status = models.ForeignKey(BookingOpsStatus)
    resources_used = models.CharField(max_length=64, help_text="user | For optional resource and & for required "
                                                               "Together resource")
    processing_time_car_level = models.IntegerField(default=0, help_text="In minutes")
    processing_time_panel_level = models.IntegerField(default=0, help_text="In minutes")

    def __unicode__(self):
        return "%s - %s" % (self.type_of_damage, self.ops_status.ops_status_desc)


class WorkshopSla(CreatedAtAbstractBase):
    """
        Table to hold master data for SLA based on number of panels of diff types.
    """
    name = models.CharField(max_length=12)
    filter_conditions = models.CharField(max_length=1024, null=True, blank=True,
                                         help_text="Static Django Query Conditions for filtering based on number of "
                                                   "panels of diff type.")

    def __unicode__(self):
        return self.name


class WorkshopExecutionSteps(CreatedAtAbstractBase):
    """
        Steps for individual days.
    """
    sla = models.ForeignKey(WorkshopSla)
    days_in_workshop = models.IntegerField(help_text="Num of working days in workshop, excluding sunday")
    ops_status = models.ForeignKey(BookingOpsStatus, related_name="opsstatustodo")
    ops_status_to_consider = models.ForeignKey(BookingOpsStatus, related_name="opsstatustoconsider", null=True, blank=True)
    portion = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    def __unicode__(self):
        return "%s - %s - %s" % (self.sla.name, self.days_in_workshop, self.ops_status.ops_status_desc)
