import json
import logging
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.urls import reverse
from home.decorators import campuspartner_required, admin_required
from django.contrib.auth import authenticate, login, logout
import csv
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import account_activation_token
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from collections import OrderedDict
import sys
sys.setrecursionlimit(1500)
# importing models in home views.py
from .models import *
from university.models import *
from partners.models import *
from projects.models import *
# importing filters in home views.py, used for adding filter
from .filters import *
# aggregating function
from django.db.models import Sum
from django.conf import settings
# importing forms into home views.py
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.template.loader import get_template
from django.core.mail import EmailMessage
import googlemaps
from shapely.geometry import shape, Point
import pandas as pd
import os
from googlemaps import Client
from home import context_processors
import boto3
from UnoCPI import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import sys
import psycopg2
import json
import datetime
# The imports below are for running sql queries for Charts
from django.db import connection
from UnoCPI import sqlfiles
from projects.forms import K12ChoiceForm,CecPartChoiceForm
from projects.models import AcademicYear, EngagementType

sql=sqlfiles
logger = logging.getLogger(__name__)
#writing into amazon s3 bucket
ACCESS_ID=settings.AWS_ACCESS_KEY_ID
ACCESS_KEY=settings.AWS_SECRET_ACCESS_KEY
s3 = boto3.resource('s3',
         aws_access_key_id=ACCESS_ID,
         aws_secret_access_key= ACCESS_KEY)

# Read JSON files for charts

charts_project_obj = s3.Object(settings.AWS_STORAGE_BUCKET_NAME, 'charts_json/projects.json')
charts_projects = charts_project_obj.get()['Body'].read().decode('utf-8')
charts_community_obj = s3.Object(settings.AWS_STORAGE_BUCKET_NAME, 'charts_json/community_partners.json')
charts_communities = charts_community_obj.get()['Body'].read().decode('utf-8')
charts_campus_obj = s3.Object(settings.AWS_STORAGE_BUCKET_NAME, 'charts_json/campus_partners.json')
charts_campuses = charts_campus_obj.get()['Body'].read().decode('utf-8')
charts_mission_obj = s3.Object(settings.AWS_STORAGE_BUCKET_NAME, 'charts_json/mission_subcategories.json')
charts_missions = charts_mission_obj.get()['Body'].read().decode('utf-8')

#read Partner.geojson from s3
content_object_partner = s3.Object(settings.AWS_STORAGE_BUCKET_NAME, 'geojson/Partner.geojson')
partner_geojson = content_object_partner.get()['Body'].read().decode('utf-8')

#read Project.geojson from s3
content_object_project = s3.Object(settings.AWS_STORAGE_BUCKET_NAME, 'geojson/Project.geojson')
project_geojson = content_object_project.get()['Body'].read().decode('utf-8')

gmaps = Client(key=settings.GOOGLE_MAPS_API_KEY)

def countyGEO():
    with open('home/static/GEOJSON/USCounties_final.geojson') as f:
        geojson1 = json.load(f)

    county = geojson1["features"]
    return county


##### Get the district GEOJSON ##############
def districtGEO():
    with open('home/static/GEOJSON/ID2.geojson') as f:
        geojson = json.load(f)

    district = geojson["features"]
    return district


def home(request):
    return render(request, 'home/communityPartner.html',
                  {'home': home})


def MapHome(request):
    return render(request, 'home/Map_Home.html',
                  {'MapHome': MapHome})

def thanks(request):
    return render(request, 'home/thanks.html',
                  {'thank': thanks})


def partners(request):
    data_definition = DataDefinition.objects.all()
    return render(request, 'home/partners.html',
                  {'partners': partners,
                   'data_definition': data_definition})


def map(request):
    return render(request, 'home/Countymap.html',
                  {'map': map})


def districtmap(request):
    return render(request, 'home/Districtmap.html',
                  {'districtmap': districtmap})


def projectmap(request):
    return render(request, 'home/projectmap.html',
                  {'projectmap': projectmap})


def cpipage(request):
    return render(request, 'home/CpiHome.html',
                  {'cpipage': cpipage})


@login_required()
def campusHome(request):
    return render(request, 'home/Campus_Home.html',
                  {'campusHome': campusHome})


@login_required()
def CommunityHome(request):
    return render(request, 'home/Community_Home.html',
                  {'CommunityHome': CommunityHome})


@login_required()
def AdminHome(request):
    user = authenticate(request)

    return render(request, 'home/admin_frame.html',
                  {'AdminHome': AdminHome})


@login_required()
def Adminframe(request):
    return render(request, 'home/admin_frame.html',
                  {'Adminframe': Adminframe})


def signup(request):
    return render(request, 'home/registration/signuporganization.html', {'signup': signup})


def signupuser(request):
    return render(request, 'home/registration/signupuser.html', {'signupuser': signupuser})

def recentchanges(request):
    #project app
    recent_project = Project.history.all().order_by('-history_date')[:100]
    recent_proj_mission = ProjectMission.history.all().order_by('-history_date')[:100]
    recent_proj_campus = ProjectCampusPartner.history.all().order_by('-history_date')[:100]
    recent_proj_comm = ProjectCommunityPartner.history.all().order_by('-history_date')[:100]
    #partner app
    recent_campus = CampusPartner.history.all().order_by('-history_date')[:100]
    recent_comm = CommunityPartner.history.all().order_by('-history_date')[:100]
    recent_comm_mission = CommunityPartnerMission.history.all().order_by('-history_date')[:100]
    #users and contacts
    # recent_user = User.history.all().order_by('-history_date')[:100]
    recent_contact = Contact.history.all().order_by('-history_date')[:50]

    return render(request, 'home/recent_changes.html', {'recent_project': recent_project, 'recent_proj_mission': recent_proj_mission,
                                                        'recent_proj_campus': recent_proj_campus, 'recent_proj_comm': recent_proj_comm,

                                                        'recent_campus': recent_campus, 'recent_comm':recent_comm, 'recent_comm_mission':recent_comm_mission,
                                                        'recent_contact':recent_contact})

def registerCampusPartnerUser(request):
    data = []
    for object in CampusPartner.objects.order_by('name'):
        data.append(object.name)
    if request.method == 'POST':
        user_form = CampususerForm(request.POST)
        campus_partner_user_form = CampusPartnerUserForm(request.POST)

        if user_form.is_valid() and campus_partner_user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.is_active = False
            new_user.is_campuspartner = True
            new_user.save()

            campuspartneruser = CampusPartnerUser(
                campus_partner=campus_partner_user_form.cleaned_data['campus_partner'], user=new_user)
            campuspartneruser.save()
            # Send an email to the user with the token:
            mail_subject = 'UNO-CPI Campus Partner Registration'
            current_site = get_current_site(request)
            message = render_to_string('account/acc_active_email.html', {
                'user': new_user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)).decode(),
                'token': account_activation_token.make_token(new_user),
            })
            to_email = new_user.email
            email = EmailMessage(mail_subject, message,to=[to_email])
            email.send()
            return render(request, 'home/register_done.html')
    else:
        user_form = CampususerForm()
        campus_partner_user_form = CampusPartnerUserForm()
    return render(request,
                  'home/registration/campus_partner_user_register.html',
                  {'user_form': user_form, 'campus_partner_user_form': campus_partner_user_form, 'data': data})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('/')
    else:
        return render(request, 'home/registration/register_fail.html')

@login_required()
def registerCommunityPartnerUser(request):
    community_partner_user_form = CommunityPartnerUserForm()
    user_form = CommunityuserForm()
    commPartner = []
    for object in CommunityPartner.objects.order_by('name'):
        commPartner.append(object.name)

    if request.method == 'POST':
        user_form = CommunityuserForm(request.POST)
        community_partner_user_form = CommunityPartnerUserForm(request.POST)
        if user_form.is_valid() and community_partner_user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.is_communitypartner = True
            new_user.save()
            communitypartneruser = CommunityPartnerUser(
                community_partner=community_partner_user_form.cleaned_data['community_partner'], user=new_user)
            communitypartneruser.save()
            return render(request, 'home/communityuser_register_done.html', )
    return render(request,
                  'home/registration/community_partner_user_register.html',
                  {'user_form': user_form, 'community_partner_user_form': community_partner_user_form
                      , 'commPartner': commPartner})


# uploading the projects data via csv file

@login_required()
@admin_required()
def upload_project(request):
    Missionlist=[]
    CampusPartnerlist=[]
    CommTypelist=[]
    if request.method == 'GET':
        download_projects_url = '/media/projects_sample.csv'
        return render(request, 'import/uploadProject.html',
                      {'download_projects_url': download_projects_url})
    if request.method == 'POST':
        csv_file = request.FILES["csv_file"]
        decoded = csv_file.read().decode('ISO 8859-1').splitlines()
        reader = csv.DictReader(decoded)
        campus_query = CampusPartner.objects.all()
        campus_names = [campus.name for campus in campus_query]
        community_query = CommunityPartner.objects.all()
        community_names = [community.name for community in community_query]
        for row in reader:
            data_dict = dict(OrderedDict(row))
            form = UploadProjectForm(data_dict)
            campus = data_dict['campus_partner'] in campus_names
            community = data_dict['community_partner'] in community_names
            if campus and community and form.is_valid():
                form.save()
                form_campus = UploadProjectCampusForm(data_dict)
                form_community = UploadProjectCommunityForm(data_dict)
                form_mission = UploadProjectMissionForm(data_dict)
                if form_campus.is_valid() and form_community.is_valid() and form_mission.is_valid():
                    form_campus.save()
                    form_community.save()
                    form_mission.save()

    return render(request, 'import/uploadProjectDone.html')


# uploading the community data via csv file


@login_required()
@admin_required()
def upload_community(request):
    if request.method == 'GET':
        download_community_url = '/media/community_sample.csv'
        return render(request, 'import/uploadCommunity.html',
                      {'download_community_url': download_community_url})
    csv_file = request.FILES["csv_file"]
    decoded = csv_file.read().decode('ISO 8859-1').splitlines()
    reader = csv.DictReader(decoded)
    for row in reader:
        data_dict = dict(OrderedDict(row))

        form = UploadCommunityForm(data_dict)

        if form.is_valid():
            form.save()
            form_mission = UploadCommunityMissionForm(data_dict)
            if form_mission.is_valid():
                form_mission.save()
    return render(request, 'import/uploadCommunityDone.html')


# uploading the campus data via csv file


@login_required()
@admin_required()
def upload_campus(request):
    if request.method == 'GET':
        download_campus_url = '/media/campus_sample.csv'
        return render(request, 'import/uploadCampus.html',
                      {'download_campus_url': download_campus_url})
    if request.method == 'POST':
        csv_file = request.FILES["csv_file"]
        decoded = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded)
        for row in reader:
            data_dict = dict(OrderedDict(row))
            college_count = College.objects.filter(college_name=data_dict['college_name']).count()
            if not college_count:
                form_college = UploadCollege(data_dict)
                if form_college.is_valid():
                    form_college.save()
                    form = UploadCampusForm(data_dict)
                    if form.is_valid():
                        form.save()
            else:
                form = UploadCampusForm(data_dict)
                if form.is_valid():
                    form.save()
    return render(request, 'import/uploadCampusDone.html')


