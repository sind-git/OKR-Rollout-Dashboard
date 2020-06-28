import datetime as dt
import os
import string

import numpy as np
import pandas as pd
from django.shortcuts import render

from .models import Functions
# from rest_framework.views import APIView
# from rest_framework.response import Response

# Create your views here.


input_directory = r"C:\Users\91810\OneDrive\Python Project\OKR"

# Read from Ally Exports
def read_excel(input_directory, filename):
    data = pd.read_excel(os.path.join(input_directory,filename))
    #logger.info("Read file {file}".format(file=filename))
    return data

def find_unique(df,col):
    data = df[col].nunique()
    return data


#def groupby_counts(df,col):
#    data = pd.value_counts(df[col]).rename_axis(col).reset_index(name="Counts")
#    return data

def totalsum(df,col,value):
    no_match = np.sum(df[col] != value)
    match = np.sum(df[col] == value)
    data = [no_match, match]
    return data

objectives_dump = read_excel(input_directory,"objectives_dump_python.xlsx")
insights_dump = read_excel(input_directory, "insights_dump_python.xlsx")
user_mapping = read_excel(input_directory,"user_mapping_dump_python.xlsx")


# Create Merge Tables
objectives_user_df = pd.merge(objectives_dump,user_mapping,left_on="Owner",right_on="Name",how="outer")
objectives_user_insights_df = pd.merge(objectives_user_df,insights_dump,left_on="Name",right_on="Name",how="outer")
user_insights_df = pd.merge(user_mapping, insights_dump,left_on="Name",right_on="Name",how="outer")


