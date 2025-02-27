from django.urls import path, include
from complaints import views
from django.contrib import admin

urlpatterns = [
    path('', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-complaint/', views.add_complaint, name='add_complaint'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('logout/', views.user_logout, name='logout'),
    path('admin/', admin.site.urls),
    path('update-status/<int:complaint_id>/', views.update_status, name='update_status'),
    path('complaint/<int:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    path('complaints/', include('complaints.urls')),  # Changed '' to 'complaints/' to avoid conflict
]
