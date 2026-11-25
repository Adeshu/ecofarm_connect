# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE courses_lesson ADD COLUMN video_file VARCHAR(100) NULL AFTER video_url;",
            reverse_sql="ALTER TABLE courses_lesson DROP COLUMN video_file;",
        ),
    ]

