from mytrip.views import *
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.conf.urls.static import static

urlpatterns = [
	url(r'^home/$', home),								# homepage
	url(r'^login/$', login),							# login page
	url(r'^auth/$', auth_view),							# login authentication
	url(r'^signup/$', signup),							# signup page
	url(r'^create/$', create),							# signup verification
	url(r'^logout/$', logout),							# logout
	url(r'^myevent/$', myevent),						# new event creation form
	url(r'^newevent/$', newevent),						# new event creation part1
	url(r'^neweventfinal/$', neweventfinal),			# new event creation part2
	url(r'^profile/$', profile),						# profile page
	url(r'^edit/$', edit),								# edit profile page
	url(r'^editfinal/$', editfinal),					# edit final profile page
	url(r'^register/(?P<ename>.+?)/$', register),		# event registration form
	url(r'^registerfinal/$', registerfinal),			# event registration
	url(r'^event/(?P<ename>.+?)/$', event),				# event description page
	url(r'^download/(?P<ename>.+?)/$', download),		# download registration details
	url(r'^editevent/(?P<ename>.+?)/$', editevent),		# edit event page
	url(r'^editeventfinal/$', editeventfinal),			# edit final event page
	url(r'^deleteevent/(?P<ename>.+?)/$', deleteevent),	# delete event page
	url(r'^checkUser/$', checkUser),					# check username if already exist
	url(r'^checkEmail/$', checkEmail),					# check email if already exist
	url(r'^checkMobile/$', checkMobile),				# check mobile if already exist
	url(r'^checkEvent/$', checkEvent),					# check event if already exist
]

# if settings.DEBUG:
# 	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)