# uploading the campus data via csv file
@login_required()
@admin_required()
def upload_income(request):
    if request.method == 'GET':
        download_campus_url = '/media/household_income.csv'
        return render(request, 'import/uploadIncome.html',
                      {'download_campus_url': download_campus_url})
    if request.method == 'POST':
        csv_file = request.FILES["csv_file"]
        decoded = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded)
        for row in reader:
            data_dict = dict(OrderedDict(row))
            form = UploadIncome(data_dict)
            if form.is_valid():
                form.save()
    return render(request, 'import/uploadIncomeDone.html')


# (14) Primary Focus Area with Topics Details  Report: - new focus areas report logic
def primary_focus_topic_info(request):
    data_definition = DataDefinition.objects.all()
    data_list =[]
    rpt_total_comm_partners = 0
    rpt_total_camp_partners = 0
    rpt_total_projects = 0
    rpt_total_uno_students = 0
    rpt_total_uno_hours = 0
    rpt_total_k12_students = 0
    rpt_total_k12_hours = 0
    missions_filter = ProjectMissionFilter(request.GET, queryset=ProjectMission.objects.filter(mission_type='Primary'))
    year_filter = ProjectFilter(request.GET, queryset=Project.objects.all())
    communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all())
    campus_filter_qs = CampusPartner.objects.all()
    campus_project_filter = [{'name': m.name, 'id': m.id} for m in campus_filter_qs]
    # campus_filter = ProjectCampusFilter(request.GET, queryset=ProjectCampusPartner.objects.all())

    engagement_filter_qs = EngagementType.objects.all()
    eng_project_filter = [{'name': e.name, 'id': e.id} for e in engagement_filter_qs]

    college_filter = CampusFilter(request.GET, queryset=CampusPartner.objects.all())
    college_unit_filter = request.GET.get('college_name', None)
    if college_unit_filter is None or college_unit_filter == "All" or college_unit_filter == '':
        college_unit_cond = '%'
        campus_filter_qs = CampusPartner.objects.all()

    else:
        college_unit_cond = college_unit_filter
        campus_filter_qs = CampusPartner.objects.filter(college_name_id=college_unit_filter)
    campus_project_filter = [{'name': m.name, 'id': m.id} for m in campus_filter_qs]


    community_type_filter = request.GET.get('community_type', None)
    if community_type_filter is None or community_type_filter == "All" or community_type_filter == '':
        community_type_cond = '%'
    else:
        community_type_cond = community_type_filter


    academic_year_filter = request.GET.get('academic_year', None)
    acad_years = AcademicYear.objects.all()
    yrs =[]
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    if month > 7:
        a_year = str(year-1) + "-" + str(year )[-2:]
    else:
        a_year = str(year - 2) + "-" + str(year-1)[-2:]

    for e in acad_years:
        yrs.append(e.id)
    try:
        acad_year = AcademicYear.objects.get(academic_year=a_year).id
        default_yr_id = acad_year - 1
    except AcademicYear.DoesNotExist:
        default_yr_id = max(yrs)
    max_yr_id = max(yrs)


    if academic_year_filter is None or academic_year_filter == '':
        academic_start_year_cond = int(default_yr_id)
        academic_end_year_cond = int(default_yr_id)

    elif academic_year_filter == "All":
        academic_start_year_cond = int(max_yr_id)
        academic_end_year_cond = 1
    else:
        academic_start_year_cond = int(academic_year_filter)
        academic_end_year_cond = int(academic_year_filter)

    campus_partner_filter = request.GET.get('campus_partner', None)
    if campus_partner_filter is None or campus_partner_filter == "All" or campus_partner_filter == '':
        campus_partner_cond = '%'
        campus_id = -1
    else:
        campus_partner_cond = campus_partner_filter
        campus_id = int(campus_partner_filter)

    mission_type_filter = request.GET.get('mission', None)
    if mission_type_filter is None or mission_type_filter == "All" or mission_type_filter == '':
        mission_type_cond = '%'
    else:
        mission_type_cond = mission_type_filter

    cec_part_choices = CecPartChoiceForm(initial={'cec_choice': "All"})

    cec_part_selection = request.GET.get('weitz_cec_part', None)
    if cec_part_selection is None or cec_part_selection == "All" or cec_part_selection == '':
        #cec_part_selection = cec_part_init_selection
        cec_comm_part_cond = '%'
        cec_camp_part_cond = '%'

    elif cec_part_selection == "CURR_COMM":
        cec_comm_part_cond = 'Current'
        cec_camp_part_cond = '%'

    elif cec_part_selection == "FORMER_COMM":
        cec_comm_part_cond = 'Former'
        cec_camp_part_cond = '%'

    elif cec_part_selection == "FORMER_CAMP":
        cec_comm_part_cond = '%'
        cec_camp_part_cond = 'Former'

    elif cec_part_selection == "CURR_CAMP":
        cec_comm_part_cond = '%'
        cec_camp_part_cond = 'Current'

    engagement_filter = request.GET.get('engagement_type', None)
    if engagement_filter is None or engagement_filter == "All" or engagement_filter == '':
        engagement_cond = '%'
        engagement_id = -1
    else:
        engagement_cond = engagement_filter
        engagement_id = int(engagement_filter)

    params = [mission_type_cond, community_type_cond, campus_partner_cond, college_unit_cond, engagement_cond,
              academic_start_year_cond, academic_end_year_cond, cec_comm_part_cond, cec_camp_part_cond,
              mission_type_cond, community_type_cond, campus_partner_cond, college_unit_cond, engagement_cond,
              academic_start_year_cond, academic_end_year_cond, cec_comm_part_cond, cec_camp_part_cond]
    cursor = connection.cursor()
    cursor.execute(sql.primaryFocusTopic_report_sql, params)

    #cec_part_choices = CecPartChoiceForm()
    cec_part_choices = CecPartChoiceForm(initial={'cec_choice': cec_part_selection})


    for obj in cursor.fetchall():
        comm_ids = obj[12]
        print('comm_ids---',comm_ids)

        proj_ids = obj[10]
        print('proj_ids---',proj_ids)

        proj_idList = ''
        comm_idList = ''

        if proj_ids is not None:
            if None in proj_ids:
                proj_ids.pop(-1)
            print('project list --',len(proj_ids))
            name_count = 0
            if len(proj_ids) > 0:
                for i in proj_ids:
                    proj_idList = proj_idList + str(i)
                    if name_count < len(proj_ids) - 1:
                        proj_idList = proj_idList + str(",")
                        name_count = name_count + 1

        if comm_ids is not None:
            if None in comm_ids:
                comm_ids.pop(-1)
            print('comm_ids list --',len(comm_ids))

            name_count = 0
            if len(comm_ids) > 0:
                for i in comm_ids:
                    comm_idList = comm_idList + str(i)
                    if name_count < len(comm_ids) - 1:
                        comm_idList = comm_idList + str(",")
                        name_count = name_count + 1

        if obj[0] == 'Focus':
            rpt_total_comm_partners += obj[11]
            rpt_total_camp_partners += obj[13]
            rpt_total_projects += obj[9]
            rpt_total_uno_students += obj[14]
            rpt_total_uno_hours += obj[15]
            rpt_total_k12_students += obj[16]
            rpt_total_k12_hours += obj[17]

        data_list.append({"rec_type": obj[0], "focus_id": obj[1],
                          "focus_name": obj[2], "focus_desc": obj[3],
                          "focus_image": obj[4], "focus_color": obj[5],
                          "topic_id": obj[6], "topic_name": obj[7], "topic_desc": obj[8],
                          "project_count": obj[9],  "project_id_array": obj[10], "proj_id_list": proj_idList,
                          "community_count": obj[11], "comm_id_array": obj[12],
                          "comm_id_list": comm_idList, "campus_count": obj[13],
                          "total_uno_students": obj[14], "total_uno_hours": obj[15],
                          "total_k12_students": obj[16], "total_k12_hours": obj[17]})

    #print('data_list: ' + str(data_list))

    return render(request, 'reports/ProjectFocusTopicInfo.html',
                   {'college_filter': college_filter, 'missions_filter': missions_filter,
                    'engagement_filter': eng_project_filter, 'engagement_id': engagement_id,
                    'year_filter': year_filter, 'focus_topic_list': data_list,
                    'data_definition':data_definition, 'communityPartners' : communityPartners ,
                    'campus_filter': campus_project_filter, 'campus_id': campus_id, 'cec_part_choices': cec_part_choices,
                    'rpt_total_comm_partners': rpt_total_comm_partners, 'rpt_total_camp_partners': rpt_total_camp_partners,
                    'rpt_total_projects': rpt_total_projects,
                    'rpt_total_uno_students': rpt_total_uno_students, 'rpt_total_uno_hours': rpt_total_uno_hours,
                    'rpt_total_k12_students': rpt_total_k12_students, 'rpt_total_k12_hours': rpt_total_k12_hours})


