# core / views.py 

from django.views import View
from core.utils import summarize_business_data, calculate_income_ratio_and_atmosphere
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404, get_list_or_404
from .models import DepositProduct, SavingsProduct, User, Exchange, StockBoard, Comment, Image, RealAsset, Interest, Join
from .serializers import DepositProductSerializer, SavingsProductSerializer, UserSerializer, StockBoardSerializer, CommentSerializer, ImageSerializer, RealAssetSerializer, InterestSerializer,BusinessReportSerializer 
from django.conf import settings
import requests
from decimal import Decimal, InvalidOperation
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action,  parser_classes
import OpenDartReader
from django.views.decorators.csrf import csrf_exempt
from decouple import config
from django.http import JsonResponse, HttpResponse
import os
from docx import Document
from bs4 import BeautifulSoup
from .serializers import CustomRegisterSerializer
from dj_rest_auth.registration.views import RegisterView
import pandas as pd
from .models import Dividend, BusinessReport
from .utils import collect_dividend_data
from django.apps import apps
from urllib.parse import urlencode
import openai
from .serializers import BusinessReportSerializer
from urllib.parse import unquote
import re
from rest_framework import generics
from django.contrib.auth.decorators import login_required
import json
from rest_framework.decorators import api_view, permission_classes
from .serializers import DepositRecommendSerializer, SavingRecommendSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Count

Dividend = apps.get_model('core', 'Dividend')

class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer


# CSRF 데코레이터!!!
@method_decorator(ensure_csrf_cookie, name='dispatch')
class YourView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": "CSRF token sent!"})

# 단일 객체 조회
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

# 리스트 조회
class DepositProductListView(APIView):
    def get(self, request):
        products = DepositProduct.objects.all()
        serializer = DepositProductSerializer(products, many=True)
        return Response(serializer.data)

class SavingsProductListView(APIView):
    def get(self, request):
        products = SavingsProduct.objects.all()
        serializer = SavingsProductSerializer(products, many=True)
        return Response(serializer.data)

