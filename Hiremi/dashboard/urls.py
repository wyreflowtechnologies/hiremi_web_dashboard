from django.urls import path
from.views import *

urlpatterns = [
    path('',index,name="index"),
    path('superuser_login/',superuser_login,name="superuser_login"),
    path('superuser_logout/',superuser_logout,name="superuser_logout"),
    path('otp_page/',otp_page,name="otp_page"),
    path('otp_verify/',otp_verify,name="otp_verify"),
    path('resend_otp/',resend_otp,name="resend_otp"),

    path('dashboard/',dashboard,name="dashboard"),
    path('interested-domain/',interested_domain,name="interested-domain"),
    path('branch/',branch,name="branch"),
    path('college-state/',college_state,name="college-state"),
    path('degree/',degree,name="degree"),
    path('passing-year/',passing_year,name="passing-year"),
    path('birth-place/',birth_place,name="birth-place"),

    path('verified-female/',verified_female,name="verified-female"),
    path('verified-male/',verified_male,name="verified-male"),
    path('non-verified-male/',non_verified_male,name="non-verified-male"),
    path('non-verified-female/',non_verified_female,name="non-verified-female"),


    path('app_downloads/',app_downloads,name="app_downloads"),
    path('not_verified/',not_verified,name="not_verified"),
    path('verified/',verified,name="verified"),
    path('total_user/',total_user,name="total_user"),
    path('experienced/',experienced,name="experienced"),
    path('internship/',internship,name="internship"),
    path('fresher_Job/',fresher_Job,name="fresher_Job"),


    path('view_user/<int:pk>/',view_user,name="view_user"),
    path('delete_user/<int:pk>/',delete_user,name="delete_user"),

    path('Query/',Query,name="Query"),
    path('Query_view/<int:pk>/',Query_view,name="Query_view"),


    path('internship_from/',internship_from,name="internship_from"),
    path('fresher_from/',fresher_from,name="fresher_from"),
    path('experienced_from/',experienced_from,name="experienced_from"),

    path('create_internship_job/',create_internship_job,name="create_internship_job"),

    
    
]
