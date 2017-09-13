from web import views
from django.conf.urls import url

urlpatterns = [
url(r'^submit/expense/$',views.submit_expense, name='submit_expense'),
url(r'^submit/income/$',views.submit_income, name='submit_income'),

url(r'^accounts/register/$', views.register, name='register'),
url(r'^$', views.index, name='index'),

url(r'^q/generalstat/$', views.generalstat, name='generalstat'),
]