# (14) Mission Summary Report: filter by Semester, EngagementType - Old Logic
def project_partner_info_old(request):
    missions = MissionArea.objects.all()
    data_definition = DataDefinition.objects.all()
    mission_dict = {}
    mission_list = []
    proj_total = 0
    comm_total = 0
    students_total = 0
    hours_total = 0

    legislative_choices = []
    legislative_search = ''

    # set legislative_selection on template choices field -- Manu Start
    legislative_selection = request.GET.get('legislative_value', None)

    status_draft = Status.objects.filter(name='Drafts')
    # status_draft_ids = status_draft.qs.value_list('id', flat=True)

    if legislative_selection is None:
        legislative_selection = 'All'

    legislative_choices.append('All')
    for i in range(1, 50):
        legistalive_val = 'Legislative District ' + str(i)
        legislative_choices.append(legistalive_val)

    if legislative_selection is not None and legislative_selection != 'All':
        legislative_search = legislative_selection.split(" ")[2]

    if legislative_selection is None or legislative_selection == "All" or legislative_selection == '':
        communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all())
        project_filter = ProjectFilter(request.GET, queryset=Project.objects.all().exclude(status__in=status_draft))
    else:
        communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.filter(
            legislative_district=legislative_search))
        project_filter = ProjectFilter(request.GET,
                                       queryset=Project.objects.filter(legislative_district=legislative_search).exclude(
                                           status__in=status_draft))
    # legislative district end -- Manu

    # project_filter = ProjectFilter(request.GET, queryset=Project.objects.all()) -- commented by Manu
    campus_filter = ProjectCampusFilter(request.GET, queryset=ProjectCampusPartner.objects.all())
    # communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all()) -- commented by Manu
    college_filter = CampusFilter(request.GET, queryset=CampusPartner.objects.all())

    # college_filtered_ids = [campus.id for campus in college_filter.qs]
    college_filtered_ids = college_filter.qs.values_list('id', flat=True)
    campus_project_filter = ProjectCampusFilter(request.GET, queryset=ProjectCampusPartner.objects.filter(
        campus_partner_id__in=college_filtered_ids))
    # campus_project_filter_ids = [project.project_name_id for project in campus_project_filter.qs]
    campus_project_filter_ids = campus_project_filter.qs.values_list('project_name', flat=True)

    # campus_filtered_ids = [project.project_name_id for project in campus_filter.qs]
    campus_filtered_ids = campus_filter.qs.values_list('project_name', flat=True)

    # project_filtered_ids = [project.id for project in project_filter.qs]
    project_filtered_ids = project_filter.qs.values_list('id', flat=True)
    print ('project_filtered_ids :', project_filtered_ids)
    # project_filtered_ids = list(set(project_filtered_ids1).difference(project_drafted_ids))

    # community_filtered_ids = [community.id for community in communityPartners.qs]
    community_filtered_ids = communityPartners.qs.values_list('id', flat=True)
    comm_filter = ProjectCommunityFilter(request.GET, queryset=ProjectCommunityPartner.objects.filter(
        community_partner_id__in=community_filtered_ids))
    # comm_filtered_ids = [project.project_name_id for project in comm_filter.qs]
    comm_filtered_ids = comm_filter.qs.values_list('project_name', flat=True)

    proj1_ids = list(set(campus_filtered_ids).intersection(project_filtered_ids))
    proj2_ids = list(set(campus_project_filter_ids).intersection(proj1_ids))
    project_ids = list(set(proj2_ids).intersection(comm_filtered_ids))

    proj_comm = ProjectCommunityPartner.objects.filter(project_name_id__in=project_ids).filter(
        community_partner_id__in=community_filtered_ids).distinct()
    proj_comm_ids = [community.community_partner_id for community in proj_comm]

    for m in missions:
        project_id_list = []
        mission_dict['id'] = m.id
        mission_dict['mission_name'] = m.mission_name
        project_count = ProjectMission.objects.filter(mission=m.id).filter(
            project_name_id__in=project_filtered_ids).filter(mission_type='Primary').count()
        community_count = CommunityPartnerMission.objects.filter(mission_area_id=m.id).filter(
            mission_type='Primary').filter(community_partner_id__in=proj_comm_ids).count()
        comm_id_filter = CommunityPartnerMission.objects.filter(mission_area_id=m.id).filter(
            mission_type='Primary').filter(community_partner_id__in=proj_comm_ids)
        comm_id_list = list(community.community_partner_id for community in comm_id_filter)
        p_mission = ProjectMission.objects.filter(mission=m.id).filter(project_name_id__in=project_filtered_ids).filter(
            mission_type='Primary')

        a = request.GET.get('engagement_type', None)
        b = request.GET.get('academic_year', None)
        c = request.GET.get('campus_partner', None)
        d = request.GET.get('college_name', None)
        if a is None or a == "All" or a == '':
            if b is None or b == "All" or b == '':
                if c is None or c == "All" or c == '':
                    if d is None or d == "All" or d == '':
                        community_count = CommunityPartnerMission.objects.filter(mission_area_id=m.id).filter(
                            mission_type='Primary').filter(community_partner_id__in=community_filtered_ids).count()
                        comm_id_filter = CommunityPartnerMission.objects.filter(mission_area_id=m.id).filter(
                            mission_type='Primary').filter(community_partner_id__in=community_filtered_ids)
                        comm_id_list = list(community.community_partner_id for community in comm_id_filter)

        e = request.GET.get('community_type', None)
        f = request.GET.get('weitz_cec_part', None)
        if f is None or f == "All" or f == '':
            if e is None or e == "All" or e == '':
                p_mission = ProjectMission.objects.filter(mission=m.id).filter(
                    project_name_id__in=project_filtered_ids).filter(mission_type='Primary')
                project_count = ProjectMission.objects.filter(mission=m.id).filter(
                    project_name_id__in=project_filtered_ids).filter(mission_type='Primary').count()

        mission_dict['project_count'] = project_count
        mission_dict['community_count'] = community_count
        total_uno_students = 0
        total_uno_hours = 0

        for pm in p_mission:
            project_id_list.append(pm.project_name_id)
            uno_students = Project.objects.filter(id=pm.project_name_id).aggregate(Sum('total_uno_students'))
            uno_hours = Project.objects.filter(id=pm.project_name_id).aggregate(Sum('total_uno_hours'))
            total_uno_students += uno_students['total_uno_students__sum']
            total_uno_hours += uno_hours['total_uno_hours__sum']

        mission_dict['total_uno_hours'] = total_uno_hours
        mission_dict['total_uno_students'] = total_uno_students
        mission_dict['project_id_list'] = project_id_list
        mission_dict['comm_id_list'] = comm_id_list
        comm_ids = ''
        name_count = 0

        for i in comm_id_list:
            comm_ids = comm_ids + str(i)

            if name_count < len(comm_id_list) - 1:
                comm_ids = comm_ids + str(",")
                name_count = name_count + 1

        mission_dict['comm_ids'] = comm_ids

        project_name_id = ''
        project_name_count = 0

        for z in project_id_list:
            project_name_id = project_name_id + str(z)

            if project_name_count < len(project_id_list) - 1:
                project_name_id = project_name_id + str(",")
                project_name_count = project_name_count + 1

        mission_dict['project_name_ids'] = project_name_id

        mission_list.append(mission_dict.copy())
        proj_total += project_count
        comm_total += community_count
        students_total += total_uno_students
        hours_total += total_uno_hours

    college_value = request.GET.get('college_name', None)
    if college_value is None or college_value == "All" or college_value == '':
        campus_filter_qs = CampusPartner.objects.all()
    else:
        campus_filter_qs = CampusPartner.objects.filter(college_name_id=college_value)
    campus_filter = [{'name': m.name, 'id': m.id} for m in campus_filter_qs]

    campus_id = request.GET.get('campus_partner')
    if campus_id == "All":
        campus_id = -1
    if (campus_id is None or campus_id == ''):
        campus_id = 0
    else:
        campus_id = int(campus_id)

    return render(request, 'reports/ProjectPartnerInfo_old.html',
                  {'project_filter': project_filter, 'data_definition': data_definition,
                   'legislative_choices': legislative_choices, 'legislative_value': legislative_selection,
                   'communityPartners': communityPartners, 'mission_list': mission_list,
                   'campus_filter': campus_filter, 'college_filter': college_filter,
                   'proj_total': proj_total, 'comm_total': comm_total, 'students_total': students_total,
                   'hours_total': hours_total, 'campus_id': campus_id})


def engagement_info(request):
    data_definition = DataDefinition.objects.all()
    data_list =[]
    missions_filter = ProjectMissionFilter(request.GET, queryset=ProjectMission.objects.filter(mission_type='Primary'))
    year_filter = ProjectFilter(request.GET, queryset=Project.objects.all())
    communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all())
    campus_filter_qs = CampusPartner.objects.all()
    campus_project_filter = [{'name': m.name, 'id': m.id} for m in campus_filter_qs]
    college_partner_filter = CampusFilter(request.GET, queryset=CampusPartner.objects.all())
    # campus_filter = ProjectCampusFilter(request.GET, queryset=ProjectCampusPartner.objects.all())

    college_unit_filter = request.GET.get('college_name', None)
    if college_unit_filter is None or college_unit_filter == "All" or college_unit_filter == '':
        college_unit_cond = '%'
        campus_filter_qs = CampusPartner.objects.all()

    else:
        college_unit_cond = college_unit_filter
        campus_filter_qs = CampusPartner.objects.filter(college_name_id=college_unit_filter)
    campus_project_filter = [{'name': m.name, 'id': m.id} for m in campus_filter_qs]


    community_type_filter = request.GET.get('community_type', None)
    if community_type_filter is None or community_type_filter == "All" or community_type_filter == '':
        community_type_cond = '%'
    else:
        community_type_cond = community_type_filter


    academic_year_filter = request.GET.get('academic_year', None)
    acad_years = AcademicYear.objects.all()
    yrs =[]
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    if month > 7:
        a_year = str(year-1) + "-" + str(year )[-2:]
    else:
        a_year = str(year - 2) + "-" + str(year-1)[-2:]

    for e in acad_years:
        yrs.append(e.id)
    try:
        acad_year = AcademicYear.objects.get(academic_year=a_year).id
        default_yr_id = acad_year
    except AcademicYear.DoesNotExist:
        default_yr_id = max(yrs)
    max_yr_id = max(yrs)


    if academic_year_filter is None or academic_year_filter == '':
        academic_start_year_cond = int(default_yr_id)
        academic_end_year_cond = int(default_yr_id)

    elif academic_year_filter == "All":
        academic_start_year_cond = int(max_yr_id)
        academic_end_year_cond = 1
    else:
        academic_start_year_cond = int(academic_year_filter)
        academic_end_year_cond = int(academic_year_filter)

    campus_partner_filter = request.GET.get('campus_partner', None)
    if campus_partner_filter is None or campus_partner_filter == "All" or campus_partner_filter == '':
        campus_partner_cond = '%'
        campus_id = -1
    else:
        campus_partner_cond = campus_partner_filter
        campus_id = int(campus_partner_filter)

    mission_type_filter = request.GET.get('mission', None)
    if mission_type_filter is None or mission_type_filter == "All" or mission_type_filter == '':
        mission_type_cond = '%'
    else:
        mission_type_cond = mission_type_filter

    cec_part_choices = CecPartChoiceForm(initial={'cec_choice': "All"})

    cec_part_selection = request.GET.get('weitz_cec_part', None)
    if cec_part_selection is None or cec_part_selection == "All" or cec_part_selection == '':
        #cec_part_selection = cec_part_init_selection
        cec_comm_part_cond = '%'
        cec_camp_part_cond = '%'

    elif cec_part_selection == "CURR_COMM":
        cec_comm_part_cond = 'Current'
        cec_camp_part_cond = '%'

    elif cec_part_selection == "FORMER_COMM":
        cec_comm_part_cond = 'Former'
        cec_camp_part_cond = '%'

    elif cec_part_selection == "FORMER_CAMP":
        cec_comm_part_cond = '%'
        cec_camp_part_cond = 'Former'

    elif cec_part_selection == "CURR_CAMP":
        cec_comm_part_cond = '%'
        cec_camp_part_cond = 'Current'

    # params = [community_type_cond, cec_comm_part_cond, mission_type_cond,  campus_partner_cond, college_unit_cond,
    #           academic_start_year_cond, academic_end_year_cond, cec_camp_part_cond]
    cursor = connection.cursor()
    engagement_start = "with eng_type_filter as (select \
                   p.engagement_type_id eng_id \
                  , count(distinct p.project_name) Projects \
                  , array_agg(distinct p.id) projects_id \
                  , count(distinct pcomm.community_partner_id) CommPartners \
                  , array_agg(distinct pcomm.community_partner_id) CommPartners_id \
                  , count(distinct pcamp.campus_partner_id) CampPartners \
                  , sum(p.total_uno_students) numberofunostudents \
                  , sum(p.total_uno_hours) unostudentshours \
                   from projects_engagementtype e \
                   join projects_project p on p.engagement_type_id = e.id \
                   left join projects_projectcampuspartner pcamp on p.id = pcamp.project_name_id \
                   left join projects_projectcommunitypartner pcomm on p.id = pcomm.project_name_id \
                   left join partners_communitypartner comm on pcomm.community_partner_id = comm.id  \
                   left join projects_status s on  p.status_id = s.id \
                   left join projects_projectmission pm on p.id = pm.project_name_id  and lower(pm.mission_type) = 'primary' \
                   left join partners_campuspartner c on pcamp.campus_partner_id = c.id  \
                   where  s.name != 'Drafts'  and " \
                       "((p.academic_year_id <="+ str(academic_start_year_cond)  +") AND \
                            (COALESCE(p.end_academic_year_id, p.academic_year_id) >="+str(academic_end_year_cond)+"))"
    clause_query=" "
    if mission_type_cond !='%':
        clause_query += " and pm.mission_id::text like '"+ mission_type_cond +"'"

    if campus_partner_cond !='%':
        clause_query +=" and pcamp.campus_partner_id::text like '"+ campus_partner_cond +"'"

    if college_unit_cond !='%':
        clause_query += " and c.college_name_id::text like '"+ college_unit_cond +"'"


    if cec_camp_part_cond != '%':
        clause_query += " and c.cec_partner_status_id in (select id from partners_cecpartnerstatus where name like '"+ cec_camp_part_cond +"')"

    if community_type_cond !='%':
        clause_query += " and comm.community_type_id::text like '"+ community_type_cond +"'"

    if cec_comm_part_cond != '%':
        clause_query +=  " and  comm.cec_partner_status_id in  (select id from partners_cecpartnerstatus where name like '"+ cec_comm_part_cond +"')"



    query_end = engagement_start + clause_query + " group by eng_id \
                order by eng_id) \
                Select distinct eng.name eng_type \
                      , eng.description eng_desc \
                     , COALESCE(eng_type_filter.Projects, 0) proj \
                     , eng_type_filter.projects_id proj_ids \
                     , COALESCE(eng_type_filter.CommPartners, 0) comm \
                     , eng_type_filter.CommPartners_id comm_id \
                     , COALESCE(eng_type_filter.CampPartners, 0) camp \
                     , COALESCE(eng_type_filter.numberofunostudents, 0) unostu \
                     , COALESCE(eng_type_filter.unostudentshours, 0) unohr \
                 from projects_engagementtype eng \
                    left join eng_type_filter on eng.id = eng_type_filter.eng_id \
                group by eng_type, eng_desc, proj, proj_ids, comm, comm_id, camp, unostu, unohr \
                order by eng_type;"

    print("Final query: ", query_end)
    # cursor.execute(sql.engagement_types_report_sql, params)
    cursor.execute(query_end)
    #cec_part_choices = CecPartChoiceForm()
    cec_part_choices = CecPartChoiceForm(initial={'cec_choice': cec_part_selection})

    for obj in cursor.fetchall():
        comm_ids = obj[5]
        proj_ids = obj[3]
        proj_idList = ''
        comm_idList = ''
        if proj_ids is not None:
            name_count = 0
            if None in proj_ids:
                proj_ids.pop(-1)
                
            if len(proj_ids) > 0:
                for i in proj_ids:
                    proj_idList = proj_idList + str(i)
                    if name_count < len(proj_ids) - 1:
                        proj_idList = proj_idList + str(",")
                        name_count = name_count + 1

        if comm_ids is not None:
            name_count = 0
            if None in comm_ids:
                comm_ids.pop(-1)

            if len(comm_ids) > 0:
                for i in comm_ids:
                    comm_idList = comm_idList + str(i)
                    if name_count < len(comm_ids) - 1:
                        comm_idList = comm_idList + str(",")
                        name_count = name_count + 1

        data_list.append({"engagement_name": obj[0], "description": obj[1], "project_count": obj[2], "project_id_list": proj_idList,
                          "community_count": obj[4], "comm_id_list": comm_idList, "campus_count": obj[6], "total_uno_students": obj[7],
                          "total_uno_hours": obj[8]})


    return render(request, 'reports/EngagementTypeReport.html',
                   {'college_filter': college_partner_filter, 'missions_filter': missions_filter,
                    'year_filter': year_filter, 'engagement_List': data_list,
                    'data_definition':data_definition, 'communityPartners' : communityPartners ,
                    'campus_filter': campus_project_filter, 'campus_id':campus_id, 'cec_part_choices': cec_part_choices})



