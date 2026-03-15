from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hostel", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="hostel",
            name="cover_photo",
            field=models.FileField(blank=True, null=True, upload_to="hostels/"),
        ),
        migrations.AddField(
            model_name="hostel",
            name="selection_badge",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
        migrations.AddField(
            model_name="hostel",
            name="subtitle",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="hostel",
            name="warden_photo",
            field=models.FileField(blank=True, null=True, upload_to="wardens/"),
        ),
    ]
