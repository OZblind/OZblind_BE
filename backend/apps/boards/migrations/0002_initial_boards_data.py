from django.db import migrations

INITIAL_BOARDS = [
    {"name": "자유게시판", "description": "자유롭게 소통하는 공간입니다."},
    {"name": "정보게시판", "description": "유용한 정보를 공유하는 공간입니다."},
    {"name": "취업게시판", "description": "취업 및 채용 정보를 나누는 공간입니다."},
    {"name": "설문게시판", "description": "다양한 주제로 설문을 진행하는 공간입니다."},
    {"name": "깃헙게시판", "description": "프로젝트나 스터디를 위한 깃허브 정보를 공유하는 공간입니다."},
]

def create_initial_boards(apps, schema_editor):
    Board = apps.get_model('boards', 'Board')

    for board_data in INITIAL_BOARDS:
        Board.objects.get_or_create(
            name=board_data['name'],
            defaults={'description': board_data['description']}
        )


def delete_initial_boards(apps, schema_editor):
    Board = apps.get_model('boards', 'Board')
    board_names = [board['name'] for board in INITIAL_BOARDS]
    Board.objects.filter(name__in=board_names).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('boards', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_boards, delete_initial_boards),
    ]