# Chart for projects with mission areas
@login_required()
def missionchart(request):
    data_definition = DataDefinition.objects.all()
    project_filter = ProjectFilter(request.GET, queryset=Project.objects.all())
    communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all())

    #set cec partner flag on template choices field
    cec_part_selection = request.GET.get('weitz_cec_part', None)
    cec_part_init_selection = "All"
    if cec_part_selection is None:
        cec_part_selection = cec_part_init_selection
    cec_part_choices = CecPartChoiceForm(initial={'cec_choice': cec_part_selection})

    college_filter = CampusFilter(request.GET, queryset=CampusPartner.objects.all())

    campus_filter_qs = CampusPartner.objects.all()
    campus_filter = [{'name': m.name, 'id': m.id, 'college':m.college_name_id} for m in campus_filter_qs]

    Projects = json.loads(charts_projects)
    CommunityPartners = json.loads(charts_communities)
    CampusPartners = json.loads(charts_campuses)
    MissionObject = json.loads(charts_missions)

    missionList = []
    for m in MissionObject:
        res = {'id': m['mission_area_id'], 'name': m['mission_area_name'], 'color': m['mission_color']}
        missionList.append(res)
    missionList = sorted(missionList, key=lambda i: i['name'])

    defaultyr = AcademicYear.objects.all()
    defaultYrID = defaultyr[defaultyr.count() - 2].id

    return render(request, 'charts/missionchart.html',
                  {'project_filter': project_filter, 'data_definition': data_definition,
                   'campus_filter': campus_filter, 'communityPartners': communityPartners, 'college_filter':college_filter,
                   'cec_part_choices': cec_part_choices, 'cec_part_selection': cec_part_selection, 'defaultYrID':defaultYrID,
                   'Projects':Projects, 'CommunityPartners':CommunityPartners, 'CampusPartners':CampusPartners, 'missionList':missionList })


@login_required()
def partnershipintensity(request):
    missions = MissionArea.objects.all()
    data_definition = DataDefinition.objects.all()
    legislative_choices = []
    legislative_search = ''
    legislative_selection = request.GET.get('legislative_value', None)

    if legislative_selection is None:
        legislative_selection = 'All'

    # legislative_choices.append('All')
    for i in range(1, 50):
        legistalive_val = 'Legislative District ' + str(i)
        legislative_choices.append(legistalive_val)

    if legislative_selection is not None and legislative_selection != 'All':
        legislative_search = legislative_selection.split(" ")[2]

    if legislative_selection is None or legislative_selection == "All" or legislative_selection == '':
        communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all())
        project_filter = ProjectFilter(request.GET, queryset=Project.objects.all())
    else:
        communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.filter(legislative_district=legislative_search))
        project_filter = ProjectFilter(request.GET,queryset=Project.objects.filter(legislative_district=legislative_search))

    y_selection = request.GET.get('y_axis', None)
    y_init_selection = "campus"
    # if y_selection is None:
        # y_selection = y_init_selection
    y_choices = YChoiceForm(initial={'y_choice': y_selection})

    college_filter = CampusFilter(request.GET, queryset=CampusPartner.objects.all())

    campus_filter_qs = CampusPartner.objects.all()
    campus_filter = [{'name': m.name, 'id': m.id, 'college':m.college_name_id} for m in campus_filter_qs]

    community_filter_qs = CommunityPartner.objects.all()
    community_filter = [{'name': m.name, 'id': m.id} for m in community_filter_qs]

    #set cec partner flag on template choices field
    cec_part_selection = request.GET.get('weitz_cec_part', None)
    # cec_part_init_selection = "All"
    # if cec_part_selection is None:
    #     cec_part_selection = "All"
    cec_part_choices = CecPartChoiceForm(initial={'cec_choice': cec_part_selection})

#########################
    # static_charts_projects = open('home/static/charts_json/projects.json')
    # static_charts_communities = open('home/static/charts_json/community_partners.json')
    # static_charts_campuses = open('home/static/charts_json/campus_partners.json')
    # static_charts_missions = open('home/static/charts_json/mission_subcategories.json')
    # Projects = json.load(static_charts_projects)
    # CommunityPartners = json.load(static_charts_communities)
    # CampusPartners = json.load(static_charts_campuses)
    # MissionObject = json.load(static_charts_missions)
#########################

    Projects = json.loads(charts_projects)
    CommunityPartners = json.loads(charts_communities)
    CampusPartners = json.loads(charts_campuses)
    MissionObject = json.loads(charts_missions)

    missionList = []
    for m in MissionObject:
        res = {'id': m['mission_area_id'], 'name': m['mission_area_name'], 'color': m['mission_color']}
        missionList.append(res)
    missionList = sorted(missionList, key=lambda i: i['name'])

    defaultyr = AcademicYear.objects.all()
    defaultYrID = defaultyr[defaultyr.count() - 2].id

    return render(request, 'charts/partnershipintensity.html',
                  {'data_definition': data_definition, 'project_filter': project_filter,
                  'legislative_choices':legislative_choices, 'legislative_value':legislative_selection,
                   'communityPartners': communityPartners, 'campus_filter': campus_filter, 'community_filter':community_filter,
                   'college_filter': college_filter, 'y_choices': y_choices, 'cec_part_choices': cec_part_choices, 'cec_part_selection': cec_part_selection,
                   'CommunityPartners': CommunityPartners, 'missionList': missionList, 'defaultYrID': defaultYrID,
                   'Projects':Projects, 'CampusPartners':CampusPartners})


# Trend Report Chart
@login_required()
@admin_required()
def trendreport(request):
    data_definition = DataDefinition.objects.all()

    communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all())
    project_filter = ProjectFilter(request.GET, queryset=Project.objects.all())
    missions_filter = ProjectMissionFilter(request.GET, queryset=ProjectMission.objects.filter(mission_type='Primary'))
    college_filter = CampusFilter(request.GET, queryset=CampusPartner.objects.all())

    campus_filter_qs = CampusPartner.objects.all()
    campus_filter = [{'name': m.name, 'id': m.id, 'college':m.college_name_id} for m in campus_filter_qs]

    #set cec partner flag on template choices field
    cec_part_selection = request.GET.get('weitz_cec_part', None)
    # cec_part_init_selection = "All"
    # if cec_part_selection is None:
    #     cec_part_selection = cec_part_init_selection
    # print('CEC Partner set in view ' + cec_part_selection)

    cec_part_choices = CecPartChoiceForm(initial={'cec_choice': cec_part_selection})

    yearList = []
    for y in AcademicYear.objects.all():
        res = {'id': y.id, 'name': y.academic_year}
        yearList.append(res)

    Projects = json.loads(charts_projects)
    CommunityPartners = json.loads(charts_communities)
    CampusPartners = json.loads(charts_campuses)

    return render(request, 'charts/trendreport.html',
                  { 'missions_filter': missions_filter, 'project_filter': project_filter, 'data_definition': data_definition,
                    'campus_filter': campus_filter, 'college_filter':college_filter, 'communityPartners': communityPartners,
                    'campus_filter': campus_filter, 'cec_part_choices': cec_part_choices, 'cec_part_selection': cec_part_selection,
                    'yearList':yearList, 'CampusPartners':CampusPartners, 'CommunityPartners': CommunityPartners, 'Projects':Projects})

