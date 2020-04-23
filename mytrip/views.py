from django.shortcuts import render 						# for page rendering and providing context
from django.views.generic import TemplateView				# to use generic view
from django.http import HttpResponseRedirect,HttpResponse 	# to give response
from django.contrib import auth 							# for authentication
from django.template.context_processors import csrf			# cross site forgery token
from django.contrib.auth import get_user_model				# to get user model
from mytrip.models import *									# for using models
from django.db import connection							# for executing complex query
from django.contrib.auth.decorators import login_required	# for login required
from django.core.mail import EmailMultiAlternatives			# for sending email
import csv													# for csv format support
import datetime												# for datetime object
from django.conf import settings
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from django.http import JsonResponse

# Create your views here.

# to get user model
User = get_user_model()

# homepage of the application
def home(request):
	username=request.session.get('username','')
	lat = request.GET.get('lat')
	lng = request.GET.get('lng')
	dist = request.GET.get('distance')
	# order = request.GET.get('order')
	preloclat = 22.667213
	preloclng = 72.890434
	predist = 50
	# preorder = 0
	# global preloclat, preloclng, predist
	print(lat)
	print(lng)
	print(dist)
	# cursor is for executing complex query
	cursor = connection.cursor()

	if lat:
		request.session['mylat']=lat
		request.session['mylng']=lng
		request.session['mydist']=dist
		# request.session['myorder']=order
        
	else:
		l = request.session.get('mylat','')
		if l == '':
			request.session['mylat']=preloclat
			request.session['mylng']=preloclng
			request.session['mydist']=predist
			# request.session['myorder']=preorder
			# print(myevent[0][1])
		
	mylat = request.session.get('mylat','')
	mylng = request.session.get('mylng','')
	mydist = request.session.get('mydist','')
	# myorder = request.session.get('myorder','')

	# for dropdown list to be selected
	indexDist=0
	if mydist == '5':
		indexDist = 0
	elif mydist == '10':
		indexDist = 1
	elif mydist == '25':
		indexDist = 2
	elif mydist == '50':
		indexDist = 3
	elif mydist == '100':
		indexDist = 4

	# indexOrder=0
	# if myorder == '0':
	# 	indexOrder = 0
	# elif myorder == '1':
	# 	indexOrder = 1

	print(mylat)
	print(mylng)
	print(mydist)
	# Haversine formula - used generally for computing great-circle distances between two pairs of coordinates on a sphere
	# sql query for getting nearby events
	# 6371 is used to search by kilometers
	# replace 6371 with 3959 to search by miles
	# distance is in kilometers
	# if indexOrder == 0:
	cursor.execute('SELECT *, ( 6371 * acos( cos( radians(%s) ) * cos( radians( lat ) ) * cos( radians( lng ) - radians(%s) ) + sin( radians(%s) ) * sin( radians( lat ) ) ) ) AS distance FROM mytrip_events HAVING distance < %s ORDER BY distance',[mylat,mylng,mylat,mydist])
	# elif indexOrder == 1:
	# 	cursor.execute('SELECT *, ( 6371 * acos( cos( radians(%s) ) * cos( radians( lat ) ) * cos( radians( lng ) - radians(%s) ) + sin( radians(%s) ) * sin( radians( lat ) ) ) ) AS distance FROM mytrip_events HAVING distance < %s ORDER BY distance DESC',[mylat,mylng,mylat,mydist])
	myevent = cursor.fetchall()
	print(myevent)
	myevent_list = list(myevent)
	# print(myevent_list)
	current = datetime.datetime.now()
	# print(current)

	for p in myevent_list:
		# print(p[10])
		p = list(p)
		if current > p[10]:
			p = tuple(p)
			# print(myevent_list.index(p))
			myevent_list[myevent_list.index(p)] = None

	myevent = tuple(myevent_list)
	print(myevent)	
	if username != '':
		return render(request,"home.html",{'usernm':username, 'events':myevent, 'indexDist':indexDist})
	else:
		return render(request,'home.html',{'events':myevent, 'indexDist':indexDist})