# POST 요청 처리
class UpdateJoinedProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        joined_products = request.data.get('joined_products', [])
        if isinstance(joined_products, list):
            user.joined_products = joined_products
            user.save()
            return Response({"message": "가입한 상품 목록이 업데이트되었습니다."}, status=status.HTTP_200_OK)
        return Response({"error": "유효한 데이터 형식이 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)

# DELETE 요청 처리
class DeleteDepositProductView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        product = get_object_or_404(DepositProduct, id=product_id)
        product.delete()
        return Response({"message": "상품이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)


class JoinedProductsUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        product_to_add = request.data.get('add', None)
        product_to_remove = request.data.get('remove', None)

        # 현재 joined_products를 리스트로 변환
        current_products = user.joined_products.split(',') if user.joined_products else []

        if product_to_add:
            current_products.append(product_to_add)
        if product_to_remove and product_to_remove in current_products:
            current_products.remove(product_to_remove)

        user.joined_products = ','.join(current_products)  # 쉼표로 구분하여 저장
        user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# 예금 상품 조회

class DepositProductListView(ListAPIView):
    queryset = DepositProduct.objects.all()
    serializer_class = DepositProductSerializer
    filter_backends = [SearchFilter]
    search_fields = ['financial_product_name', 'financial_company_code']

    def get_queryset(self):
        queryset = super().get_queryset()
        bank_name = self.request.query_params.get('bank_name')
        term = self.request.query_params.get('term')

        if bank_name:
            queryset = queryset.filter(financial_company_code=bank_name)
        if term:
            queryset = queryset.filter(join_way__icontains=term)  # 가입 방식 필터링

        return queryset

class DepositProductDetailView(RetrieveAPIView):
    queryset = DepositProduct.objects.all()
    serializer_class = DepositProductSerializer

# 적금 상품 조회

class SavingsProductListView(ListAPIView):
    queryset = SavingsProduct.objects.all()
    serializer_class = SavingsProductSerializer
    filter_backends = [SearchFilter]
    search_fields = ['financial_product_name', 'financial_company_code']

    def get_queryset(self):
        queryset = super().get_queryset()
        bank_name = self.request.query_params.get('bank_name')
        term = self.request.query_params.get('term')

        if bank_name:
            queryset = queryset.filter(financial_company_code=bank_name)
        if term:
            queryset = queryset.filter(join_way__icontains=term)

        return queryset

class SavingsProductDetailView(RetrieveAPIView):
    queryset = SavingsProduct.objects.all()
    serializer_class = SavingsProductSerializer

class DepositProductViewSet(ModelViewSet):
    queryset = DepositProduct.objects.all()
    serializer_class = DepositProductSerializer

class SavingsProductViewSet(ModelViewSet):
    queryset = SavingsProduct.objects.all()
    serializer_class = SavingsProductSerializer

class FetchDepositProductsView(APIView):
    permission_classes = [IsAdminUser]  # 관리자만 실행 가능

    def get(self, request):
        url = "http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json"
        api_key = settings.FSS_API_KEY

        if not api_key:
            return Response({"error": "FSS_API_KEY is not set in the environment variables."}, status=500)

        params = {"auth": api_key, "topFinGrpNo": "020000", "pageNo": 1}
        current_page = 1
        created_products = []
        skipped_products = []

        while True:
            params["pageNo"] = current_page
            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200:
                return Response(
                    {"error": f"Failed to fetch data. Status code: {response.status_code}", "response": response.text},
                    status=response.status_code,
                )

            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError:
                return Response({"error": "Invalid JSON response from the API.", "response": response.text[:500]}, status=500)

            products = data.get("result", {}).get("baseList", [])
            if not products:
                break

            for product in products:
                obj, created = DepositProduct.objects.get_or_create(
                    financial_company_code=product.get("fin_co_no", "Unknown"),
                    financial_product_code=product.get("fin_prdt_cd", "Unknown"),
                    defaults={
                        "financial_product_name": product.get("fin_prdt_nm", "Unknown"),
                        "join_way": product.get("join_way", "N/A"),
                        "interest_rate_type": product.get("intr_rate_type", "N/A"),
                        "interest_rate_type_name": product.get("intr_rate_type_nm", "N/A"),
                        "basic_interest_rate": product.get("intr_rate", 0.0),
                        "max_interest_rate": product.get("intr_rate2", 0.0),
                    },
                )
                if created:
                    created_products.append(obj.financial_product_name)
                else:
                    skipped_products.append(obj.financial_product_name)

            current_page += 1
            max_page = data.get("result", {}).get("max_page_no", current_page)
            if current_page > max_page:
                break

        return Response(
            {
                "message": "Fetch operation completed.",
                "created_products": created_products,
                "skipped_products": skipped_products,
            }
        )
    
class FetchSavingsProductsView(APIView):
    permission_classes = [IsAdminUser]  # 관리자만 접근 가능

    def get(self, request):
        url = "http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json"
        api_key = settings.FSS_API_KEY

        if not api_key:
            return Response({"error": "FSS_API_KEY is not set in the environment variables."}, status=500)

        params = {"auth": api_key, "topFinGrpNo": "020000", "pageNo": 1}
        current_page = 1
        created_products = []
        skipped_products = []

        while True:
            params["pageNo"] = current_page
            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200:
                return Response(
                    {"error": f"Failed to fetch data. Status code: {response.status_code}", "response": response.text},
                    status=response.status_code,
                )

            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError:
                return Response({"error": "Invalid JSON response from the API.", "response": response.text[:500]}, status=500)

            products = data.get("result", {}).get("baseList", [])
            if not products:
                break

            for product in products:
                try:
                    obj, created = SavingsProduct.objects.get_or_create(
                        financial_company_code=product.get("fin_co_no", "Unknown"),
                        financial_product_code=product.get("fin_prdt_cd", "Unknown"),
                        defaults={
                            "financial_product_name": product.get("fin_prdt_nm", "Unknown"),
                            "join_way": product.get("join_way", "N/A"),
                            "interest_rate_type": product.get("intr_rate_type", "N/A"),
                            "interest_rate_type_name": product.get("intr_rate_type_nm", "N/A"),
                            "basic_interest_rate": self.get_decimal_value(product.get("intr_rate", 0.0)),
                            "max_interest_rate": self.get_decimal_value(product.get("intr_rate2", 0.0)),
                            "maturity_amount": self.get_decimal_value(product.get("mtrt_int", None)),
                        },
                    )
                    if created:
                        created_products.append(obj.financial_product_name)
                    else:
                        skipped_products.append(obj.financial_product_name)
                except Exception as e:
                    return Response({"error": f"Error saving product: {str(e)}"}, status=500)

            current_page += 1
            max_page = data.get("result", {}).get("max_page_no", current_page)
            if current_page > max_page:
                break

        return Response(
            {
                "message": "Fetch operation completed.",
                "created_products": created_products,
                "skipped_products": skipped_products,
            }
        )

    def get_decimal_value(self, value):
        """
        Convert a value to Decimal if possible, otherwise return None.
        """
        if value is None or value == "":
            return None
        try:
            return Decimal(value)
        except (InvalidOperation, ValueError):
            return None
        
class ExchangeRateAPIView(APIView):
    def get(self, request):
        # 모든 환율 데이터를 반환
        rates = Exchange.objects.all().values(
            "cur_unit", "cur_nm", "deal_bas_r", "bkpr", "ttb", "tts"
        )
        return Response({"rates": list(rates)})

    def post(self, request):
        # 두 통화와 금액을 입력받아 환율 계산
        from_currency = request.data.get("from_currency")
        to_currency = request.data.get("to_currency")
        amount = float(request.data.get("amount", 1))

        if not from_currency or not to_currency:
            return Response({"error": "Both from_currency and to_currency are required."}, status=400)

        from_rate = get_object_or_404(Exchange, cur_unit=from_currency).deal_bas_r
        to_rate = get_object_or_404(Exchange, cur_unit=to_currency).deal_bas_r

        converted_amount = (amount / from_rate) * to_rate
        return Response({"converted_amount": converted_amount})


# class SearchBanksView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         latitude = request.query_params.get("latitude")
#         longitude = request.query_params.get("longitude")
#         keyword = request.query_params.get("keyword")

#         if not latitude or not longitude or not keyword:
#             return Response({"error": "latitude, longitude, and keyword are required."}, status=400)

#         url = "https://dapi.kakao.com/v2/local/search/keyword.json"
#         headers = {
#             "Authorization": f"KakaoAK {settings.KAKAO_API_KEY}"
#         }
#         params = {
#             "query": keyword,
#             "x": longitude,
#             "y": latitude,
#             "radius": 500
#         }

#         try:
#             response = requests.get(url, headers=headers, params=params)
#             print("응답 상태 코드:", response.status_code)
#             print("응답 본문:", response.text)
            
#             if response.status_code == 200:
#                 return Response(response.json())
#             else:
#                 return Response({"error": f"Kakao API 요청 실패: {response.status_code}"}, status=response.status_code)
#         except Exception as e:
#             return Response({"error": str(e)}, status=500)

class StockBoardViewSet(viewsets.ModelViewSet):
    queryset = StockBoard.objects.all().order_by('-created_at')
    serializer_class = StockBoardSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return Response({'status': 'like toggled', 'likes_count': post.like_count()})

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class ImageUploadViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()

class RealAssetViewSet(viewsets.ModelViewSet):
    serializer_class = RealAssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RealAsset.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InterestViewSet(viewsets.ModelViewSet):
    serializer_class = InterestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Interest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        """
        현재 사용자 정보를 반환합니다.
        특정 요청에서는 제한된 데이터만 반환합니다.
        """
        user = request.user

        # 쿼리 매개변수 체크 (e.g., /api/core/actions/profile/?fields=income)
        if request.query_params.get("fields") == "income":
            response_data = {
                "income_level": user.income_level,
                "income_ratio": user.income_ratio,
                "income_atmosphere": user.income_atmosphere,
            }
            return Response(response_data)

        # 기본 동작: 전체 사용자 데이터 반환
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        """
        사용자 정보를 업데이트합니다.
        """
        user = request.user
        data = request.data

        # 자산 업데이트
        if 'current_assets' in data:
            try:
                user.current_assets = float(data['current_assets'])
            except ValueError:
                return Response({"detail": "Invalid value for current_assets"}, status=400)

        # 연봉 업데이트
        if 'income_level' in data:
            try:
                user.income_level = int(data['income_level'])
            except ValueError:
                return Response({"detail": "Invalid value for income_level"}, status=400)

        # 사용자 데이터 저장
        user.save()

        # 업데이트된 데이터 반환 (전체 프로필 데이터)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_profile_img(request):
    user = request.user
    profile_picture = request.FILES.get('profile_picture')

    if profile_picture:
        user.profile_picture = profile_picture
        user.save()
        # 반환하는 URL이 MEDIA_URL을 포함하도록 설정
        return JsonResponse({'profile_picture': user.profile_picture.url}, status=200)

    return JsonResponse({'error': 'No file uploaded'}, status=400)

class IncomeCalculatorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 소득분위 계산 로직
        income = request.data.get("income")
        if income is None:
            return Response({"error": "Income is required"}, status=400)

        # 예제: 간단한 소득분위 계산기
        try:
            income = float(income)
            if income < 20000:
                level = 1
            elif income < 40000:
                level = 2
            elif income < 60000:
                level = 3
            else:
                level = 4

            user = request.user
            user.income_level = level
            user.save()

            return Response({"income_level": level})
        except ValueError:
            return Response({"error": "Invalid income value"}, status=400)

class UpdateJoinedProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        joined_products = request.data.get('joined_products', [])
        if isinstance(joined_products, list):
            user.joined_products = joined_products  # 배열 데이터를 그대로 저장
            user.save()
            return Response({"message": "가입한 상품 목록이 업데이트되었습니다.", "joined_products": user.joined_products}, status=status.HTTP_200_OK)
        return Response({"error": "유효한 데이터 형식이 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)        

class CustomRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        # 요청 데이터 출력
        print("DEBUG: 회원가입 요청 데이터 - ", request.data)

        # 디버깅을 위해 기본 동작 수행
        response = super().post(request, *args, **kwargs)

        # 응답 데이터 확인
        print("DEBUG: 회원가입 응답 데이터 - ", response.data)
        return response

class HighDividendStocksView(APIView):
    """
    배당률이 높은 주식 정보를 반환하는 API
    """

    def get(self, request):
        # API URL
        url = "http://apis.data.go.kr/1160100/service/GetStocDiviInfoService/getDiviInfo"

        # API 요청 파라미터
        query_params = {
            "serviceKey": settings.DART_STOCK_API_KEY,  # 발급받은 인증키
            "numOfRows": "10",  # 한 번에 가져올 데이터 수
            "pageNo": "1",  # 페이지 번호
            "basDt": "20230101",  # 기준 날짜 (필요 시 변경)
        }

        try:
            # API 요청
            response = requests.get(url, params=query_params, timeout=10)

            # 디버깅: 상태 코드 및 응답 내용 확인
            print("DEBUG: 응답 상태 코드:", response.status_code)
            print("DEBUG: 응답 본문:", response.text)

            # 상태 코드 확인
            if response.status_code != 200:
                return Response(
                    {"error": f"API 요청 실패: 상태 코드 {response.status_code}"}, status=500
                )

            # JSON 파싱
            try:
                data = response.json()
            except ValueError as e:
                print("DEBUG: JSON 파싱 오류:", str(e))
                return Response({"error": f"JSON 파싱 오류: {str(e)}"}, status=500)

            # 응답 데이터 확인
            items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
            if not items:
                return Response({"error": "데이터가 없습니다."}, status=404)

            return Response(items, status=200)

        except Exception as e:
            print("DEBUG: API 요청 실패:", str(e))
            return Response({"error": f"API 요청 실패: {str(e)}"}, status=500)





dart = OpenDartReader(settings.DART_API_KEY)

# Helper Function: 특정 섹션 추출
def extract_section(text_content, section_title):
    """
    텍스트 데이터에서 특정 섹션의 내용을 추출
    """
    try:
        # 패턴 설정: 섹션 제목과 다음 섹션 제목 사이의 내용 추출
        pattern = rf"{re.escape(section_title)}(.*?)(\n\d+\.\s|$)"
        match = re.search(pattern, text_content, re.DOTALL)
        if match:
            extracted_content = match.group(1).strip()
            if not extracted_content:
                return f"{section_title} 섹션에 유효한 내용이 없습니다."
            return extracted_content
        else:
            return f"{section_title} 섹션을 찾을 수 없습니다."
    except Exception as e:
        return f"섹션 추출 중 오류 발생: {str(e)}"


def save_recent_business_sections(corp_name):
    try:
        dart = OpenDartReader(settings.DART_API_KEY)
        corp_code = dart.find_corp_code(corp_name)
        if not corp_code:
            return {"error": f"Cannot find corp_code for {corp_name}"}
        
        # DART API에서 보고서 목록 가져오기
        reports = dart.list(corp_code, kind='A')  # 정기보고서

        if reports.empty:
            return {"error": f"No reports found for {corp_name}"}

        saved_report_ids = []
        # 최근 하나의 보고서만 가져오기
        recent_report = reports.head(1)

        for _, report in recent_report.iterrows():
            rcept_no = report['rcept_no']
            report_title = report['report_nm']

            # II. 사업의 내용 가져오기
            sub_docs = dart.sub_docs(rcept_no)
            print(f"DEBUG: sub_docs titles: {sub_docs['title'].tolist()}")  # 디버그 출력 추가
            business_section_row = sub_docs[sub_docs['title'].str.contains('사업의 내용', na=False)]
            if business_section_row.empty:
                print(f"DEBUG: {report_title}에 '사업의 내용' 섹션 없음.")
                continue

            business_url = business_section_row['url'].iloc[0]
            response = requests.get(business_url, stream=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text(separator="\n").strip()

            # 데이터 저장 또는 업데이트
            report_obj, created = BusinessReport.objects.update_or_create(
                rcept_no=rcept_no,
                defaults={
                    'corp_name': corp_name,
                    'report_title': report_title,
                    'business_content': text_content,
                    'main_products_services': extract_section(text_content, '2. 주요 제품 및 서비스'),
                    'sales_and_orders': extract_section(text_content, '4. 매출 및 수주상황'),
                }
            )
            saved_report_ids.append(report_obj.id)

        if not saved_report_ids:
            return {"error": "No relevant sections found in the recent report."}

        return {"message": "Sections saved successfully", "saved_report_ids": saved_report_ids}

    except Exception as e:
        return {"error": str(e)}







# # API View: 보고서 저장 및 요약
# @csrf_exempt
# def fetch_and_summarize_business(request):
#     corp_name = request.GET.get('corp_name')
#     if not corp_name:
#         return JsonResponse({"error": "corp_name is required"}, status=400)

#     try:
#         # 보고서 저장
#         save_result = save_recent_business_sections(corp_name)
#         if "error" in save_result:
#             return JsonResponse(save_result, status=404)

#         # 저장된 보고서를 가져와 요약
#         saved_reports = BusinessReport.objects.filter(id__in=save_result["saved_report_ids"])
#         summarized_data = []

#         for report in saved_reports:
#             summary = summarize_business_data(report.business_content)
#             summarized_data.append({
#                 "corp_name": report.corp_name,
#                 "report_title": report.report_title,
#                 "summary": summary,
#             })

#         return JsonResponse({"message": "Data summarized successfully", "summaries": summarized_data}, safe=False, status=200)

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def fetch_and_summarize_business(request):
    corp_name = request.GET.get('corp_name')
    if not corp_name:
        return JsonResponse({"error": "corp_name is required"}, status=400)

    try:
        # 보고서 저장
        save_result = save_recent_business_sections(corp_name)
        if "error" in save_result:
            print(f"DEBUG: save_result 에러 - {save_result['error']}")
            return JsonResponse(save_result, status=500)

        # 저장된 보고서를 가져와 요약
        report_id = save_result["saved_report_ids"][0]  # 하나의 보고서 ID만 사용
        report = BusinessReport.objects.get(id=report_id)
        print(f"DEBUG: Processing report - {report.report_title}")
        print(f"DEBUG: Length of business_content: {len(report.business_content)}")

        # 텍스트 요약
        summary = summarize_business_data(report.business_content)

        formatted_summary = summary.replace("\n", "<br>")
        report.summary = summary  # 요약 결과를 모델 인스턴스에 저장
        report.save()  # 변경 사항 저장

        summarized_data = {
            "corp_name": report.corp_name,
            "report_title": report.report_title,
            "summary": summary,
        }

        return JsonResponse({"message": "Data summarized successfully", "summary": summarized_data}, safe=False, status=200)

    except Exception as e:
        print(f"DEBUG: Exception 발생 - {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)



# API View: GPT 요약 요청
class GPTSummaryView(APIView):
    def get(self, request, report_id):
        openai.api_key = settings.OPENAI_API_KEY

        # 특정 보고서 가져오기
        report = get_object_or_404(BusinessReport, id=report_id)

        try:
            # GPT를 이용한 요약
            summary = summarize_business_data(report.business_content)

            return Response({"corp_name": report.corp_name, 
                             "report_title": report.report_title, 
                             "summary": summary}, status=200)
        except openai.error.OpenAIError as e:
            return Response({"error": str(e)}, status=500)
        
@csrf_exempt
def fetch_recent_ii_business(request):
    """
    특정 기업의 최근 보고서를 저장하고 데이터를 반환
    """
    corp_name = request.GET.get('corp_name')
    if not corp_name:
        return JsonResponse({"error": "corp_name is required"}, status=400)

    try:
        # Business sections 저장 로직 호출
        result = save_recent_business_sections(corp_name)
        if "error" in result:
            return JsonResponse(result, status=404)

        return JsonResponse({"message": result["message"], "saved_report_ids": result["saved_report_ids"]}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
class BusinessReportDetailView(APIView):
    def get(self, request, report_id):
        try:
            report = BusinessReport.objects.get(id=report_id)
            data = {
                "corp_name": report.corp_name,
                "report_title": report.report_title,
                "summary": report.summary,
            }
            return Response(data, status=200)
        except BusinessReport.DoesNotExist:
            return Response({"error": "Report not found"}, status=404)
        
class BusinessReportDetailView(generics.RetrieveAPIView):
    queryset = BusinessReport.objects.all()
    serializer_class = BusinessReportSerializer
    lookup_field = 'id'


# @csrf_exempt
# def recommend_products(request):
#     """
#     사용자 입력값에 기반한 금융상품 추천 API
#     """
#     try:
#         # 입력 데이터 가져오기
#         goal_amount = int(request.GET.get('goal_amount', 0))
#         goal_period = int(request.GET.get('goal_period', 12))
#         monthly_saving = int(request.GET.get('monthly_saving', 0))
#         priority = request.GET.get('priority', 'interest')  # 'interest' 또는 'stability'
#         product_type = request.GET.get('product_type', '적금')  # '적금' 또는 '예금'

#         # 금융상품 필터링
#         if product_type == '적금':
#             products = SavingsProduct.objects.all()
#         else:
#             products = DepositProduct.objects.all()

#         # 상품 추천 계산
#         recommendations = []
#         for product in products:
#             if product_type == '적금':
#                 # 적금 계산: 월 저축 금액 * 기간
#                 total_saving = monthly_saving * goal_period
#                 if total_saving >= goal_amount:
#                     recommendations.append({
#                         'name': product.financial_product_name,
#                         'basic_interest_rate': product.basic_interest_rate,
#                         'max_interest_rate': product.max_interest_rate,
#                     })
#             elif product_type == '예금':
#                 # 예금 계산: 저축액 + (저축액 * 기본 금리 * (기간 / 12))
#                 estimated_amount = monthly_saving + (
#                     monthly_saving * float(product.basic_interest_rate) * (goal_period / 12)
#                 )
#                 if estimated_amount >= goal_amount:
#                     recommendations.append({
#                         'name': product.financial_product_name,
#                         'basic_interest_rate': product.basic_interest_rate,
#                         'max_interest_rate': product.max_interest_rate,
#                     })
#         # 디버깅 코드 추가
#         for product in products:
#             if product_type == '적금':
#                 total_saving = monthly_saving * goal_period
#                 print(f"Checking {product.financial_product_name}: Total Saving: {total_saving}")
#                 if total_saving >= goal_amount:
#                     print(f"Product {product.financial_product_name} is eligible")
#             elif product_type == '예금':
#                 estimated_amount = monthly_saving + (monthly_saving * float(product.basic_interest_rate) * (goal_period / 12))
#                 print(f"Checking {product.financial_product_name}: Estimated Amount: {estimated_amount}")
#                 if estimated_amount >= goal_amount:
#                     print(f"Product {product.financial_product_name} is eligible")
  

#         # 정렬
#         if priority == 'interest':
#             recommendations = sorted(recommendations, key=lambda x: x['max_interest_rate'], reverse=True)
#         else:
#             recommendations = sorted(recommendations, key=lambda x: x['basic_interest_rate'], reverse=True)

#         return JsonResponse({'recommendations': recommendations[:5]})  # 최대 5개 추천

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_product(request):
    try:
        user = request.user
        product_id = request.data.get("product_id")
        product_type = request.data.get("product_type")

        if not product_id or not product_type:
            return Response({"error": "product_id와 product_type은 필수입니다."}, status=400)

        if product_type == "savings":
            product = SavingsProduct.objects.filter(financial_product_code=product_id).first()
        elif product_type == "deposit":
            product = DepositProduct.objects.filter(financial_product_code=product_id).first()
        else:
            return Response({"error": "잘못된 product_type 입니다."}, status=400)

        if not product:
            return Response({"error": "해당 상품을 찾을 수 없습니다."}, status=404)

        if product_type == "savings" and product in user.saving_products.all():
            return Response({"error": "이미 가입된 적금 상품입니다."}, status=400)
        elif product_type == "deposit" and product in user.deposit_products.all():
            return Response({"error": "이미 가입된 예금 상품입니다."}, status=400)

        if product_type == "savings":
            user.saving_products.add(product)
        elif product_type == "deposit":
            user.deposit_products.add(product)

        return Response({"message": f"{product.financial_product_name} 가입 완료!"}, status=200)

    except Exception as e:
        print(f"DEBUG: 오류 발생 - {e}")
        return Response({"error": str(e)}, status=500)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_joined_products(request):
    """
    사용자가 가입한 금융 상품 목록 가져오기
    """
    try:
        user = request.user

        # ManyToManyField에서 데이터 가져오기
        deposit_products = user.deposit_products.all()
        saving_products = user.saving_products.all()

        # 직렬화된 데이터 생성
        deposit_data = [
            {
                "id": product.id,
                "type": "deposit",
                "name": product.financial_product_name,
                "company": product.financial_company_name,
                "interest_rate": product.basic_interest_rate,
                "max_interest_rate": product.max_interest_rate,
                "dcls_month": product.dcls_month,  # 공시 제출월
                "spcl_cnd": product.spcl_cnd,      # 우대조건
                "etc_note": product.etc_note,      # 추가설명
            }
            for product in deposit_products
        ]

        saving_data = [
            {
                "id": product.id,
                "type": "savings",
                "name": product.financial_product_name,
                "company": product.financial_company_name,
                "interest_rate": product.basic_interest_rate,
                "max_interest_rate": product.max_interest_rate,
                "dcls_month": product.dcls_month,  # 공시 제출월
                "spcl_cnd": product.spcl_cnd,      # 우대조건
                "etc_note": product.etc_note,      # 추가설명
            }
            for product in saving_products
        ]

        return Response({
            "joined_products": {
                "deposits": deposit_data,
                "savings": saving_data,
            }
        }, status=200)

    except Exception as e:
        print(f"DEBUG: 오류 발생 - {e}")
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_product(request):
    """
    금융 상품 해지 API
    - 사용자의 ManyToManyField에서 상품 제거
    """
    try:
        user = request.user
        product_id = request.data.get("product_id")
        product_type = request.data.get("product_type")

        if not product_id or not product_type:
            return Response({"error": "product_id와 product_type은 필수입니다."}, status=400)

        if product_type == "savings":
            product = SavingsProduct.objects.filter(financial_product_code=product_id).first()
            if product and product in user.saving_products.all():
                user.saving_products.remove(product)
                return Response({"message": f"{product.financial_product_name} 상품이 해지되었습니다."}, status=200)
            else:
                return Response({"error": "해당 상품은 가입되지 않았습니다."}, status=400)

        elif product_type == "deposit":
            product = DepositProduct.objects.filter(financial_product_code=product_id).first()
            if product and product in user.deposit_products.all():
                user.deposit_products.remove(product)
                return Response({"message": f"{product.financial_product_name} 상품이 해지되었습니다."}, status=200)
            else:
                return Response({"error": "해당 상품은 가입되지 않았습니다."}, status=400)


        else:
            return Response({"error": "잘못된 product_type입니다."}, status=400)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


# 예금 추천 (사용자 기반)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def deposit_recommend(request, username):
    user = get_object_or_404(User, username=username)
    income_level = user.income_level if user.income_level is not None else 0
    current_assets = user.current_assets if user.current_assets is not None else 0
    tendency = user.tendency if user.tendency is not None else 0
    desirePeriod = user.desirePeriod if user.desirePeriod is not None else 12

    cnt_lst = [0] * 70
    users = User.objects.all()
    for other_user in users:
        other_income_level = other_user.income_level if other_user.income_level is not None else 0
        other_current_assets = other_user.current_assets if other_user.current_assets is not None else 0
        other_tendency = other_user.tendency if other_user.tendency is not None else 0
        other_desirePeriod = other_user.desirePeriod if other_user.desirePeriod is not None else 12

        if (
            income_level - 2 <= other_income_level <= income_level + 2 and
            current_assets - 1000000000 <= other_current_assets <= current_assets + 1000000000 and
            tendency - 2 <= other_tendency <= tendency + 2 and
            desirePeriod - 12 <= other_desirePeriod <= desirePeriod + 12
        ):
            # 수정된 필드명 사용
            deposits = other_user.deposit_products.all()
            for deposit in deposits:
                cnt_lst[int(deposit.id)] += 1

    cnt_tpl = [(cnt, idx) for idx, cnt in enumerate(cnt_lst)]
    cnt_tpl.sort(key=lambda x: -x[0])
    best = [tpl[1] for tpl in cnt_tpl[:11]]

    deposits = DepositProduct.objects.filter(id__in=best)
    serializer = DepositRecommendSerializer(deposits, many=True)
    return Response(serializer.data)

# 적금 추천 (사용자 기반)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def saving_recommend(request, username):
    user = get_object_or_404(User, username=username)
    # 기본값 설정
    income_level = user.income_level if user.income_level is not None else 0
    current_assets = user.current_assets if user.current_assets is not None else 0
    tendency = user.tendency if user.tendency is not None else 0
    desirePeriod = user.desirePeriod if user.desirePeriod is not None else 12

    cnt_lst = [0] * 70
    users = User.objects.all()
    for other_user in users:
        # 다른 사용자 데이터 기본값 처리
        other_income_level = other_user.income_level if other_user.income_level is not None else 0
        other_current_assets = other_user.current_assets if other_user.current_assets is not None else 0
        other_tendency = other_user.tendency if other_user.tendency is not None else 0
        other_desirePeriod = other_user.desirePeriod if other_user.desirePeriod is not None else 12

        if (
            income_level - 2 <= other_income_level <= income_level + 2 and
            current_assets - 1000000000 <= other_current_assets <= current_assets + 1000000000 and
            tendency - 2 <= other_tendency <= tendency + 2 and
            desirePeriod - 12 <= other_desirePeriod <= desirePeriod + 12
        ):
            # 수정된 필드명 사용
            savings = other_user.saving_products.all()
            for saving in savings:
                cnt_lst[int(saving.id)] += 1

    cnt_tpl = [(cnt, idx) for idx, cnt in enumerate(cnt_lst)]
    cnt_tpl.sort(key=lambda x: -x[0])
    best = [tpl[1] for tpl in cnt_tpl[:11]]

    savings = SavingsProduct.objects.filter(id__in=best)
    serializer = SavingRecommendSerializer(savings, many=True)
    return Response(serializer.data)

# 예금 추천 (연령 기반)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def deposit_recommend_second(request, username):
    user = get_object_or_404(User, username=username)
    age = user.age

    # cnt_lst를 딕셔너리로 변경
    cnt_dict = {}

    users = User.objects.all()
    for other_user in users:
        if age // 10 == other_user.age // 10:
            deposits = other_user.deposit_products.all()
            for deposit in deposits:
                if deposit.id not in cnt_dict:
                    cnt_dict[deposit.id] = 0
                cnt_dict[deposit.id] += 1

    # 딕셔너리를 정렬하여 상위 5개만 추출
    sorted_cnt = sorted(cnt_dict.items(), key=lambda x: -x[1])
    best_ids = [item[0] for item in sorted_cnt[:10]]

    deposits = DepositProduct.objects.filter(id__in=best_ids)
    serializer = DepositRecommendSerializer(deposits, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def saving_recommend_second(request, username):
    user = get_object_or_404(User, username=username)
    age = user.age

    # cnt_lst를 딕셔너리로 변경
    cnt_dict = {}

    users = User.objects.all()
    for other_user in users:
        if age // 10 == other_user.age // 10:
            savings = other_user.saving_products.all()
            for saving in savings:
                if saving.id not in cnt_dict:
                    cnt_dict[saving.id] = 0
                cnt_dict[saving.id] += 1

    # 딕셔너리를 정렬하여 상위 5개만 추출
    sorted_cnt = sorted(cnt_dict.items(), key=lambda x: -x[1])
    best_ids = [item[0] for item in sorted_cnt[:10]]

    savings = SavingsProduct.objects.filter(id__in=best_ids)
    serializer = SavingRecommendSerializer(savings, many=True)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_joined_products(request):
    try:
        # 예금 상품 집계
        top_deposit_products = (
            DepositProduct.objects.annotate(join_count=Count('users'))
            .order_by('-join_count')[:5]
        )

        # 적금 상품 집계
        top_savings_products = (
            SavingsProduct.objects.annotate(join_count=Count('users'))
            .order_by('-join_count')[:5]
        )

        # 데이터 직렬화
        deposit_data = [
            {
                "id": product.id,
                "name": product.financial_product_name,
                "company": product.financial_company_name,
                "join_count": product.join_count,
                "type": "deposit",
            }
            for product in top_deposit_products
        ]

        savings_data = [
            {
                "id": product.id,
                "name": product.financial_product_name,
                "company": product.financial_company_name,
                "join_count": product.join_count,
                "type": "savings",
            }
            for product in top_savings_products
        ]

        # 상위 5개 데이터를 합치기
        combined_data = sorted(
            deposit_data + savings_data,
            key=lambda x: x['join_count'],
            reverse=True
        )[:5]

        return Response({"top_joined_products": combined_data}, status=200)

    except Exception as e:
        print(f"DEBUG: 오류 발생 - {e}")
        return Response({"error": str(e)}, status=500)


    
class IncomeRatioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        사용자가 입력한 소득과 가구원 수를 기반으로 소득 비율 및 분위 계산.
        동시에 사용자의 소득 데이터를 업데이트.
        """
        income_level = request.query_params.get("income_level")
        family_size = request.query_params.get("family_size", 1)  # 기본값 1

        if not income_level or not family_size:
            return Response(
                {"detail": "income_level and family_size are required."},
                status=400
            )

        try:
            income_level = int(income_level)
            family_size = int(family_size)
        except ValueError:
            return Response(
                {"detail": "income_level and family_size must be integers."},
                status=400
            )

        # 사용자 정보 업데이트
        user = request.user
        user.income_level = income_level
        user.save()

        # 소득 비율 및 분위 계산
        income_ratio, income_atmosphere = calculate_income_ratio_and_atmosphere(
            income_level, family_size
        )

        return Response({
            "income_level": income_level,
            "income_ratio": income_ratio,
            "income_atmosphere": income_atmosphere
        })
    def post(self, request):
            income_level = request.data.get("income_level")
            family_size = request.data.get("family_size")

            if not income_level or not family_size:
                return Response({"detail": "소득과 가구원 수를 입력해주세요."}, status=400)

            try:
                income_level = int(income_level)
                family_size = int(family_size)
                income_ratio, income_atmosphere = calculate_income_ratio_and_atmosphere(income_level, family_size)
                return Response({
                    "income_level": income_level,
                    "income_ratio": income_ratio,
                    "income_atmosphere": income_atmosphere
                })
            except ValueError:
                return Response({"detail": "소득 또는 가구원 수가 유효하지 않습니다."}, status=400)
            except Exception as e:
                return Response({"detail": str(e)}, status=500)