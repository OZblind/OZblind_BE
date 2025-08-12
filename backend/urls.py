from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/', include('backend.apps.users.urls')),
    path('boards/', include('backend.apps.boards.urls')),
    path('posts/', include('backend.apps.posts.urls')),
    path('api/comments/', include('backend.apps.comments.urls')),
    path('api/reactions/', include('backend.apps.reactions.urls')),
    path('api/bookmarks/', include('backend.apps.bookmarks.urls')),
    path('api/ntf/', include('backend.apps.notifications.urls')),
    path('tags/', include('backend.apps.tags.urls')),
]
