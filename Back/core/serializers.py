# core/serializers.py


from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from .models import (
    User, FinancialInstitution, SavingsProduct, DepositProduct,
    StockBoard, Comment, Image, RealAsset, Interest, BusinessReport
)
from datetime import date
from .utils import calculate_income_ratio_and_atmosphere

class CustomRegisterSerializer(RegisterSerializer):
    # 기본 필드들을 명시적으로 정의합니다.
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    # 추가 필드들 정의
    nickname = serializers.CharField(max_length=50, required=False, allow_blank=True)
    income_level = serializers.IntegerField(required=False, allow_null=True)
    member_number = serializers.CharField(max_length=50, required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=True)  # 생년월일 필드는 필수로 설정
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    current_assets = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)

    def calculate_age(self, date_of_birth):
        """
        date_of_birth를 기반으로 만 나이를 계산합니다.
        """
        if not date_of_birth:
            return None
        today = date.today()
        return today.year - date_of_birth.year - (
            (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
        )

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        # 기본 필드들을 포함합니다.
        data['username'] = self.validated_data.get('username', '')
        data['email'] = self.validated_data.get('email', '')
        data['password1'] = self.validated_data.get('password1', '')

        # 추가 필드들을 포함합니다.
        data['nickname'] = self.validated_data.get('nickname', '')
        data['income_level'] = self.validated_data.get('income_level', None)
        data['member_number'] = self.validated_data.get('member_number', '')
        data['date_of_birth'] = self.validated_data.get('date_of_birth', None)
        data['profile_picture'] = self.validated_data.get('profile_picture', None)
        data['current_assets'] = self.validated_data.get('current_assets', None)
        print(f"DEBUG: get_cleaned_data - {data}")
        return data

    def save(self, request):
        user = super().save(request)
        print(f"DEBUG: 요청 데이터 - {request.data}")
        print(f"DEBUG: save - validated_data: {self.validated_data}")

        # 추가 필드들을 저장합니다.
        user.nickname = self.validated_data.get('nickname', '')
        user.income_level = self.validated_data.get('income_level', None)
        user.member_number = self.validated_data.get('member_number', '')
        user.date_of_birth = self.validated_data.get('date_of_birth', None)
        user.profile_picture = self.validated_data.get('profile_picture', None)
        user.current_assets = self.validated_data.get('current_assets', None)

        # 만 나이를 계산하여 저장
        if user.date_of_birth:
            user.age = self.calculate_age(user.date_of_birth)

        user.save()
        print(f"DEBUG: 사용자 저장 후 - nickname: {user.nickname}, date_of_birth: {user.date_of_birth}, age: {user.age}")
        return user

# 사용자 Serializer
class UserSerializer(serializers.ModelSerializer):
    family_size = serializers.IntegerField(write_only=True, help_text="가구원 수를 입력하세요")
    income_ratio = serializers.SerializerMethodField()
    income_atmosphere = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'nickname', 'date_of_birth',
            'age', 'income_level', 'current_assets', 'profile_picture', 'profile_picture_url',
            'family_size', 'income_ratio', 'income_atmosphere'
        ]

    def update(self, instance, validated_data):
        # joined_products가 쉼표로 구분된 문자열로 저장되는지 처리
        joined_products = validated_data.get('joined_products')
        if isinstance(joined_products, list):
            instance.joined_products = ','.join(map(str, joined_products))
        else:
            instance.joined_products = joined_products
        instance.save()
        return instance
    
    def get_profile_picture_url(self, obj):
        # 프로필 이미지 URL 반환
        if obj.profile_picture:
            return obj.profile_picture.url
        return None
    
    def get_income_ratio(self, obj):
        family_size = self.context.get('family_size', None)
        if obj.income_level and family_size:
            return calculate_income_ratio_and_atmosphere(obj.income_level, family_size)['ratio']
        return None

    def get_income_atmosphere(self, obj):
        family_size = self.context.get('family_size', None)
        if obj.income_level and family_size:
            return calculate_income_ratio_and_atmosphere(obj.income_level, family_size)['atmosphere']
        return "데이터 없음"

