from django.urls import path
from . import views

# # just for debug
# from django.conf import settings
# from django.conf.urls.static import static
#--------------------------#

urlpatterns = [
    path('api/xfile/', views.XFileListCreate.as_view(), name='xfile_LC'),
    path('api/xfile/<int:pk>/', views.XFileRetrieveUpdateDestroy.as_view(), name='xfile_RUD'),
    path('api/xfile/<int:pk>/content/', views.XFileContentList.as_view(), name='xfile_content_L'),
    path('api/xfile/<int:pk>/content/<int:content_pk>/detail/', views.XFileDetailListCreate.as_view(), name='xfile_detail_LC'),
    path('api/xfile/<int:pk>/content/<int:content_pk>/detail/<int:detail_pk>/', views.XFileDetailRetrieveUpdateDestroy.as_view(), name='xfile_detail_RUD'),
    path('api/xfile/<int:pk>/attacklog/', views.XFileAttackLogListCreate.as_view(), name='xfile_attacklog_LC'),
    path('api/xfile/<int:pk>/attacklog/<int:attacklog_pk>/', views.XFileAttackRetrieveUpdateDestroy.as_view(), name='xfile_attacklog_RUD'),
    path('api/xfile/<int:pk>/xfilelog/', views.XFileLogListCreate.as_view(), name='xfile_xfilelog_LC'),
    path('api/xfile/<int:pk>/xfilelog/<int:xfilelog_pk>/', views.XFileAttackRetrieveUpdateDestroy.as_view(), name='xfile_xfilelog_RUD'),

    path('api/xfiletype/', views.XFileTypeListCreate.as_view(), name='xfiletype_LC'),
    path('api/xfiletype/<int:pk>/', views.XFileTypeRetrieveUpdateDestroy.as_view(), name='xfiletype_RUD'),

    path('api/target/', views.TargetListCreate.as_view(), name='target_LC'),
    path('api/target/<int:pk>/', views.TargetRetrieveUpdateDestroy.as_view(), name='target_RUD'),

    path('api/xfile/<int:pk>/perm/', views.XFilePermView.as_view(), name='xfile_perm'),
    path('api/xfile/<int:pk>/submit/', views.XFileSubmitView.as_view(), name='xfile_submit'),
    path('api/xfile/<int:pk>/reject/', views.XFileRejectView.as_view(), name='xfile_reject'),
    path('api/xfile/<int:pk>/approve/', views.XFileApproveView.as_view(), name='xfile_approve'),
    path('api/xfile/<int:pk>/rejectdone/', views.XFileCreateChangeView.as_view(), name='xfile_rejectdone'),

    path('api/test/<int:pk>/', views.test, name='test')
]

# if settings.DEBUG :
#     urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)