@login_required()
def EngagementType_Chart(request):
    data_definition = DataDefinition.objects.all()
    missions_filter = ProjectMissionFilter(request.GET, queryset=ProjectMission.objects.filter(mission_type='Primary'))
    year_filter = ProjectFilter(request.GET, queryset=Project.objects.all())

    communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all())

    defaultyr = AcademicYear.objects.all()
    defaultYrID = defaultyr[defaultyr.count() - 2].id

    college_filter = CampusFilter(request.GET, queryset=CampusPartner.objects.all())

    campus_filter_qs = CampusPartner.objects.all()
    campus_filter = [{'name': m.name, 'id': m.id, 'college':m.college_name_id} for m in campus_filter_qs]

    cec_part_selection = request.GET.get('weitz_cec_part', None)
    cec_part_choices = CecPartChoiceForm(initial={'cec_choice': cec_part_selection})

    engagements = EngagementType.objects.all()
    engagementList = []
    for e in engagements:
        res = {'id': e.id, 'name': e.name}
        engagementList.append(res)
    engagementList = sorted(engagementList, key=lambda i: i['name'])

    Projects = json.loads(charts_projects)
    CommunityPartners = json.loads(charts_communities)
    CampusPartners = json.loads(charts_campuses)

    return render(request, 'charts/engagementtypechart2.html',
                 {'missions_filter': missions_filter, 'academicyear_filter': year_filter,'data_definition':data_definition,
                  'campus_filter': campus_filter, 'communityPartners' : communityPartners, 'college_filter': college_filter,
                  'engagementList':engagementList, 'cec_part_choices': cec_part_choices, 'cec_part_selection': cec_part_selection, 'defaultYrID':defaultYrID,
                  'Projects':Projects, 'CommunityPartners':CommunityPartners, 'CampusPartners':CampusPartners})


def GEOJSON():
    # if (os.path.isfile('home/static/GEOJSON/Partner.geojson')):  # check if the GEOJSON is already in the DB
    #     with open('home/static/GEOJSON/Partner.geojson') as f:
    #         geojson1 = json.load(f)  # get the GEOJSON
    #     collection = geojson1  # assign it the collection variable to avoid changing the other code
    collection = json.loads(partner_geojson)
    mission_list = MissionArea.objects.all()
    mission_list = [str(m.mission_name) +':'+str(m.mission_color) for m in mission_list]
    CommTypelist = CommunityType.objects.all()
    CommTypelist = [m.community_type for m in CommTypelist]
    CampusPartner_qs = CampusPartner.objects.all()
    CampusPartnerlist = [{'name':m.name, 'c_id':m.college_name_id} for m in CampusPartner_qs]
    collegeName_list = College.objects.all()
    collegeName_list = collegeName_list.exclude(college_name__exact="N/A")
    collegeNamelist = [{'cname': m.college_name, 'id': m.id} for m in collegeName_list]
    yearlist=[]
    for year in AcademicYear.objects.all():
        yearlist.append(year.academic_year)
    commPartnerlist = CommunityPartner.objects.all()
    commPartnerlist = [m.name for m in commPartnerlist]
    return (collection, sorted(mission_list), sorted(CommTypelist), (CampusPartnerlist), sorted(yearlist),
            sorted(commPartnerlist), (collegeNamelist))


######## export data to Javascript for Household map ################################
def countyData(request):
    Campuspartner = GEOJSON()[3]
    data = GEOJSON()[0]
    # Campuspartner = set(Campuspartner[0])
    # Campuspartner = list(Campuspartner)
    json_data = open('home/static/GEOJSON/USCounties_final.geojson')
    county = json.load(json_data)

    return render(request, 'home/Countymap.html',
                  {'countyData': county, 'collection': GEOJSON()[0],
                   'Missionlist': sorted(GEOJSON()[1]),
                   'CommTypeList': sorted(GEOJSON()[2]),  # pass the array of unique mission areas and community types
                   'Campuspartner': sorted(Campuspartner),
                   'number': len(data['features']),
                   'year': GEOJSON()[4]
                   }
                  )



def GEOJSON2():
    # if (os.path.isfile('home/static/GEOJSON/Project.geojson')):  # check if the GEOJSON is already in the DB
    #     with open('home/static/GEOJSON/Project.geojson') as f:
    #         geojson1 = json.load(f)  # get the GEOJSON
    #     collection = geojson1  # assign it the collection variable to avoid changing the other code
    collection = json.loads(project_geojson)
    Missionlist = []  ## a placeholder array of unique mission areas
    Engagementlist = []
    Academicyearlist = []
    CommunityPartnerlist = []
    CampusPartnerlist = []
    CommunityPartnerTypelist = []
    CollegeNamelist = []

    for e in CommunityType.objects.all():
        if (str(e.community_type) not in CommunityPartnerTypelist):
            CommunityPartnerTypelist.append(str(e.community_type))

    for e in College.objects.all():
        if(str(e.college_name) not in CollegeNamelist):
            if (str(e.college_name) != "N/A"):
                CollegeNamelist.append({'cname':str(e.college_name), 'id':e.id})


    for year in AcademicYear.objects.all():
        Academicyearlist.append(year.academic_year)

    for mission in MissionArea.objects.all():
        Missionlist.append(mission.mission_name)

    for engagement in EngagementType.objects.all():
        Engagementlist.append(engagement.name)

    for communitypart in CommunityPartner.objects.all():
        CommunityPartnerlist.append(communitypart.name)

    for campuspart in CampusPartner.objects.all():
        CampusPartnerlist.append({'name': campuspart.name, 'c_id': campuspart.college_name_id})


    return (collection, sorted(Engagementlist),sorted(Missionlist),sorted(CommunityPartnerlist),
            (CampusPartnerlist), sorted(CommunityPartnerTypelist),sorted(Academicyearlist), (CollegeNamelist))


###Project map export to javascript
def googleprojectdata(request):
    data_definition = DataDefinition.objects.all()
    map_json_data = GEOJSON2()
    Campuspartner = map_json_data[4]
    Communitypartner = map_json_data[3]
    json_data = open('home/static/GEOJSON/ID2.geojson')
    district = json.load(json_data)
    data = map_json_data[0]
    return render(request, 'home/projectMap.html',
                  {'districtData': district, 'collection': map_json_data[0],
                   'number': len(data['features']),
                   'Missionlist': sorted(map_json_data[2]),
                   'CommTypelist': sorted(map_json_data[5]),  # pass the array of unique mission areas and community types
                   'Campuspartner': (Campuspartner),
                   'Communitypartner': sorted(Communitypartner),
                   'EngagementType': sorted(map_json_data[1]),
                   'year': sorted(map_json_data[6]),'data_definition':data_definition,
                   'Collegename': (map_json_data[7])
                   }
                  )


def googleDistrictdata(request):
    data_definition = DataDefinition.objects.all()
    map_json_data = GEOJSON()
    Campuspartner = map_json_data[3]
    data = map_json_data[0]
    json_data = open('home/static/GEOJSON/ID2.geojson')
    district = json.load(json_data)
    return render(request, 'home/legislativeDistrict.html',
                  {'districtData': district, 'collection': map_json_data[0],
                   'Missionlist': sorted(map_json_data[1]),
                   'CommTypeList': sorted(map_json_data[2]),  # pass the array of unique mission areas and community types
                   'Campuspartner': (Campuspartner),
                   'number': len(data['features']),
                   'year': sorted(map_json_data[4]),'data_definition':data_definition,
                   'Collegename': map_json_data[6]
                   }
                  )


def googlepartnerdata(request):
    data_definition = DataDefinition.objects.all()
    map_json_data = GEOJSON()
    Campuspartner = map_json_data[3]
    College = map_json_data[6]
    data = map_json_data[0]
    json_data = open('home/static/GEOJSON/ID2.geojson')
    district = json.load(json_data)
    print('sorted(map_json_data[1]---',sorted(map_json_data[1]))
    return render(request, 'home/communityPartner.html',
                  {'collection': data, 'districtData':district,
                   'Missionlist': sorted(map_json_data[1]),
                   'CommTypeList': sorted(map_json_data[2]),  # pass the array of unique mission areas and community types
                   'Campuspartner': (Campuspartner),
                   'number': len(data['features']),
                   'year': map_json_data[4],'data_definition':data_definition,
                   'College': (College) #k sorted
                   }
                  )


def googlemapdata(request):
    data_definition = DataDefinition.objects.all()
    map_json_data = GEOJSON()
    Campuspartner = map_json_data[3]
    College = map_json_data[6]
    data = map_json_data[0]
    json_data = open('home/static/GEOJSON/ID2.geojson')
    district = json.load(json_data)
    return render(request, 'home/communityPartnerType.html',
                  {'collection': data, 'districtData': district,
                   'Missionlist': sorted(map_json_data[1]),
                   'CommTypeList': sorted(map_json_data[2]),  # pass the array of unique mission areas and community types
                   'Campuspartner': (Campuspartner),
                   'number': len(data['features']),
                   'year': map_json_data[4],'data_definition':data_definition,
                   'College': (College)
                   }
                  )

#TO invite community Partner to the Application
@login_required()
def invitecommunityPartnerUser(request):
    form = CommunityPartnerUserInvite()
    community_partner_user_form = CommunityPartnerUserForm()
    commPartner = []
    for object in CommunityPartner.objects.order_by('name'):
        commPartner.append(object.name)

    if request.method == 'POST':
        form = CommunityPartnerUserInvite(request.POST)
        community_partner_user_form = CommunityPartnerUserForm(request.POST)
        if form.is_valid() and community_partner_user_form.is_valid():
            new_user = form.save(commit=False)
            new_user.is_communitypartner = True
            new_user.is_active = False
            new_user.set_password(raw_password='Default')
            new_user.save()
            communitypartneruser = CommunityPartnerUser(
                community_partner=community_partner_user_form.cleaned_data['community_partner'], user=new_user)
            communitypartneruser.save()
            mail_subject = 'UNO-CPI Community Partner Registration'
            current_site = get_current_site(request)
            message = render_to_string('account/CommunityPartner_Invite_email.html', {
                'user': new_user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)).decode(),
                'token': account_activation_token.make_token(new_user),
            })
            to_email = new_user.email
            email = EmailMessage(mail_subject, message,to=[to_email])
            email.send()
            return render(request, 'home/communityuser_register_done.html', )
    return render(request, 'home/registration/inviteCommunityPartner.html' , {'form':form ,
                                                                              'community_partner_user_form':community_partner_user_form})

