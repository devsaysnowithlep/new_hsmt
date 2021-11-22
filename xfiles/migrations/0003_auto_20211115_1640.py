# Generated by Django 3.2.8 on 2021-11-15 13:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('xfiles', '0002_alter_xfile_editors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attacklog',
            name='timestamp',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='xfile',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='xfilelog',
            name='action',
            field=models.PositiveIntegerField(choices=[(0, 'tạo mới'), (1, 'sửa đổi'), (2, 'gửi phê duyệt'), (3, 'phê duyệt'), (4, 'yêu cầu sửa lại'), (5, 'hủy bỏ trạng thái hoàn thiện để tiếp tục sửa đổi')], default=1),
        ),
        migrations.AlterField(
            model_name='xfilelog',
            name='performer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='xfile_logs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='xfilelog',
            name='xfile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='xfile_logs', to='xfiles.xfile'),
        ),
    ]