from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AccountingEntry

@api_view(['POST'])
def Generate_Accounting(request):
	return Response(AccountingEntry.generate_accounting(request.data))

@api_view(['POST'])
def Generate_Excel(request):
	return Response(AccountingEntry.generate_excel(request.data))