# loginform rendering
def login(request):
	# ce = {}
	# ce.update(csrf(request))
	return render(request,"login.html")

# signupform rendering
def signup(request):
	return render(request,"signup.html")

# check username if already exist
def checkUser(request):
	row = 0
	usr = request.GET.get('username','')
	for p in User.objects.raw('SELECT * FROM mytrip_users where username = %s',[usr]):
		row = row + 1
	if row != 0:
		return JsonResponse("failure",safe=False)
	return JsonResponse("success",safe=False)

# check email if already exist
def checkEmail(request):
	row = 0
	emailid = request.GET.get('myemail','')
	for p in User.objects.raw('SELECT * FROM mytrip_users where email = %s',[emailid]):
		row = row + 1
	if row != 0:
		return JsonResponse("failure",safe=False)
	return JsonResponse("success",safe=False)

# check mobile if already exist
def checkMobile(request):
	row = 0
	mobile = request.GET.get('mymobile','')
	for p in User.objects.raw('SELECT * FROM mytrip_users where mobileno = %s',[mobile]):
		row = row + 1
	if row != 0:
		return JsonResponse("failure",safe=False)
	return JsonResponse("success",safe=False)

# authenticating user in login
def auth_view(request):
	username = request.POST.get('username')
	password = request.POST.get('password','')
	nexturl = request.POST.get('next','')
	user = auth.authenticate(username=username, password=password)
	if user is not None:
		request.session['username']=username
		auth.login(request,user)
		if nexturl == '':
			return HttpResponseRedirect('/mytrip/home')
		else:
			return HttpResponseRedirect(nexturl)
		# return HttpResponseRedirect('/mytrip/home')
	else:
		# return HttpResponseRedirect('/mytrip/login',{'wrong':'username or password is incorrect'})
		return render(request,'login.html',context={'wrong':'username or password is incorrect'})

# creating new user in signup
def create(request):
	row = 0

	# fetching form data
	uname = request.POST.get('username', '')
	emailid = request.POST.get('email', '')
	fname = request.POST.get('firstname', '')
	lname = request.POST.get('lastname', '')
	mobile = request.POST.get('phone', '')
	pword = request.POST.get('password', '')
	pword1 = request.POST.get('password1', '')

	# checking for duplicate entries in the table
	# for username
	# for p in User.objects.raw('SELECT * FROM mytrip_users where username = %s',[uname]):
	# 	row = row + 1
	# if row != 0:
	# 	return render(request,'signup.html',context={'exists':'username exists'})

	# # for email
	# for p in User.objects.raw('SELECT * FROM mytrip_users where email = %s',[emailid]):
	# 	row = row + 1
	# if row != 0:
	# 	return render(request,'signup.html',context={'email':'email exists'})

	# # for mobile no
	# for p in User.objects.raw('SELECT * FROM mytrip_users where mobileno = %s',[mobile]):
	# 	row = row + 1
	# if row != 0:
	# 	return render(request,'signup.html',context={'mobile':'mobileno exists'})

	#creating user if both passwords are same
	if pword == pword1:
		user = User.objects.create_user(uname, emailid, pword, first_name=fname, last_name=lname, mobileno=mobile)
	else:
		return render(request,'signup.html',context={'error':'both password must be same'})

	# saving user
	request.session['username']=uname
	if user is not None:
			user.save();

			subject, from_email, to = 'Confirm Email', 'YOUR_EMAIL',emailid
			text_content = 'This is an important message.'
			html_content = '<p>Welcome to <b>TripManager</b><br><b>#ExploreNearby</b></p>'
			msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
			msg.attach_alternative(html_content, "text/html")
			try:
				msg.send()
			except:
				print('There was an error sending an email: ')
				return HttpResponse("ERROR")

			auth.login(request,user)
			return HttpResponseRedirect('/mytrip/home/')
	else:
		print("enter correct details")
		return HttpResponseRedirect('/mytrip/signup/')

