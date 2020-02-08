# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def remove_carversions(apps, schema_editor):
    """
    For all booking sources, create a source.
    """
    CarModelVariant = apps.get_model('core','CarModelVariant')
    CarModelVariant.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0210_auto_20170214_1556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carmodelvariant',
            name='car_model',
            field=models.ForeignKey(related_name='carvariant', to='core.CarModel'),
        ),
        migrations.RunPython(remove_carversions, reverse_code=migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='carmodelvariant',
            unique_together=set([('car_model', 'name')]),
        ),
    ]
