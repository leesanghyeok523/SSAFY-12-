import requests
from django.core.management.base import BaseCommand
from core.models import SavingsProduct
from decouple import config
from decimal import Decimal, InvalidOperation


class Command(BaseCommand):
    help = "Fetch savings products from external API and save them to the database."

    def handle(self, *args, **kwargs):
        url = "http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json"
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
                self.stderr.write(f"Response content: {response.text}")
                return

            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError:
                self.stderr.write("The API did not return valid JSON.")
                self.stderr.write(f"Response content: {response.text[:500]}")
                return

            # Process baseList (basic product data)
            base_list = data.get("result", {}).get("baseList", [])
            for base in base_list:
                product = SavingsProduct.objects.filter(financial_product_code=base.get("fin_prdt_cd")).first()

                if not product:
                    # Create a new product
                    product = SavingsProduct.objects.create(
                        id=base.get("fin_prdt_cd"),  # Use the financial product code as the primary key
                        financial_company_code=base.get("fin_co_no", "Unknown"),
                        financial_company_name=base.get("kor_co_nm", "Unknown"),
                        financial_product_code=base.get("fin_prdt_cd", "Unknown"),
                        financial_product_name=base.get("fin_prdt_nm", "Unknown"),
                        join_way=base.get("join_way", "N/A"),
                        mtrt_int=base.get("mtrt_int", "N/A"),  # 만기 후 이율
                        dcls_month=base.get("dcls_month", "Unknown"),  # 공시제출월
                        spcl_cnd=base.get("spcl_cnd", "N/A"),  # 우대조건
                        etc_note=base.get("etc_note", "N/A"),  # 추가설명
                    )
                    self.stdout.write(f"Created: {product.financial_product_name}")
                else:
                    # Update existing product
                    product.financial_product_name = base.get("fin_prdt_nm", product.financial_product_name)
                    product.join_way = base.get("join_way", product.join_way)
                    product.mtrt_int = base.get("mtrt_int", product.mtrt_int)
                    product.dcls_month = base.get("dcls_month", product.dcls_month)
                    product.spcl_cnd = base.get("spcl_cnd", product.spcl_cnd)
                    product.etc_note = base.get("etc_note", product.etc_note)
                    product.save()
                    self.stdout.write(f"Updated: {product.financial_product_name}")

            # Process optionList (detailed rate data)
            option_list = data.get("result", {}).get("optionList", [])
            for option in option_list:
                product_code = option.get("fin_prdt_cd")
                saving_product = SavingsProduct.objects.filter(financial_product_code=product_code).first()

                if saving_product:
                    saving_product.interest_rate_type = option.get("intr_rate_type", "N/A")
                    saving_product.interest_rate_type_name = option.get("intr_rate_type_nm", "N/A")
                    saving_product.basic_interest_rate = self.get_decimal_value(option.get("intr_rate", 0.0))
                    saving_product.max_interest_rate = self.get_decimal_value(option.get("intr_rate2", 0.0))
                    saving_product.save()

                    self.stdout.write(
                        f"Updated: {saving_product.financial_product_name} - "
                        f"Basic Rate: {saving_product.basic_interest_rate}, Max Rate: {saving_product.max_interest_rate}"
                    )
                else:
                    self.stderr.write(f"Option for product code {product_code} does not have a corresponding SavingsProduct.")

            # Check if more pages exist
            current_page += 1
            max_page = data.get("result", {}).get("max_page_no", current_page)
            if current_page > max_page:
                break

    def get_decimal_value(self, value):
        """
        Convert a value to Decimal if possible, otherwise return None.
        """
        if value is None or value == "":
            return None
        try:
            return Decimal(value)
        except (InvalidOperation, ValueError) as e:
            self.stderr.write(f"Invalid decimal value '{value}': {e}")
            retur
