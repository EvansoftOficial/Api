from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *

@api_view(['GET'])
def Get_Type_Worker(request):
	return Response(Type_Worker.get_type_worker())

@api_view(['GET'])
def Get_Type_Contract(request):
	return Response(Type_Contract.get_type_contract())

@api_view(['GET'])
def Get_TSub_Type_Worker(request):
	return Response(Sub_Type_Worker.get_sub_type_worker())

@api_view(['GET'])
def Get_Payroll_Type_Document_Identification(request):
	return Response(Payroll_Type_Document_Identification.get_payroll_type_document_identification())

@api_view(['GET'])
def Get_Municipalities(request):
	return Response(Municipalities.get_municipalities())

@api_view(['GET'])
def Get_Permission(request):
	return Response(Permission.get_list_permission())

@api_view(['GET'])
def Get_Type_Document_I(request):
	return Response(Type_Document_I.get_type_document_i())


@api_view(['GET'])
def Get_Type_Regimen(request):
	return Response(Type_Regimen.get_type_regimen())

@api_view(['GET'])
def Get_Type_Organization(request):
	return Response(Type_Organization.get_type_organization())

@api_view(['POST'])
def Get_Unit_Measures(request):
	print("Hola")
	return Response(Unit_Measures.create_unit_measures(request.data))

@api_view(['GET'])
def Get_All_Unit_Measures(request):
	return Response(Unit_Measures.get_unit_measures())