# event description page
@login_required(login_url="/mytrip/login")
def event(request,ename):
	row=0
	x=0
	username=request.session.get('username','')
	event = events.objects.raw('SELECT * FROM mytrip_events WHERE name = %s',[ename])[0]
	usr = User.objects.raw('SELECT * FROM mytrip_users WHERE username = %s',[username])[0]
	
	# checking if user has registered for the event or not
	for r in event_registration.objects.raw("SELECT * FROM mytrip_event_registration WHERE evnt_id = %s AND usr_id = %s",[event.pk,usr.pk]):
		row = row + 1

	# checking available seats in the event
	for r in event_registration.objects.raw("SELECT * FROM mytrip_event_registration WHERE evnt_id = %s",[event.pk]):
		x = x + 1
	avail = event.capacity - x

	reguser = event_registration.objects.raw("SELECT * FROM mytrip_event_registration WHERE evnt_id = %s",[event.pk])
	registered = event.capacity - avail
	# user has already registered for the event
	if row != 0:
		reg = True
	# user has not registered for the event
	else:
		reg = False

	if usr.pk == event.org_id:
		return render(request,"event-org.html",{'usernm':username, 'event':event, 'avail':avail, 'reguser':reguser, 'registered':registered})
	elif username != '':
		return render(request,"event.html",{'usernm':username, 'event':event, 'usr':usr, 'reg':reg, 'avail':avail})
	else:
		return render(request,'home.html')

# check event if already exist
def checkEvent(request):
	row = 0
	eventnm = request.GET.get('eventname','')
	for p in events.objects.raw('SELECT * FROM mytrip_events where name = %s', [eventnm]):
		row = row + 1
	if row != 0:
		return JsonResponse("failure",safe=False)
	return JsonResponse("success",safe=False)

# new event creation form rendering
@login_required(login_url="/mytrip/login")
def myevent(request):
	username=request.session.get('username','')
	
	if username != '':
		# object for organizer
		# org = User.objects.raw('SELECT * FROM mytrip_users WHERE username = %s',[username])[0]

		# fetching event types from the table
		types = event_types.objects.raw('SELECT * FROM mytrip_event_types ORDER BY etype')
		return render(request,"myevent.html",{'usernm':username, 'types':types})
	else:
		return render(request,'home.html')

# new event creation - part1
@login_required(login_url="/mytrip/login")
def newevent(request):
	uname=request.session.get('username','')
	row = 0

	# fetching form data
	name = request.POST.get('name', '')
	orgname = request.POST.get('orgname', '')
	capacity = request.POST.get('capacity', '')
	price = request.POST.get('price', '')
	event_type = request.POST.get('event_type', '')
	new_type = request.POST.get('newtype', '')
	contact = request.POST.get('contact', '')
	event_date = request.POST.get('event_date','')
	ephoto = request.FILES.get('photo')

	# new_event_date = parse_datetime(event_date)
	# new_event_date1 = make_aware(new_event_date)
	# print("photo details")
	# print(ephoto)

	# checking if event already exists
	for p in events.objects.raw('SELECT * FROM mytrip_events where name = %s', [name]):
		row = row + 1
	if row != 0:
		return render(request,'myevent.html',context={'error':'event exists','usernm':uname})

	# event organizer
	person = User.objects.raw("SELECT * FROM mytrip_users WHERE username = %s", [uname])[0]

	# creating and saving event object
	if new_type != '':
		etype = event_types(etype=new_type)
		etype.save()
		event = events(name=name, event_type=new_type, capacity=capacity, contact=contact, orgname=orgname, price=price, event_date=event_date, org_id=person.pk, photo=ephoto)
	else:
		event = events(name=name, event_type=event_type, capacity=capacity, contact=contact, orgname=orgname, price=price, event_date=event_date, org_id=person.pk, photo=ephoto)
	
	event.save()
	request.session['ename']=name

	return render(request,'myevent2.html',{'ename':name,'usernm':uname})