# 금융기관 Serializer
class FinancialInstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialInstitution
        fields = ['id', 'institution_code', 'institution_name', 'region', 'phone_number']

# 적금 상품 Serializer
class DepositProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositProduct
        fields = [
            'financial_company_code', 'financial_company_name',
            'financial_product_code', 'financial_product_name',
            'join_way', 'interest_rate_type', 'interest_rate_type_name',
            'basic_interest_rate', 'max_interest_rate', 'dcls_month',
            'spcl_cnd', 'mtrt_int', 'etc_note', 'created_at', 'updated_at', 'mtrt_int'
        ]

# 예금 상품 Serializer
class SavingsProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsProduct
        fields = [
            'financial_company_code', 'financial_company_name',
            'financial_product_code', 'financial_product_name',
            'join_way', 'interest_rate_type', 'interest_rate_type_name',
            'basic_interest_rate', 'max_interest_rate', 'maturity_amount',
            'created_at', 'updated_at', 'mtrt_int'
        ]

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image', 'uploaded_at']

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_username', 'content', 'created_at']

class StockBoardSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    author_username = serializers.ReadOnlyField(source='author.username')
    like_count = serializers.ReadOnlyField()

    class Meta:
        model = StockBoard
        fields = [
            'id', 'title', 'content', 'stock_name', 'created_at', 'updated_at', 
            'author', 'author_username', 'likes', 'like_count', 'comments', 'images'
        ]
        
class RealAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealAsset
        fields = ['id', 'category', 'name', 'value', 'created_at']

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'category', 'item_id', 'liked_at']

# class CustomRegisterSerializer(RegisterSerializer):
#     date_of_birth = serializers.DateField(required=True)

#     def save(self, request):
#         # 요청 데이터 디버깅
#         print("DEBUG: 요청 데이터 - ", self.validated_data)

#         user = super().save(request)

#         # 생년월일 값을 저장
#         date_of_birth = self.validated_data.get('date_of_birth', None)
#         print("DEBUG: 생년월일 값 - ", date_of_birth)

#         if date_of_birth:
#             user.date_of_birth = date_of_birth
#             user.save()
#             print("DEBUG: 사용자 저장 완료 - ", user.date_of_birth)
#         else:
#             print("ERROR: 생년월일 값이 전달되지 않음!")

#         return user

class BusinessReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessReport
        fields = ['id', 'corp_name', 'report_title', 'rcept_no', 'content', 'created_at', 'summary']
        
class BusinessReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessReport
        fields = ['id', 'corp_name', 'report_title', 'summary']

class DepositRecommendSerializer(serializers.ModelSerializer):
    similarity_score = serializers.SerializerMethodField()

    class Meta:
        model = DepositProduct
        fields = [
            'id', 'financial_product_name', 'financial_company_name', 
            'basic_interest_rate', 'max_interest_rate', 'similarity_score'
        ]

    def get_similarity_score(self, obj):
        # 유사도 점수를 포함하고 싶다면 여기에 계산 로직을 추가
        # 현재는 예시로 None을 반환
        return obj.similarity_score if hasattr(obj, 'similarity_score') else None
    
class SavingRecommendSerializer(serializers.ModelSerializer):
    similarity_score = serializers.SerializerMethodField()

    class Meta:
        model = SavingsProduct
        fields = [
            'id', 'financial_product_name', 'financial_company_name', 
            'basic_interest_rate', 'max_interest_rate', 'maturity_amount', 'similarity_score'
        ]

    def get_similarity_score(self, obj):
        # 유사도 점수를 포함하고 싶다면 여기에 계산 로직을 추가
        # 현재는 예시로 None을 반환
        return obj.similarity_score if hasattr(obj, 'similarity_score') else None
    
