from django.db import migrations

def seed_ozkey_fe(apps, schema_editor):
    OzKey = apps.get_model('users', 'OzKey')
    from backend.apps.users.services import hash_key

    PLAIN_KEY = "OZ-TEST-KEY-2025-COHORT12-FE"  # FE 전용 키
    COHORT = "12"
    COURSE = "FE"

    h = hash_key(PLAIN_KEY)
    OzKey.objects.create(
        key_hash=h,
        is_active=True,
        tag_number=COHORT,
        tag_class=COURSE
    )

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_userozkeymap_unique_together'),
    ]

    operations = [
        migrations.RunPython(seed_ozkey_fe, migrations.RunPython.noop),
    ]
