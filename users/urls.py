from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('api/department/', views.DepartmentListCreate.as_view(), name='department_LC'),
    path('api/position/', views.PositionListCreate.as_view(), name='position_LC'),

    path('api/user/', views.UserListCreate.as_view(), name='user_LC'),
    path('api/user/me/', views.UserMeView.as_view(), name='user_me'),
    path('api/user/change-pwd/', views.UserChangePwd.as_view(), name='user_pwd'),
    path('api/user/update/', views.UserUpdate.as_view(), name='user_U'),
    path('api/user/<int:pk>/', views.UserRetrieve.as_view(), name='user_R'),
    path('api/user/<int:pk>/manage/', views.UserManager.as_view(), name='user_M'),

    path('api/login/', TokenObtainPairView.as_view(), name='user_login'),
    path('api/login/refresh/', TokenRefreshView.as_view(), name='user_refresh'),
    path('api/department/change-pwd/', views.DepartmentChangePwd.as_view(), name='department_change_pwd'),
    path('api/department/login/', views.DepartmentLogin.as_view(), name='department_login'),
]
