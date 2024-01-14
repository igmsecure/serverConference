from django.urls import path
from account import views
from account import authViews



app_name = "account"

urlpatterns = [
    #---------------------------<views>----------------------------- 
    # path('auth/login', views.loginView),
    # path('auth/register', views.registerView),
    # path('auth/check', views.checkView),
    # path('auth/logout', views.logoutView),

    #-------------------------<authViews>--------------------------- 
    path("auth/register/", authViews.RegisterView.as_view(), name="register"), #POST
    path("auth/login/", authViews.LoginView.as_view(), name="login"), #POST
    path("auth/refresh/", authViews.RefresfTokenView.as_view(), name="refresh_token"), #GET
    path("auth/check/", authViews.CheckLoginStatus.as_view(), name="check_access_token"),  #GET
    path("auth/logout/", authViews.Logout.as_view(), name="logout"), #GET
]