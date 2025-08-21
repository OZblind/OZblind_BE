# import django_filters
# from .models import Post
#
# class PostFilter(django_filters.FilterSet):
#     # Post 모델에 대한 커스텀 필터셋
#     # 1. 필드네임 user__tag_number : 필터가 Post 모델의 'user'를 따라가서 해당 유저의 'tag_number' 필드를 필터링 하도록 지정
#     user_tag_number = django_filters.NumberFilter(field_name='user__tag_number')
#     user_tag_name = django_filters.CharFilter(field_name='user__tag_class')
#
#     class Meta:
#         model = Post
#         fields = ['board', 'user_tag_number', 'user_tag_class']