def setup_chartdetails(input_function):
#        global objectives_user_df, objectives_user_insights_df, user_insights_df

        print ("Input function inside setup_chartdetails ", input_function)
        objectives_user_df = pd.merge(objectives_dump, user_mapping, left_on="Owner", right_on="Name", how="outer")
        objectives_user_insights_df = pd.merge(objectives_user_df, insights_dump, left_on="Name", right_on="Name",
                                               how="outer")
        user_insights_df = pd.merge(user_mapping, insights_dump, left_on="Name", right_on="Name", how="outer")

        #to resolve "ValueError('cannot insert level_0, already exists')" error
      #  objectives_user_df = objectives_user_df.reset_index(drop=True)
      #  objectives_user_insights_df = objectives_user_insights_df.reset_index(drop=True)
      #  user_insights_df = user_insights_df.reset_index(drop=True)

    #    user_insights_df = user_insights_df[user_insights_df["FUNCTION"] == input_function].reset_index()
    #    objectives_user_insights_df = objectives_user_insights_df[objectives_user_insights_df["FUNCTION"] == input_function].reset_index()

        if input_function != "ALL":
               user_insights_df = user_insights_df[user_insights_df["FUNCTION"] == input_function]
               objectives_user_insights_df = objectives_user_insights_df[objectives_user_insights_df["FUNCTION"] == input_function]


        #1 Total OKRs
        total_okrs = find_unique(objectives_user_insights_df, "Id_x")

        #2 OKRs checked-in
        okr_checkedin = (total_okrs - np.sum(objectives_user_insights_df["Status_x"] == "Not Started"))

        #3 OKRs Closed
        okr_closed = (np.sum(objectives_user_insights_df["Status_x"] == "Closed"))

        #4 Avg. Progress
        avg_progress = round((np.sum(objectives_user_insights_df["Progress %"]) / total_okrs),2)

        #5 OKRs with KPIs
        okr_with_kpi = (total_okrs - (np.sum(objectives_user_insights_df["Metric Name"] == "% Completed")))

        #6 OKRs not updated in the last 2 weeks
        objectives_user_insights_df["Last Updated"] = pd.to_datetime(objectives_user_insights_df["Last Updated"]).dt.strftime("%Y-%m-%d")
        objectives_user_insights_df["Today's Date"] = dt.datetime.utcnow().strftime("%Y-%m-%d")
        objectives_user_insights_df["Days Since Update"] = pd.to_datetime(objectives_user_insights_df["Today's Date"]) - pd.to_datetime(objectives_user_insights_df["Last Updated"])
        days_since_update = objectives_user_insights_df["Days Since Update"].dropna().dt.days
        okr_updated_in_last_2_weeks = (np.sum(days_since_update < 14) / total_okrs)*100

        #7 OKRs by Progress%
        progress_bins = ["Under 30%", "30% to 70%", "Over 70%"]
        progress_bins_percent = pd.cut(objectives_user_insights_df["Progress %"], [-1, 30, 70, 100], labels=progress_bins)
        result = pd.value_counts(progress_bins_percent)
        okr_progress = []
        for record in result:
              okr_progress.append(record)

        #8 OKRs by Status
        result1 = objectives_user_insights_df.groupby("Status_x").size()
        okrstatus_datalabels = []
        okrstatus_datalabels = result1.index.values.tolist()
        okrstatus_data = []

        for data in result1:
            okrstatus_data.append(data)


        #9 No. of users
        noofusers_data = find_unique(user_insights_df, "Name")

        #8 Users Status
        userstatus_data = []
        result = user_insights_df.groupby("Status_x").size()
        for Status_x in result:
              userstatus_data.append(Status_x)


        #9 Users Objective Assignment
        userobj_data = totalsum(user_insights_df, "Public Objectives", 0)

        #10 Users Check-in rigor
        usercheckin_data = totalsum(user_insights_df, "Objectives with Check-ins", 0)

        #11 QuickExportDF
        quickExportDF = user_insights_df[['Name', 'Manager_x', 'Public Objectives','Objectives with Check-ins','Average Progress (in %)','Last Active']].copy()
        quickExportDF['Last Active'] = quickExportDF['Last Active'].dt.strftime('%m/%d/%Y')
        quickExportDF = quickExportDF.rename(columns={'Public Objectives': 'PublicObjectives', 'Objectives with Check-ins': 'ObjectiveswithCheckins', 'Average Progress (in %)': 'AverageProgress', 'Last Active':'LastActive'})
        #quickExportDF = quickExportDF['LastActive'].replace(',midnight','night').copy()

        #print("User Insights DF :", user_insights_df)

        #12 getting values of function from Model
        functions = Functions.objects.all()

        datapoints = {
            'total_okrs': total_okrs,
            'okr_checkedin': okr_checkedin,
            'okr_closed': okr_closed,
            'avg_progress': avg_progress,
            'okr_with_kpi': okr_with_kpi,
            'okr_updated_in_last_2_weeks': okr_updated_in_last_2_weeks,
            'okr_progress': okr_progress,
            'okrstatus_data': okrstatus_data,
            'okrstatus_datalabels': okrstatus_datalabels,
            'noofusers_data': noofusers_data,
            'userstatus_data': userstatus_data,
            'userobj_data': userobj_data,
            'usercheckin_data': usercheckin_data,
            'quickExportDF': quickExportDF,
        }
        return datapoints

#def home(request):
#    return render(request,'dashboard/base.html',functions)


#def base(request):
#    context = {
#        'datapoints': datapoints
#    }
#    return render(request,'dashboard/base.html',context)

#def dropdowntoload(request):
#    functions = Functions.objects.all()
#    return render(request,'dashboard/functionselection.html',{'functions': functions})

def functionselection(request):
    functions = Functions.objects.all().order_by('name')
    datapoints = setup_chartdetails("ALL")
#    print("Datapoints :", datapoints)
    return render(request,'dashboard/functionselection.html',{'functions': functions, 'datapoints': datapoints})
#    return render(request,'dashboard/functionselection.html',{'functions': functions})


def load_functiondetails(request):
    input_function = request.GET.get('functionname')
    datapoints = setup_chartdetails(input_function)
  #  print ("Datapoints" , datapoints)
    return render(request, 'dashboard/functiondetails.html', {'datapoints': datapoints})