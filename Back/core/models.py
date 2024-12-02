# core/models.py 

from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from django.core.validators import MaxValueValidator, MinValueValidator

# 사용자 모델
class User(AbstractUser):
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nickname = models.CharField(max_length=50, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    income_level = models.IntegerField(null=True, blank=True) # 연봉
    member_number = models.CharField(max_length=50, null=True, blank=True)
    joined_products = models.JSONField(default=list, blank=True, null=True) # 가입한 상품
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    current_assets = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True) # 현재 자산
    # 새 필드 추가
    monthly_saving = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(10000), MaxValueValidator(5000000)],
        help_text="사용자의 월 저축 가능 금액 (1만원 ~ 500만원)"
    )
    goal_amount = models.IntegerField(
        null=True, blank=True,
        help_text="사용자의 목표 금액"
    )
    goal_period = models.IntegerField(
        null=True, blank=True,
        help_text="사용자의 목표 기간 (개월 단위)"
    )
    tendency = models.IntegerField(default=0)  # 투자 성향
    desirePeriod = models.IntegerField(default=12)  # 선호 기간

    def calculate_age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    def save(self, *args, **kwargs):
        self.age = self.calculate_age()
        print(f"DEBUG: 모델 저장 전 - nickname: {self.nickname}, date_of_birth: {self.date_of_birth}")
        super().save(*args, **kwargs)
        print(f"DEBUG: 모델 저장 후 - nickname: {self.nickname}, date_of_birth: {self.date_of_birth}")

    def __str__(self):
        return self.username
    
    deposit_products = models.ManyToManyField(
        'DepositProduct',
        related_name='users',
        blank=True
    )

    saving_products = models.ManyToManyField(
        'SavingsProduct',
        related_name='users',
        blank=True
    )
    
class Join(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_code = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product_name}"


# 금융기관 정보 모델 (fdrmEntyApi)
class FinancialInstitution(models.Model):
    institution_code = models.CharField(max_length=20, unique=True)
    institution_name = models.CharField(max_length=255)
    region = models.CharField(max_length=255, null=True, blank=True)  # 지역 정보
    phone_number = models.CharField(max_length=20, null=True, blank=True)  # 전화번호

# 예금
class DepositProduct(models.Model):
    id = models.CharField(max_length=20, primary_key=True)  # CharField로 수정
    financial_company_code = models.CharField(max_length=20)
    financial_company_name = models.CharField(max_length=20)
    financial_product_code = models.CharField(max_length=20)
    financial_product_name = models.CharField(max_length=255)
    join_way = models.CharField(max_length=100, null=True, blank=True)
    interest_rate_type = models.CharField(max_length=50, null=True, blank=True)
    interest_rate_type_name = models.CharField(max_length=50, null=True, blank=True)
    basic_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dcls_month = models.CharField(max_length=6, null=True, blank=True)  # 공시제출월
    spcl_cnd = models.TextField(null=True, blank=True)  # 우대조건
    mtrt_int = models.TextField(null=True, blank=True)  # 만기 후 이율
    etc_note = models.TextField(null=True, blank=True)  # 추가설명
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expected_yield = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="예상 수익")
    popularity = models.IntegerField(default=0, help_text="사용자 가입 수 또는 인기도")

# 적금
class SavingsProduct(models.Model):
    id = models.CharField(max_length=20, primary_key=True)  # CharField로 수정
    financial_company_code = models.CharField(max_length=20)
    financial_company_name = models.CharField(max_length=20)
    financial_product_code = models.CharField(max_length=20)
    financial_product_name = models.CharField(max_length=255)
    join_way = models.CharField(max_length=100, null=True, blank=True)
    interest_rate_type = models.CharField(max_length=50, null=True, blank=True)
    interest_rate_type_name = models.CharField(max_length=50, null=True, blank=True)
    basic_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    maturity_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # New Fields
    dcls_month = models.CharField(max_length=6, null=True, blank=True)  # 공시제출월
    spcl_cnd = models.TextField(null=True, blank=True)  # 우대조건
    mtrt_int = models.TextField(null=True, blank=True)  # 만기 후 이율 (수정된 부분)
    etc_note = models.TextField(null=True, blank=True)  # 추가설명

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expected_yield = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="예상 수익")
    popularity = models.IntegerField(default=0, help_text="사용자 가입 수 또는 인기도")

class UserProductRelation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=10, choices=[('deposit', '예금'), ('savings', '적금')])
    product_id = models.IntegerField()
    join_date = models.DateTimeField(auto_now_add=True)
    amount_saved = models.DecimalField(max_digits=12, decimal_places=2, default=0)


class Exchange(models.Model):
    cur_unit = models.CharField(max_length=10)  # 통화 코드 (예: USD, JPY 등)
    cur_nm = models.CharField(max_length=100)  # 통화 이름 (예: 미국 달러)
    ttb = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # 살 때 환율
    tts = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # 팔 때 환율
    deal_bas_r = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # 기준 환율
    bkpr = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # 장부가격
    yy_efee_r = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # 연 환가료율
    ten_dd_efee_r = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # 10일 환가료율
    kftc_deal_bas_r = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # 서울외국환중개 기준환율
    kftc_bkpr = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # 서울외국환중개 장부가격

    def __str__(self):
        return f"{self.cur_nm} ({self.cur_unit})"
    
class StockBoard(models.Model):
    title = models.CharField(max_length=200)  # 게시글 제목
    content = models.TextField()             # 게시글 내용
    stock_name = models.CharField(max_length=100)  # 종목명
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)  # 좋아요

    def like_count(self):
        return self.likes.count()

class Comment(models.Model):
    post = models.ForeignKey(StockBoard, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Image(models.Model):
    post = models.ForeignKey(StockBoard, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class RealAsset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='real_assets')
    category = models.CharField(max_length=50)  # 대출, 예적금, 부동산, 자동차 등
    name = models.CharField(max_length=100)  # 자산 이름
    value = models.DecimalField(max_digits=12, decimal_places=2)  # 자산 가치
    created_at = models.DateTimeField(auto_now_add=True)

class Interest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interests')
    category = models.CharField(max_length=50)  # 예금, 적금, 주식
    item_id = models.PositiveIntegerField()  # 좋아요 한 상품/주식 ID
    liked_at = models.DateTimeField(auto_now_add=True)
    
class Dividend(models.Model):
    corp_name = models.CharField(max_length=255)  # 기업명
    corp_code = models.CharField(max_length=20)  # 기업 코드
    dividend_per_stock = models.FloatField()  # 주당 배당금
    created_at = models.DateTimeField(auto_now_add=True)  # 생성일시

    def __str__(self):
        return f"{self.corp_name} ({self.corp_code}) - {self.dividend_per_stock} KRW"
    
class BusinessReport(models.Model):
    corp_name = models.CharField(max_length=255)
    report_title = models.CharField(max_length=255)
    rcept_no = models.CharField(max_length=20, unique=True)
    main_products_services = models.TextField(null=True, blank=True)
    sales_and_orders = models.TextField(null=True, blank=True)
    business_content = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)  # 요약 필드 추가

    def __str__(self):
        return f"{self.corp_name} - {self.report_title}"