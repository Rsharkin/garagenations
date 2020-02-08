# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0255_auto_20170607_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookinginvoice',
            name='cgst',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookinginvoice',
            name='igst',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookinginvoice',
            name='sgst',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='city',
            name='cgst',
            field=models.DecimalField(default=9, help_text=b'CGST - Center GST in percentage', max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='city',
            name='gstin',
            field=models.CharField(default='29AABCU6599C2ZW', help_text=b'GST Number for this state', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='city',
            name='igst',
            field=models.DecimalField(default=18, help_text=b'IGST - Inter state GST in percentage', max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='city',
            name='invoice_address',
            field=models.TextField(help_text=b'This will be the address on invoice', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='city',
            name='sgst',
            field=models.DecimalField(default=9, help_text=b'SGST - State GST in percentage', max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='city',
            name='state_code',
            field=models.CharField(default=29, help_text=b'This is for GST', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='city',
            name='state_name',
            field=models.CharField(default='Karnataka', help_text=b'This is for GST', max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='checklistitem',
            name='item_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Boolean'), (2, b'Image'), (3, b'Number')]),
        ),
        migrations.AlterField(
            model_name='messages',
            name='action',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (58, 58), (59, 59), (60, 60), (101, 101), (102, 102), (103, 103), (104, 104), (105, 105), (106, 106), (107, 107), (108, 108), (109, 109), (111, 111), (112, 112), (113, 113), (114, 114), (115, 115), (116, 116), (117, 117), (118, 118), (119, 119), (120, 120), (121, 121), (122, 122), (123, 123), (124, 124), (125, 125), (126, 126), (127, 127), (128, 128), (129, 129), (130, 130), (131, 131), (132, 132), (133, 133), (134, 134), (135, 135), (136, 136), (137, 137), (138, 138), (139, 139), (140, 140), (141, 141), (142, 142), (143, 143), (144, 144), (145, 145), (146, 146), (147, 147), (148, 148), (151, 151), (152, 152), (153, 153), (154, 154), (216, 216)]),
        ),
    ]