# new event creation - part2
@login_required(login_url="/mytrip/login")
def neweventfinal(request):
	username=request.session.get('username','')
	name = request.session.get('ename','')

	# fetching event object
	myevent = events.objects.raw('SELECT * FROM mytrip_events WHERE name = %s',[name])[0]

	# fetching form data
	myevent.address = request.POST.get('address', '')
	myevent.lat = request.POST.get('lat', '')
	myevent.lng = request.POST.get('lng', '')

	#saving event
	myevent.save()

	return HttpResponseRedirect('/mytrip/home')

# event registeration form
@login_required(login_url="/mytrip/login")
def register(request, ename):
	username=request.session.get('username','')

	# fetching event object
	myevent = events.objects.raw('SELECT * FROM mytrip_events WHERE name = %s',[ename])[0]

	if username != '':
		return render(request,"register.html",{'usernm':username, 'event':myevent})
	else:
		return render(request,'home.html')

# event registeration
@login_required(login_url="/mytrip/login")
def registerfinal(request):
	username=request.session.get('username','')

	# fetching form data
	fullname = request.POST.get('fullname', '')
	email = request.POST.get('email', '')
	mobileno = request.POST.get('phone', '')
	ename = request.POST.get('ename', '')

	# fetching user object
	person = User.objects.raw("SELECT * FROM mytrip_users WHERE username = %s",[username])[0]
	# fetching event object
	myevent = events.objects.raw('SELECT * FROM mytrip_events WHERE name = %s',[ename])[0]

	usr_id = person.pk
	evnt_id = myevent.pk
	row=0

	# checking if user has already registered for the event or not
	# checking for email
	for p in event_registration.objects.raw("SELECT * FROM mytrip_event_registration WHERE evnt_id = %s AND email = %s",[evnt_id,email]):
		row = row+1
	if row != 0:
		return HttpResponseRedirect("/mytrip/home")
	# checking for mobile no
	for p in event_registration.objects.raw("SELECT * FROM mytrip_event_registration WHERE evnt_id = %s AND mobileno = %s",[evnt_id,mobileno]):
		row = row+1	
	if row != 0:
		return HttpResponseRedirect("/mytrip/home")

	# registering user for the event
	reg = event_registration(fullname=fullname, email=email, mobileno=mobileno, usr_id=usr_id, evnt_id=evnt_id)
	reg.save();

	subject, from_email, to = 'Event registration', 'YOUR_EMAIL',email
	text_content = 'This is an important message.'
	html_content = '<p><b>Your registration for the event has been confirmed!!</b><br>Event details are as under:</p><p><b>Event name: </b>' + myevent.name + '<br><b>Date: </b>' + myevent.event_date.strftime("%d-%b-%Y %H:%M:%S") + '<br><b>Contact: </b>' + myevent.contact + '<br><b>Address: </b>' + myevent.address + '</p>'
	msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
	msg.attach_alternative(html_content, "text/html")
	try:
		msg.send()
	except:
		print('There was an error sending an email: ')
		return HttpResponse("ERROR")
	return HttpResponseRedirect("/mytrip/home")

# profile page of the user
@login_required(login_url="/mytrip/login")
def profile(request):
	usernm=request.session.get('username','')

	# fetching user object
	person = User.objects.raw("SELECT * FROM mytrip_users WHERE username = %s",[usernm])[0]

	# fetching event objects whose organizer is user
	myevent = events.objects.raw('SELECT * FROM mytrip_events WHERE org_id = %s', [person.pk])

	# fetching event objects in which user has registered
	#regevent = event_registration.objects.raw('SELECT * FROM mytrip_event_registration INNER JOIN mytrip_events WHERE mytrip_event_registration.evnt_id = mytrip_events.id AND usr_id = %s', [person.pk])
	regevent = event_registration.objects.filter(usr = person)

	return render(request,"profile.html",{'usernm':usernm, 'person':person, 'myevent': myevent, 'regevent': regevent})

