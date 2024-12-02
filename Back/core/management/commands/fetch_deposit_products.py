import requests
from django.core.management.base import BaseCommand
from core.models import DepositProduct
from decouple import config
from decimal import Decimal, InvalidOperation


class Command(BaseCommand):
    help = "Fetch deposit products from external API and save them to the database."

    def handle(self, *args, **kwargs):
        url = "http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json"
        api_key = config('FSS_API_KEY')

        if not api_key:
            self.stderr.write("FSS_API_KEY is not set in the environment variables.")
            return

        params = {"auth": api_key, "topFinGrpNo": "020000", "pageNo": 1}
        current_page = 1

        while True:
            params["pageNo"] = current_page
            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200:
                self.stderr.write(f"Failed to fetch data. Status code: {response.status_code}")
                return

            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError:
                self.stderr.write("Invalid JSON response.")
                return

            base_list = data.get("result", {}).get("baseList", [])
            for base in base_list:
                product = DepositProduct.objects.filter(financial_product_code=base.get("fin_prdt_cd")).first()

                if not product:
                    product = DepositProduct.objects.create(
                        id=base.get("fin_prdt_cd"),
                        financial_company_code=base.get("fin_co_no"),
                        financial_company_name=base.get("kor_co_nm"),
                        financial_product_code=base.get("fin_prdt_cd"),
                        financial_product_name=base.get("fin_prdt_nm"),
                        join_way=base.get("join_way"),
                        dcls_month=base.get("dcls_month"),
                        spcl_cnd=base.get("spcl_cnd"),
                        etc_note=base.get("etc_note"),
                        mtrt_int=base.get("mtrt_int"),
                    )
                    self.stdout.write(f"Created: {product.financial_product_name}")
                else:
                    product.join_way = base.get("join_way", product.join_way)
                    product.dcls_month = base.get("dcls_month", product.dcls_month)
                    product.spcl_cnd = base.get("spcl_cnd", product.spcl_cnd)
                    product.save()
                    self.stdout.write(f"Updated: {product.financial_product_name}")

            option_list = data.get("result", {}).get("optionList", [])
            for option in option_list:
                product = DepositProduct.objects.filter(financial_product_code=option.get("fin_prdt_cd")).first()

                if product:
                    product.basic_interest_rate = self.get_decimal_value(option.get("intr_rate"))
                    product.max_interest_rate = self.get_decimal_value(option.get("intr_rate2"))
                    product.save()

            current_page += 1
            max_page = data.get("result", {}).get("max_page_no", current_page)
            if current_page > max_page:
                break

    def get_decimal_value(self, value):
        if value is None or value == "":
            return None
        try:
            return Decimal(value)
        except (InvalidOperation, ValueError) as e:
            self.stderr.write(f"Invalid decimal value '{value}': {e}")
            return None
