from django.db import migrations

def seed_ozkey(apps, schema_editor):
    OzKey = apps.get_model('users', 'OzKey')
    from backend.apps.users.services import hash_key

    PLAIN_KEY = "OZ-TEST-KEY-2025-COHORT11"
    COHORT = "11"
    COURSE = "BE" # 또는 FE

    h = hash_key(PLAIN_KEY)
    OzKey.objects.create(
        key_hash=h,
        is_active=True,
        tag_number=COHORT,
        tag_classes=COURSE
    )

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_rename_tag_class_ozkey_tag_classes'),
    ]
    operations = [
        migrations.RunPython(seed_ozkey, migrations.RunPython.noop),
    ]