# edit profile page
@login_required(login_url="/mytrip/login")
def edit(request):
	username=request.session.get('username','')
	person = User.objects.raw("SELECT * FROM mytrip_users WHERE username = %s",[username])[0]
	if username != '':
		return render(request,"edit.html",{'usernm':username, 'person':person})
	else:
		return render(request,'edit.html')

# edit profile page
@login_required(login_url="/mytrip/login")
def editfinal(request):
	uname = request.POST.get('username', '')
	emailid = request.POST.get('email', '')
	fname = request.POST.get('firstname', '')
	lname = request.POST.get('lastname', '')
	mobile = request.POST.get('phone', '')
	
	username=request.session.get('username','')
	person = User.objects.raw("SELECT * FROM mytrip_users WHERE username = %s",[username])[0]

	person.username = uname
	person.first_name = fname
	person.last_name = lname
	person.email = emailid
	person.mobileno = mobile
	person.save()
	request.session['username']=uname
	return HttpResponseRedirect("/mytrip/home")

# for downloading registration details file in csv format
@login_required(login_url="/mytrip/login")
def download(request,ename):
	event = events.objects.raw('SELECT * FROM mytrip_events WHERE name = %s',[ename])[0]
	reguser = event_registration.objects.raw("SELECT * FROM mytrip_event_registration WHERE evnt_id = %s",[event.pk])
	
	# name of the downloaded file
	filenm = 'registrations-' + ename + '.csv'
	response = HttpResponse(content_type='text/csv')

	# attaching file to the response
	response['Content-Disposition'] = 'attachment; filename=' + filenm

	# writing data in the file
	writer = csv.writer(response)
	writer.writerow(['fullname','email','mobileno'])
	for r in reguser:
		writer.writerow([r.fullname,r.email,r.mobileno])
	return response

# edit event page
@login_required(login_url="/mytrip/login")
def editevent(request, ename):
	username=request.session.get('username','')
	# fetching event object
	myevent = events.objects.raw('SELECT * FROM mytrip_events WHERE name = %s',[ename])[0]
	return render(request,"editevent.html",{'usernm':username, 'e':myevent})

# edit event page
@login_required(login_url="/mytrip/login")
def editeventfinal(request):
	username=request.session.get('username','')

	# fetching form data
	ename = request.POST.get('ename', '')
	capacity = request.POST.get('capacity', '')
	# event_date = request.POST.get('event_date','')
	ephoto = request.FILES.get('photo')

	# fetching event object
	myevent = events.objects.raw('SELECT * FROM mytrip_events WHERE name = %s',[ename])[0]

	myevent.capacity = capacity
	# myevent.event_date = event_date
	myevent.photo = ephoto
	myevent.save()
	return HttpResponseRedirect("/mytrip/event/" + ename)

# edit event page
@login_required(login_url="/mytrip/login")
def deleteevent(request, ename):
	username=request.session.get('username','')

	# fetching event object
	event = events.objects.raw('SELECT * FROM mytrip_events WHERE name = %s',[ename])[0]
	# fetching event registration objects
	eventreg = event_registration.objects.raw('SELECT * FROM mytrip_event_registration WHERE evnt_id = %s',[event.pk])
	for r in eventreg:
		subject, from_email, to = 'Event Cancelled', 'YOUR_EMAIL',r.email
		text_content = 'This is an important message.'
		html_content = '<p><b>'+ ename +'</b> has been cancelled by the organizers.<br>Your amount will be refunded within 10 working days, if any.<br>Sorry for the inconvenience.<br><br>Team TripManager</p>'
		msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
		msg.attach_alternative(html_content, "text/html")
		try:
			msg.send()
		except:
			print('There was an error sending an email: ')
			return HttpResponse("ERROR")
		r.delete();
	event.delete();

	return HttpResponseRedirect('/mytrip/home')

# logout view
@login_required(login_url="/mytrip/login")
def logout(request):
	#del request.session['username']
	auth.logout(request)
	return HttpResponseRedirect('/mytrip/home')
