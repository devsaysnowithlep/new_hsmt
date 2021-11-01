from django.urls import path
from . import views

# # just for debug
# from django.conf import settings
# from django.conf.urls.static import static
#--------------------------#

urlpatterns = [
    path('api/xfile/', views.XFileListCreate.as_view(),  name='xfile_LC'),
    path('api/xfile/<int:pk>/', views.XFileRetrieveUpdateDestroy.as_view(),  name='xfile_RUD'),
    path('api/xfile/<int:pk>/content/', views.XFileContentList.as_view(),  name='xfile_content_L'),
    path('api/xfile/<int:pk>/content/<int:content_pk>/detail/', views.XFileDetailListCreate.as_view(),  name='xfile_detail_LC'),
    path('api/xfile/<int:pk>/content/<int:content_pk>/detail/<int:detail_pk>/', views.XFileDetailRetrieveUpdateDestroy.as_view(),  name='xfile_detail_RUD'),

    path('api/xfiletype/', views.XFileTypeListCreate.as_view(),  name='xfiletype_LC'),
    path('api/xfiletype/<int:pk>/', views.XFileTypeRetrieveUpdateDestroy.as_view(),  name='xfiletype_RUD'),
]

# if settings.DEBUG :
#     urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)