from django.conf.urls import url
from .views import *

urlpatterns=[
	url(r'^Generate_Accounting/$',Generate_Accounting,name="Generate_Accounting"),
	url(r'^Generate_Excel/$',Generate_Excel,name="Generate_Excel"),
]