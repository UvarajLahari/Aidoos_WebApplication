from django.conf.urls import url,include
#from django.urls import include,path
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^dashboard/',include('dashboard.urls',namespace='dashboard')),
]
