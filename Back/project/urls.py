# project/urls.py 

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    DepositProductViewSet,
    SavingsProductViewSet,
    StockBoardViewSet,
    CommentViewSet,
    ImageUploadViewSet,
    RealAssetViewSet,
    InterestViewSet,
)
from dj_rest_auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static

# Router
router = DefaultRouter()
router.register(r'deposits', DepositProductViewSet, basename='depositproduct')
router.register(r'savings', SavingsProductViewSet, basename='savingsproduct')
router.register(r'posts', StockBoardViewSet, basename='posts')
router.register(r'comments', CommentViewSet, basename='comments')
router.register(r'images', ImageUploadViewSet, basename='images')
router.register(r'real-assets', RealAssetViewSet, basename='real-assets')
router.register(r'interests', InterestViewSet, basename='interests')

# URL Patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/core/router/', include(router.urls)),  # Router URL
    path('api/core/actions/', include('core.urls')),  # Core 앱의 URL 포함
    path('api/auth/', include('dj_rest_auth.urls')),  # 로그인/로그아웃
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),  # 회원가입
    path('api/auth/token/', LoginView.as_view(), name='token-login'),
]

# Static and Media 파일 설정
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
