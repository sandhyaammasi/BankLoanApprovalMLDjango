from django.shortcuts import render
from .forms import ApprovalForm, MyForm #you might need to comment it down
from rest_framework import viewsets
from rest_framework.decorators import api_view
from django.core import serializers
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework.parsers import JSONParser
from django.contrib import messages

from . models import approvals
from . serializers import approvalsSerializers
import pickle
import joblib
import json
import numpy as np
from sklearn import preprocessing
import pandas as pd

from tensorflow import keras

class ApprovalsView(viewsets.ModelViewSet):
	queryset = approvals.objects.all()
	serializer_class = approvalsSerializers
		

def ohevalue(df):
	ohe_col = ['Dependents', 'ApplicantIncome', 'CoapplicantIncome', 'LoanAmount',
       'Loan_Amount_Term', 'Credit_History', 'Gender_Female', 'Gender_Male',
       'Married_No', 'Married_Yes', 'Education_Graduate',
       'Education_Not Graduate', 'Self_Employed_No', 'Self_Employed_Yes',
       'Property_Area_Rural', 'Property_Area_Semiurban',
       'Property_Area_Urban']

	cat_columns = ['Gender','Married','Education','Self_Employed','Property_Area']
	df_processed = pd.get_dummies(df,columns=cat_columns)
	newdict ={}
	for i in ohe_col:
		if i in df_processed:
			newdict[i]=df_processed[i].values
		else:
			newdict[i] = 0
	newdf = pd.DataFrame(newdict)
	return newdf


def myform(request):
	if request.method=="POST":
		form = MyForm(request.POST)
		if form.is_valid():
			myform =form.save(commit=False)
	else :
		form = MyForm()

#@api_view(["POST"])
def approvereject(unit):
	try:
		mdl=keras.models.load_model('d:/BankLoanApproval/DjangoAPI/MyAPI/bankLoanPredModel.h5')
		#mydata=pd.read_excel('/Users/sahityasehgal/Documents/Coding/bankloan/test.xlsx')
	#	mydata=request
	#	unit=np.array(list(mydata.values()))
	#	unit=unit.reshape(1,-1)
	#	unit=unit.reshape(1,-1)
		scalers=joblib.load("D:/BankLoanApproval/DjangoAPI/MyAPI/scalers.pkl")
		X=scalers.transform(unit)
		y_pred=mdl .predict(X)
		y_pred=(y_pred>0.58)
		newdf=pd.DataFrame(y_pred, columns=['Status'])
		newdf=newdf.replace({True:'Approved', False:'Rejected'})
		return ('Your Status is {}'.format(newdf))
		
	except ValueError as e:
		return Response(e.args[0], status.HTTP_400_BAD_REQUEST)

def cxcontact(request):
	if request.method=='POST':
		form = ApprovalForm(request.POST)
		if form.is_valid():
			firstname  = form.cleaned_data['firstname']
			lastname  = form.cleaned_data['lastname']
			Dependents  = form.cleaned_data['Dependents']
			ApplicantIncome  = form.cleaned_data['ApplicantIncome']
			CoapplicantIncome  = form.cleaned_data['CoapplicantIncome']
			LoanAmount  = form.cleaned_data['LoanAmount']
			Loan_Amount_Term  = form.cleaned_data['Loan_Amount_Term']
			Credit_History  = form.cleaned_data['Credit_History']
			Gender  = form.cleaned_data['Gender']
			Married  = form.cleaned_data['Married']
			Education  = form.cleaned_data['Education']
			Self_Employed  = form.cleaned_data['Self_Employed']
			Property_Area  = form.cleaned_data['Property_Area']
			#print(firstname,lastname,Dependants,Married,Property_Area)
			myDict = (request.POST).dict()
			df = pd.DataFrame(myDict,index=[0])
			print(approvereject(ohevalue(df)))
			answer = approvereject(ohevalue(df))
			messages.success(request,'Application Status: {}'.format(answer))
			#print(ohevalue(df))

	form = ApprovalForm()

	return render(request,'myForm/cxform.html',{'form':form})