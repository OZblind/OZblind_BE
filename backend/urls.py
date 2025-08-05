
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
    path('users/', include('users.urls')),
    path('boards/', include('boards.urls')),
    path('posts/', include('posts.urls')),
    path('comments/', include('comments.urls')),
    path('reactions/', include('reactions.urls')),
    path('bookmarks/', include('bookmarks.urls')),
    path('notifications/', include('notifications.urls')),
    path('tags/', include('tags.urls')),

]