def registerCommPartner(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User,pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'home/registration/registerCommunityPartner.html', {'user': user})
    else:
        return render(request, 'home/registration/register_fail.html')



def commPartnerResetPassword(request,pk):
    if request.method == 'POST':
        user_obj = User.objects.get(pk=pk)
        form = SetPasswordForm(user_obj, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return render(request,'home/registration/communityPartnerRegistrationComplete.html')
        else:
            return render(request, 'registration/password_reset_confirm.html', {'form': form, 'validlink': True })
    else:
        form = SetPasswordForm(request.user)
    return render(request, 'registration/password_reset_confirm.html', {'form': form,'validlink':True })


#
# #Issue Address Analysis Chart
# @login_required()
# def issueaddress(request):
#
#     missions =[]
#     for m in  MissionArea.objects.all():
#         res={'id':m.id,'name':m.mission_name,'color': m.mission_color}
#         missions.append(res)
#     missions=sorted(missions,key=lambda i:i['name'],reverse=True)
#     # print("sorted mission list",missions)
#     missionarealist = list()
#     for m in missions:
#         missionarealist.append(m['name'])
#     # print("mission_area1",missionarealist)
#     subcategory = []
#     y=[]
#
#     data_definition = DataDefinition.objects.all()
#     json_data=[]
#     from_json_data=[]
#     to_json_data=[]
#
#     yrs = []
#     yrid=[]
#     acad_years = AcademicYear.objects.all()
#     for e in acad_years:
#         yrs.append(e.academic_year)
#         yrid.append(e.id)
#     max_yr_id = max(yrid)
#     min_yr_id = min(yrid)
#     # max_yr= [p.academic_year for p in (AcademicYear.objects.filter(id=max_yr_id))]
#     max_year=yrs[len(yrs)-1]
#     # min_yr = [p.academic_year for p in (AcademicYear.objects.filter(id=(max_yr_id-1)))]
#     min_year=yrs[len(yrs)-2]
#     # print(" min yaer",min_year," ma yaer ",max_year)
#
#     b = request.GET.get('academic_year', None)
#     ba = request.GET.get('end_academic_year', None)
#
#     if ((b == '' or b == None) and (ba == '' or ba == None)):
#         start = max_yr_id - 1
#         end = max_yr_id
#     elif ((b == '' or b == None) and (ba != '')):
#         start = min_yr_id
#         end = ba
#     elif ((ba == '' or ba == None) and (b != '')):
#         end = max_yr_id
#         start = b
#     else:
#         start = b
#         end = ba
#     start = int(start)
#     end = int(end)
#
#     print(" start ",start)
#     print(" end ", end)
#     from_project_filter = FromProjectFilter(request.GET, queryset=Project.objects.filter())
#     from_start = list(range(min_yr_id, (start + 1)))
#     from_end = list(range(start, (max_yr_id + 1)))
#     print(" from start and from end ", from_start,from_end )
#     to_project_filter = ToProjectFilter(request.GET, queryset=Project.objects.all())
#     to_start = list(range(min_yr_id, (end + 1)))
#     to_end = list(range(end, (max_yr_id + 1)))
#     print(" to start and from end ", to_start, to_end)
#     from_project_count_data = list()
#     to_project_count_data = list()
#     from_subcat_count=list()
#     to_subcat_count=list()
#     subdrill = []
#     from_subcat_counts=[]
#     to_subcat_counts=[]
#
#
#
#     cp=CecPartnerStatus.objects.all()
#     status=[]
#     for c in cp:
#         res={'id':c.id,'status':c.name}
#         status.append(res)
#         if c.name=='Current':
#             Current=c.id
#         if c.name=='Former':
#             Former=c.id
#         if c.name=='Never':
#             Never=c.id
#
#
#
#
#     #set cec partner flag on template choices field
#     weitz_cec_part = request.GET.get('weitz_cec_part', None)
#     # cec_part_init_selection = "All"
#     if weitz_cec_part is None or weitz_cec_part == "All" or weitz_cec_part == '':
#             ceccommunityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all())
#             ceccampuspartners = [d.id for d in (CampusPartner.objects.all())]
#     cec_part_choices = CecPartChoiceForm(initial={'cec_choice': weitz_cec_part})
#
#     # print("weitz_cec_part",weitz_cec_part)
#     if weitz_cec_part == "All":
#         ceccommunityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all())
#         ceccampuspartners = [d.id for d in (CampusPartner.objects.all())]
#         # print(" all ",ceccommunityPartners,ceccampuspartners )
#     if weitz_cec_part == "CURR_CAMP" :
#         ceccampuspartners= [d.id for d in (CampusPartner.objects.filter(cec_partner_status=Current))]
#         ceccommunityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all())
#         # print(" cec partner with current ",ceccampuspartners)
#     if weitz_cec_part == "FORMER_CAMP" :
#         ceccampuspartners = [d.id for d in (CampusPartner.objects.filter(cec_partner_status=Former))]
#         ceccommunityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all())
#         # print(" cec partner with former ", ceccampuspartners)
#     if weitz_cec_part == "CURR_COMM" :
#         ceccommunityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.filter(
#             cec_partner_status=Current))
#         ceccampuspartners = [d.id for d in (CampusPartner.objects.all())]
#         # print(" cec comm partner with current ", ceccommunityPartners)
#     if weitz_cec_part == "FORMER_COMM" :
#         ceccommunityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.filter(
#             cec_partner_status=Former))
#         ceccampuspartners = [d.id for d in (CampusPartner.objects.all())]
#         # print(" cec comm partner with former ", ceccommunityPartners)
#
#
#
#     ceccampus_project_filter = ProjectCampusFilter(request.GET, queryset=ProjectCampusPartner.objects.filter(
#         campus_partner_id__in=ceccampuspartners))
#     cec_campus_project_filter_ids = [project.project_name_id for project in ceccampus_project_filter.qs]
#
#     cec_community_filtered_ids = [community.id for community in ceccommunityPartners.qs]
#     cec_comm_filter = ProjectCommunityFilter(request.GET, queryset=ProjectCommunityPartner.objects.filter(
#         community_partner_id__in=cec_community_filtered_ids))
#     cec_comm_proj_filtered_ids = [project.project_name_id for project in cec_comm_filter.qs]
#
#     college_filter = CampusFilter(request.GET, queryset=CampusPartner.objects.all())
#     college_filtered_ids = [campus.id for campus in college_filter.qs]
#
#     campus_project_filter = ProjectCampusFilter(request.GET, queryset=ProjectCampusPartner.objects.filter(
#         campus_partner_id__in=college_filtered_ids))
#     campus_project_filter_ids = [project.project_name_id for project in campus_project_filter.qs]
#
#     campus_filter = ProjectCampusFilter(request.GET, queryset=ProjectCampusPartner.objects.all())
#     campus_filtered_ids = [project.project_name_id for project in campus_filter.qs]
#     campus_filtered_ids=list(set(campus_filtered_ids).intersection(cec_campus_project_filter_ids))
#
#     project_filter = ProjectFilter(request.GET, queryset=Project.objects.all())
#     projects = Project.objects.all()
#
#     engagement_type = request.GET.get('engagement_type', None)
#     if engagement_type is None or engagement_type == "All" or engagement_type == '':
#         projects = Project.objects.all()
#     else:
#         projects = Project.objects.filter(engagement_type=engagement_type)
#
#     project_filtered_ids = [project.id for project in projects]
#
#
#
#     legislative_choices = []
#     legislative_search = ''
#     legislative_selection = request.GET.get('legislative_value', None)
#
#     if legislative_selection is None:
#         legislative_selection = 'All'
#
#     # legislative_choices.append('All')
#     for i in range(1, 50):
#         legistalive_val = 'Legislative District ' + str(i)
#         legislative_choices.append(legistalive_val)
#
#     if legislative_selection is not None and legislative_selection != 'All':
#         legislative_search = legislative_selection.split(" ")[2]
#
#     if legislative_selection is None or legislative_selection == "All" or legislative_selection == '':
#         communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all())
#         # project_filter = ProjectFilter(request.GET, queryset=Project.objects.all())
#     else:
#         # print(" checking legislative district, ",legislative_search)
#         communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.filter(
#             legislative_district=legislative_search))
#         # print(" count",communityPartners.__sizeof__())
#         # project_filter = ProjectFilter(request.GET,
#         #                                queryset=Project.objects.filter(legislative_district=legislative_search))
#
#     community_filtered_ids = [community.id for community in communityPartners.qs]
#     # print(" no. of partner",len(community_filtered_ids))
#
#
#     comm_filter = ProjectCommunityFilter(request.GET, queryset=ProjectCommunityPartner.objects.filter(
#         community_partner_id__in=community_filtered_ids))
#     comm_proj_filtered_ids = [project.project_name_id for project in comm_filter.qs]
#
#     comm_proj_filtered_ids=list(set(comm_proj_filtered_ids).intersection(cec_comm_proj_filtered_ids))
#
#
#     proj1_ids = list(set(campus_filtered_ids).intersection(project_filtered_ids))
#     proj2_ids = list(set(campus_project_filter_ids).intersection(proj1_ids))
#     project_ids = list(set(proj2_ids).intersection(comm_proj_filtered_ids))
#
#     a = request.GET.get('engagement_type', None)
#     c = request.GET.get('campus_partner', None)
#     d = request.GET.get('college_name', None)
#     # b = request.GET.get('academic_year', None)
#     # ba = request.GET.get('end_academic_year', None)
#     e = request.GET.get('community_type', None)
#     f = request.GET.get('weitz_cec_part', None)
#
#     if a is None or a == "All" or a == '':
#         if b is None or b == "All" or b == '':
#             if ba is None or ba == "All" or ba == '':
#                 if c is None or c == "All" or c == '':
#                     if d is None or d == "All" or d == '':
#                         if f is None or f == "All" or f == '':
#                             if e is None or e == "All" or e == '':
#                                 project_ids = project_filtered_ids
#
#     secondary_y_axis=[]
#     Yaxis=[]
#     for m in missions:
#             y=[]
#             subcategory=[]
#             for s in MissionSubCategory.objects.filter(secondary_mission_area_id=m["id"]).values("sub_category_id"):
#                 if (s["sub_category_id"] not in y):
#                     y.append(s["sub_category_id"])
#             # print(" sub category ids for mission 1", y)
#             for sc in SubCategory.objects.filter(id__in=y):
#                 res = {'id': sc.id, 'name': sc.sub_category}
#                 subcategory.append(res)
#             subcategory = sorted(subcategory, key=lambda i: i['name'],reverse=True)
#             subcategorylist = []
#             for sc in subcategory:
#                 subcategorylist.append(sc['name'])
#             mid = next((index for (index, d) in enumerate(missions) if d["name"] == m['name']),None)
#             if f is None or f == "All" or f == '':
#                 if e is None or e == "All" or e == '':
#                     project_ids = proj2_ids
#             project_count1 = Project.objects.filter(academic_year__in=from_start).filter(end_academic_year=None).filter(id__in=project_ids)
#             project_count2 = Project.objects.filter(academic_year__in=from_start).filter(end_academic_year__in=from_end).filter(id__in=project_ids)
#             project_count3 = project_count1 | project_count2
#             from_project_ids = []
#             for c in project_count3:
#                 from_project_ids.append (c.id)
#             print("from_project_ids ",from_project_ids)
#             from_project_count_ids = ProjectMission.objects.filter(mission=m['id']).filter(mission_type='Primary').filter(project_name_id__in=from_project_ids)
#             fromids=[]
#             for c in from_project_count_ids:
#                 # if c.project_name_id not in fromids:
#                    fromids.append(c.project_name_id)
#             from_project_count = len(fromids)
#             print("from_project_count_ids ", from_project_count_ids)
#
#             project_count4 = Project.objects.filter(academic_year__in=to_start).filter(end_academic_year=None).filter(id__in=project_ids)
#             project_count5 = Project.objects.filter(academic_year__in=to_start).filter(end_academic_year__in=to_end).filter(id__in=project_ids)
#             project_count6 = project_count4 | project_count5
#             to_project_ids = []
#             for c in project_count6:
#                 to_project_ids.append (c.id)
#             print("to_project_ids",to_project_ids)
#             to_project_count_ids = ProjectMission.objects.filter(mission=m['id']).filter(mission_type='Primary').filter(project_name_id__in=to_project_ids)
#             toids=[]
#             for c in to_project_count_ids:
#                 # if c.project_name_id not in fromids:
#                 toids.append(c.project_name_id)
#             to_project_count=len(toids)
#                 # ProjectMission.objects.filter(mission=m['id']).filter(mission_type='Primary').filter(
#                 # project_name_id__in=to_project_ids).count()
#             print("to_project_count_ids ", to_project_count_ids)
#             x1=[pm.project_name_id for pm in from_project_count_ids]
#             x=[]
#             for id in x1:
#                 if id not in x:
#                     x.append(id)
#             y1 = [pm.project_name_id for pm in to_project_count_ids]
#             y=[]
#             for id in y1:
#                 if id not in y:
#                     y.append(id)
#             print(" from_project_count_ids ids",x)
#             print(" to_project_count_ids  ids", y)
#
#             drilldata=[]
#             if request.user.is_superuser:
#                 for sc in subcategory:
#                     sid = next((index for (index, d) in enumerate(subcategory) if d["name"] == sc['name']), None)
#                     from_project_mission_sub_ids=ProjectSubCategory.objects.filter(project_name_id__in=x).filter(sub_category_id=sc['id']).count()
#                     to_project_mission_sub_ids = ProjectSubCategory.objects.filter(project_name_id__in=y).filter(
#                         sub_category_id=sc['id']).count()
#                     from_subcat_counts.append(from_project_mission_sub_ids)
#                     to_subcat_counts.append(to_project_mission_sub_ids)
#                     if(from_project_mission_sub_ids>to_project_mission_sub_ids):
#                         drill = {"name":sc['name'],"x": from_project_mission_sub_ids,
#                              "x2": to_project_mission_sub_ids, "y": sid ,"color":"red"}
#                     else:
#                         drill = {"name":sc['name'],"x": from_project_mission_sub_ids,
#                                  "x2": to_project_mission_sub_ids, "y":sid ,"color":"turquoise"}
#                     drilldata.append(drill)
#                 drilled = {"type":"xrange","name": m['name'], "id": m['name'], "yAxis": mid+1 ,"data": drilldata}
#                 subdrill.append(drilled)
#             from_project_count_data.append(from_project_count)
#             to_project_count_data.append(to_project_count)
#             if(from_project_count > to_project_count):
#                 res = {"name":m['name'],"x": from_project_count, "x2": to_project_count, "y":mid, "drilldown":m['name'],"color":"red"}
#             else:
#                 res = {"name": m['name'], "x": from_project_count, "x2": to_project_count, "y": mid ,
#                        "drilldown": m['name'], "color": "turquoise"}
#             resfrom = {"x": from_project_count,"y":mid,"drilldown":m['name']}
#             resto = {"x": to_project_count,"y":mid,"drilldown":m['name']}
#
#             json_data.append(res)
#             from_json_data.append(resfrom)
#             to_json_data.append(resto)
#             # print(" mid value ",mid," lemngt ",len(missions))
#             yaxis={
#             'id':mid+1,
#             'type': 'category',
#             # 'min':1,
#             # 'max':len(subcategorylist)-1,
#             # 'tickInterval':1.0,
#             'title': {'text': '',
#                       'style': {'fontFamily':'Arial Narrow','fontWeight': 'bold', 'color': 'black', 'fontSize': '15px'}},
#             'labels': {'style': {'color': 'black', 'fontSize': '13px'}},
#             'categories': subcategorylist}
#             if(mid== len(missions)-1):
#                 yaxis = {
#                     'id': mid + 1,
#                     'type': 'category',
#                     # 'min':1,
#                     # 'max':len(subcategorylist)-1,
#                     # 'tickInterval':1.0,
#                     'title': {'text': 'Focus Area',
#                               'style': {'fontFamily':'Arial Narrow','fontWeight': 'bold', 'color': 'black', 'fontSize': '15px'}},
#                     'labels': {'style': {'color': 'black', 'fontSize': '13px'}},
#                     'categories': subcategorylist}
#             secondary_y_axis.append(yaxis)
#
#     primary_axis={  # Primary Axis for Mission Areas
#                 'id':0,
#                 'type': 'category',
#                 'title': {'text': '',
#                           'style': {'fontWeight': 'bold', 'color': 'black', 'fontSize': '15px'}},
#                 'labels': {'style': {'color': 'black', 'fontSize': '13px'}},
#                 'categories': missionarealist,
#             }
#     Yaxis.append(primary_axis)
#     for axis in secondary_y_axis:
#         if(axis not in Yaxis):
#             Yaxis.append(axis)
#
#     # print(" yxis value in category ",Yaxis)
#     Academic_Year = {
#         'name': 'Analysis Start Year',
#         'data': from_json_data,
#         'color': 'teal',
#         'type': 'scatter'}
#     End_Academic_Year = {
#         'name': 'Analysis Comparison (End) Year',
#         'data': to_json_data,
#         'color': 'blue',
#         'type': 'scatter'}
#     project_over_academic_years = {
#         'name': 'No of Projects ',
#         'data': json_data,
#         'type':'xrange',
#         'showInLegend':False,
#         'marker':{
#             'enabled':True
#         }
#         # 'color': 'turquoise'
#                 }
#
#
#     dumbellchart = {
#
#        'title': '',
#         'xAxis': {'allowDecimals': False, 'title': {'text': 'Projects ',
#                                                     'style': {'fontFamily':'Arial Narrow','fontWeight': 'bold', 'color': 'black',
#                                                               'fontSize': '15px'}}},
#         'yAxis':Yaxis,
#         'plotOptions': {
#             'xrange': {
#                 'pointWidth': 4,
#                 'dataLabels': {
#                     'enabled': True,
#                     'inside':False,
#                     'style': {
#                         'fontSize': '6px'
#                     },
#                     'marker':{
#                     'linewidth':'4px',
#                     }
#
#                 },'colorByPoint': False,
#                 'tooltip': {
#                     'style': {'fontFamily': 'Arial Narrow'},
#                     'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
#                     'pointFormat': '<span style="color:{point.color}">{point.name}</span><br> FromYearProjectCount:{point.x}<br>ToYearProjectCount:{point.x2}<br>'
#                 }
#             },
#
#             'scatter': {
#                 'marker': {
#                     'radius': 6,
#                     'symbol': 'circle'
#                 }
#             }
#         },
#         'tooltip': {
#             'style': {'fontFamily': 'Arial Narrow'},
#         'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
#         'pointFormat': '<span style="color:{point.color}">{point.name}</span><br> ProjectCount:{point.x}<span></span> '
#                  },
#         'legend': {
#             'layout': 'horizontal',
#             'align': 'right',
#             'verticalAlign': 'top',
#             'x': -10,
#             'y': 10,
#             'borderWidth': 1,
#             'backgroundColor': '#FFFFFF',
#             'shadow': 'true',
#             'itemStyle': {'fontFamily': 'Arial Narrow'},
#             'backgroundColor': '#FFFFFF', "shadow": 'true'
#         },
#
#
#         'series': [project_over_academic_years, Academic_Year, End_Academic_Year],
#         'drilldown':{
#             'series': subdrill,
#         }
#
#     }
#     college_value = request.GET.get('college_name', None)
#     if college_value is None or college_value == "All" or college_value == '':
#         campus_filter_qs = CampusPartner.objects.all()
#     else:
#         campus_filter_qs = CampusPartner.objects.filter(college_name_id=college_value)
#     campus_filter = [{'name': m.name, 'id': m.id} for m in campus_filter_qs]
#
#     campus_id = request.GET.get('campus_partner')
#     if campus_id == "All":
#         campus_id = -1
#     if (campus_id is None or campus_id == ''):
#         campus_id = 0
#     else:
#         campus_id = int(campus_id)
#
#     dump = json.dumps(dumbellchart)
#     return render(request, 'charts/issueaddressanalysis.html',
#                       {'dumbellchart': dump, 'from_project_filter': from_project_filter,'project_filter':project_filter,
#                        'to_project_filter': to_project_filter,
#                        'data_definition': data_definition,
#                        'campus_filter': campus_filter, 'communityPartners': communityPartners,
#                        'college_filter': college_filter, 'campus_id': campus_id,'legislative_choices':legislative_choices, 'legislative_value':legislative_selection,
#                         'max_year':max_year,'min_year':min_year,'cec_part_choices': cec_part_choices})
#
#



##### Get the Chart JSONS for network Analysis ##############
def chartjsons():
    # with open('home/static/GEOJSON/ID2.geojson') as f:
    #     geojson = json.load(f)
    #
    # district = geojson["features"]
    # campus_partner=open('home/static/charts_json/campus_partners.json')
    campus_partner_json=json.loads(charts_campuses)
    # campus_partner_json = json.load(campus_partner)#local
    # community_partner = open('home/static/charts_json/community_partners.json')
    community_partner_json = json.loads(charts_communities)
    # community_partner_json = json.load(community_partner)#local
    # mission_subcategories = open('home/static/charts_json/mission_subcategories.json')
    mission_subcategories_json = json.loads(charts_missions)
    # mission_subcategories_json = json.load(mission_subcategories)#local
    # projects =open ('home/static/charts_json/projects.json')
    projects_json = json.loads(charts_projects)
    # projects_json = json.load(projects)#local
    return (campus_partner_json,community_partner_json,mission_subcategories_json,projects_json)



###Network Analysis Chart
@login_required()
def networkanalysis(request):
    data_definition = DataDefinition.objects.all()
    Campuspartner = GEOJSON2()[4]
    Communitypartner = GEOJSON2()[3]
    data = GEOJSON2()[0]
    campus_partner_json=chartjsons()[0]
    community_partner_json=chartjsons()[1]
    mission_subcategories_json=chartjsons()[2]
    projects_json=chartjsons()[3]
    # print(" project json ",projects_json)
    yrs = []
    acad_years = AcademicYear.objects.all()
    for e in acad_years:
        res={'id':e.id,'year':e.academic_year}
        yrs.append(res)
    # max_yr_id = max(yrs)
    acyear = sorted(yrs, key=lambda i: i['year'], reverse=True)

    year_ids=[]
    year_names=[]
    for e in acyear:
        year_ids.append(e['id'])
        year_names.append(e['year'])
    # print(year_ids[1])
    # print(year_names[1])
    # max_yr = [p.academic_year for p in (AcademicYear.objects.filter(id = (max_yr_id-1)))]
    max_yr_id=year_ids[1]
    max_year = year_names[1]
    print(" ma year ",max_year)
    print(" ma year ", max_yr_id)

    missionList = []
    for m in MissionArea.objects.all():
        res = {'id': m.id, 'name': m.mission_name, 'color': m.mission_color}
        missionList.append(res)
    missionList = sorted(missionList, key=lambda i: i['name'])

    # community_filter = ProjectCommunityFilter(request.GET, queryset=ProjectCommunityPartner.objects.all())

    mission = ProjectMissionFilter(request.GET, queryset=ProjectMission.objects.filter(mission_type='Primary'))
    project_filter = ProjectFilter(request.GET, queryset=Project.objects.order_by('academic_year'))
    communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all())
    college_filter = CampusFilter(request.GET, queryset=CampusPartner.objects.all())
    # campus_partner_filter = ProjectCampusFilter(request.GET, queryset=ProjectCampusPartner.objects.all())
    campus_filter = ProjectCampusFilter(request.GET, queryset=ProjectCampusPartner.objects.all())
    campus_filtered_ids = [project.project_name_id for project in campus_filter.qs]

    community_filter_qs = CommunityPartner.objects.all()
    community_filter = [{'name': m.name, 'id': m.id} for m in community_filter_qs]

    cec_part_selection = request.GET.get('weitz_cec_part', None)
    cec_part_init_selection = "All"
    cec_part_choices = CecPartChoiceForm(initial={'cec_choice': cec_part_selection})
    # print("campus_partner_filter",campus_filter)
    k12_selection = request.GET.get('k12_flag', None)
    k12_init_selection = "All"
    if k12_selection is None:
        k12_selection = k12_init_selection

    k12_choices = K12ChoiceForm(initial={'k12_choice': k12_selection})

    if k12_selection == 'Yes':
        project_filter = ProjectFilter(request.GET, queryset=Project.objects.filter(k12_flag=True))

    elif k12_selection == 'No':
        project_filter = ProjectFilter(request.GET, queryset=Project.objects.filter(k12_flag=False))

    # else:
    #     project_filter = ProjectFilter(request.GET, queryset=Project.objects.all())

    college_value = request.GET.get('college_name', None)
    if college_value is None or college_value == "All" or college_value == '':
        campus_filter_qs = CampusPartner.objects.all()
    else:
        campus_filter_qs = CampusPartner.objects.filter(college_name_id=college_value)
    campus_filter = [{'name': m.name, 'id': m.id} for m in campus_filter_qs]

    campus_id = request.GET.get('campus_partner')
    if campus_id == "All":
        campus_id = -1
    if (campus_id is None or campus_id == ''):
        campus_id = 0
    else:
        campus_id = int(campus_id)

    legislative_choices = []
    legislative_search = ''
    legislative_selection = request.GET.get('legislative_value', None)

    if legislative_selection is None:
        legislative_selection = 'All'

    # legislative_choices.append('All')
    for i in range(1, 50):
        legistalive_val = 'Legislative District ' + str(i)
        legislative_choices.append(legistalive_val)

    if legislative_selection is not None and legislative_selection != 'All':
        legislative_search = legislative_selection.split(" ")[2]

    if legislative_selection is None or legislative_selection == "All" or legislative_selection == '':
        communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all())
        # project_filter = ProjectFilter(request.GET, queryset=Project.objects.all())
    else:
        communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.filter(
            legislative_district=legislative_search))
        # project_filter = ProjectFilter(request.GET,
        #                                queryset=Project.objects.filter(legislative_district=legislative_search))





    return render(request, 'charts/network.html',
                  { 'Missionlist': missionList,'data_definition':data_definition,'Collegenames': (GEOJSON2()[7]),
                   'campus_partner_json':campus_partner_json,'community_partner_json':community_partner_json,'max_yr_id':max_yr_id,'max_year':max_year,
                   'mission_subcategories_json':mission_subcategories_json,'projects_json':projects_json,
                    'project_filter': project_filter,'campus_filter': campus_filter,'missions': mission,'communityPartners': communityPartners,
                    'college_filter': college_filter,'k12_choices': k12_choices,'campus_id': campus_id,
                    'legislative_choices': legislative_choices, 'legislative_value': legislative_selection,'cec_part_choices': cec_part_choices,'community_filter':community_filter} )




