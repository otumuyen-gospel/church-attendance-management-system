
from django.shortcuts import render
import pandas as pd
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from urllib.parse import urlparse
from rest_framework.permissions import IsAuthenticated, IsAdminUser,AllowAny
from django_filters import AllValuesFilter, DateTimeFilter, NumberFilter
from rest_framework.exceptions import PermissionDenied
from django.http import HttpResponse
from rest_framework.views import APIView
from django.contrib.auth.models import Permission
from person.models import Person
from contact.models import Contact
from household.models import HouseHold
from user.models import User
from ministries.models import Ministries
from membership.models import Membership
from attendance.models import Attendance
from services.models import Services
from leadership.models import Leadership
from role.models import Role
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime

# Create your views here.
class Analytics(APIView):
    permission_classes = [IsAuthenticated] #only authenticated users can access
    name = 'Analytics'
    def get(self,request):
        try:
            # Take statistics of menbers in the various ministries
            persons = Person.objects.values() 
            contacts = Contact.objects.values()
            household = HouseHold.objects.values()
            users = User.objects.values()
            leaderships = Leadership.objects.values()
            #only todays's attendance
            today = timezone.localtime(timezone.now()).date()
            attendance = Attendance.objects.filter(checkInTimestamp__date=today).values()
            df = pd.merge(pd.DataFrame.from_records(persons), 
                          pd.DataFrame.from_records(contacts), left_on='id', 
                          right_on='personId_id', how='outer')

            men = df[(df['gender'] == 'M') & ((df['marital_status'] == 'MARRIED') | 
                                              (df['marital_status'] == 'SEPARATED'))].shape[0]
            women = df[(df['gender'] == 'F') & ((df['marital_status'] == 'MARRIED') | 
                                              (df['marital_status'] == 'SEPARATED'))].shape[0]
            youths = 0
            teens = 0
            children = 0
            for row in df.itertuples(index=False):
                youths  += 1 if (row.marital_status == 'SINGLE' and self.age(row.dob) > 19) else 0
                teens  += 1 if (row.marital_status == 'SINGLE' and (self.age(row.dob) > 12 and self.age(row.dob) < 19)) else 0
                children  += 1 if (row.marital_status == 'SINGLE' and self.age(row.dob) < 12) else 0
            total_users = len(users)
            families = len(household)
            total_persons = df.shape[0]
            statistics = {
                "men": men,
                "women": women,
                "youths": youths,
                "teens": teens,
                "children": children,
                "total_users": total_users,
                "families": families,
                "total_persons": total_persons,
            }

            membership = df['membershipId_id'].value_counts()
            membership_status = {}
            for member in membership.items():
                membership_status[Membership.objects.get(id=member[0]).status]= member[1]

            ethnicity = df['ethnicity'].value_counts()
            ethnic_groups = {}
            for ethnic in ethnicity.items():
                ethnic_groups[ethnic[0]] = ethnic[1]

            df3 = pd.DataFrame.from_records(leaderships)
            leadership = df3['roleId_id'].value_counts()
            leadership_status = {}
            for leader in leadership.items():
                leadership_status[Role.objects.get(id=leader[0]).name]= leader[1]

            # Annual Membership Growth for the last 5 years
            five_years_age = timezone.now() - timedelta(days=5*365)
            df['entranceDate'] = pd.to_datetime(df['entranceDate'])
            filtered_df = df[df['entranceDate'] >= five_years_age]
            annual_membership_statistics = filtered_df.groupby(filtered_df['entranceDate'].dt.year).size().to_dict()

            # Monthly Membership Growth for the current  year
            currentYear = timezone.now().year
            df['entranceDate'] = pd.to_datetime(df['entranceDate'])
            filtered_df = df[df['entranceDate'].dt.year == currentYear]
            key_mapping = {1:'January', 2:'February', 3:'March',4:'April',5:'May', 6:'June',
                           7:'July', 8:'August',9:'September', 10:'October',11:'November',
                           12:'December'}
            monthly_membership_statistics = filtered_df.groupby(filtered_df['entranceDate'].dt.month).size().to_dict()
            current_year_monthly_membership_statistics = {key_mapping.get(k,k): v for k, v in monthly_membership_statistics.items()}

            #membership attendance merge
            today_attendance = {}
            if attendance:
                df4 = pd.merge(pd.DataFrame.from_records(persons), 
                          pd.DataFrame.from_records(attendance), left_on='id', 
                          right_on='personId_id', how='inner')
                if not df4.empty:
                    memberships = Membership.objects.values('id','status')
                    memberships = {m['id']:m['status'] for m in memberships}
                    today_attendance = df4.groupby('membershipId_id').size().to_dict()
                    today_attendance = {memberships.get(k,k): v for k, v in today_attendance.items()}

            return Response({ "statistics": statistics, "membership_status": membership_status, "ethnic_groups": ethnic_groups, 
                             "leadership_status": leadership_status, "annual_growth": annual_membership_statistics, 
                             "current_year_monthly_growth": current_year_monthly_membership_statistics, "today_attendance": today_attendance }, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    def age(self, birthdate):
        today = timezone.now().date()
        dob = timezone.datetime.strptime(str(birthdate),'%Y-%m-%d')
        age = today.year - dob.year
        if (today.month, today.day) < (dob.month, dob.day):
            age -= 1 #is not yet birthday so subtract 1 from age
        return age
   
    