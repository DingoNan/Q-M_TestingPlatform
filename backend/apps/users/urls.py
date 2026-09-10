from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import (
    LoginView,
    MyTokenRefreshView,
    PermissionView,
    RoleViewSet,
    RolePermissionViewSet,
    UserViewSet,
    UserRegister,
    modify_pwd,
    GroupViewSet,
    NavigationViewSet,
    get_usernames,
    get_online_users_count,
    logout_user,
)


router = DefaultRouter()
router.register('permission', PermissionView)
router.register('role', RoleViewSet)
router.register('role_permission', RolePermissionViewSet)
router.register('users', UserViewSet)
router.register('group', GroupViewSet)
router.register('navigation', NavigationViewSet)
router.register('register', UserRegister, basename='user_register')

urlpatterns = [
    path('user/login/', LoginView.as_view(), name='login'),
    path('user/usernames/', get_usernames, name='usernames'),
    path('user/modify_pwd/', modify_pwd, name='modify_pwd'),
    path('user/online_count/', get_online_users_count, name='online_users_count'),
    path('user/logout/', logout_user, name='logout'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('user/', include(router.urls), name='user')
]