@login_required()
###Focus Area Analysis Chart
def issueaddress(request):
    data_definition = DataDefinition.objects.all()
    Campuspartner = GEOJSON2()[4]
    Communitypartner = GEOJSON2()[3]
    data = GEOJSON2()[0]
    campus_partner_json=chartjsons()[0]
    community_partner_json=chartjsons()[1]
    mission_subcategories_json=chartjsons()[2]
    projects_json=chartjsons()[3]
    # print(" project json ",projects_json)
    yrs = []
    acad_years = AcademicYear.objects.all()
    for e in acad_years:
        res={'id':e.id,'year':e.academic_year}
        yrs.append(res)
    # max_yr_id = max(yrs)
    acyear = sorted(yrs, key=lambda i: i['year'], reverse=True)

    year_ids=[]
    year_names=[]
    for e in acyear:
        year_ids.append(e['id'])
        year_names.append(e['year'])
    # print(year_ids[1])
    # print(year_names[1])
    # max_yr = [p.academic_year for p in (AcademicYear.objects.filter(id = (max_yr_id-1)))]
    max_yr_id=year_ids[0]
    min_yr_id=year_ids[1]
    max_year = year_names[0]
    min_year=year_names[1]
    print(" max year ",max_year)
    print(" min year ", min_year)

    MissionObject = json.loads(charts_missions)
    user_role = request.user.is_superuser
    # print("super user ",user_role)

    missionList = []
    for m in MissionObject:
        res = {'id': m['mission_area_id'], 'name': m['mission_area_name'], 'color': m['mission_color']}
        missionList.append(res)
    missionList = sorted(missionList, key=lambda i: i['name'],reverse=True)


    # community_filter = ProjectCommunityFilter(request.GET, queryset=ProjectCommunityPartner.objects.all())

    mission = ProjectMissionFilter(request.GET, queryset=ProjectMission.objects.filter(mission_type='Primary'))
    project_filter = ProjectFilter(request.GET, queryset=Project.objects.order_by('academic_year'))
    from_project_filter = FromProjectFilter(request.GET, queryset=Project.objects.order_by('academic_year'))
    to_project_filter = ToProjectFilter(request.GET, queryset=Project.objects.order_by('academic_year'))
    communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all())
    college_filter = CampusFilter(request.GET, queryset=CampusPartner.objects.all())
    # campus_partner_filter = ProjectCampusFilter(request.GET, queryset=ProjectCampusPartner.objects.all())
    campus_filter = ProjectCampusFilter(request.GET, queryset=ProjectCampusPartner.objects.all())
    campus_filtered_ids = [project.project_name_id for project in campus_filter.qs]

    community_filter_qs = CommunityPartner.objects.all()
    community_filter = [{'name': m.name, 'id': m.id} for m in community_filter_qs]

    cec_part_selection = request.GET.get('weitz_cec_part', None)
    cec_part_init_selection = "All"
    cec_part_choices = CecPartChoiceForm(initial={'cec_choice': cec_part_selection})
    # print("campus_partner_filter",campus_filter)
    k12_selection = request.GET.get('k12_flag', None)
    k12_init_selection = "All"
    if k12_selection is None:
        k12_selection = k12_init_selection

    k12_choices = K12ChoiceForm(initial={'k12_choice': k12_selection})

    if k12_selection == 'Yes':
        project_filter = ProjectFilter(request.GET, queryset=Project.objects.filter(k12_flag=True))

    elif k12_selection == 'No':
        project_filter = ProjectFilter(request.GET, queryset=Project.objects.filter(k12_flag=False))

    # else:
    #     project_filter = ProjectFilter(request.GET, queryset=Project.objects.all())

    college_value = request.GET.get('college_name', None)
    if college_value is None or college_value == "All" or college_value == '':
        campus_filter_qs = CampusPartner.objects.all()
    else:
        campus_filter_qs = CampusPartner.objects.filter(college_name_id=college_value)
    campus_filter = [{'name': m.name, 'id': m.id} for m in campus_filter_qs]

    campus_id = request.GET.get('campus_partner')
    if campus_id == "All":
        campus_id = -1
    if (campus_id is None or campus_id == ''):
        campus_id = 0
    else:
        campus_id = int(campus_id)

    legislative_choices = []
    legislative_search = ''
    legislative_selection = request.GET.get('legislative_value', None)

    if legislative_selection is None:
        legislative_selection = 'All'

    # legislative_choices.append('All')
    for i in range(1, 50):
        legistalive_val = 'Legislative District ' + str(i)
        legislative_choices.append(legistalive_val)

    if legislative_selection is not None and legislative_selection != 'All':
        legislative_search = legislative_selection.split(" ")[2]

    if legislative_selection is None or legislative_selection == "All" or legislative_selection == '':
        communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.all())
        # project_filter = ProjectFilter(request.GET, queryset=Project.objects.all())
    else:
        communityPartners = communityPartnerFilter(request.GET, queryset=CommunityPartner.objects.filter(
            legislative_district=legislative_search))
        # project_filter = ProjectFilter(request.GET,
        #                                queryset=Project.objects.filter(legislative_district=legislative_search))





    return render(request, 'charts/focusareaanalaysis.html',
                  { 'Missionlist': missionList,'data_definition':data_definition,'Collegenames': (GEOJSON2()[7]),
                   'campus_partner_json':campus_partner_json,'community_partner_json':community_partner_json,'max_yr_id':max_yr_id,'min_yr_id':min_yr_id,
                   'mission_subcategories_json':mission_subcategories_json,'projects_json':projects_json,
                    'to_project_filter': to_project_filter,'from_project_filter': from_project_filter,'project_filter': project_filter,'campus_filter': campus_filter,'missions': mission,'communityPartners': communityPartners,
                    'communityPartners': communityPartners,'college_filter': college_filter,'k12_choices': k12_choices,'campus_id': campus_id,
                    'legislative_choices': legislative_choices, 'legislative_value': legislative_selection,'cec_part_choices': cec_part_choices,'community_filter':community_filter,'max_year':max_year,'min_year':min_year,"user_role":user_role} )

