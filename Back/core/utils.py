# core/utils.py

import numpy as np
import time
import pandas as pd
import OpenDartReader
from .models import Dividend
from django.conf import settings
import openai

# OpenDartReader 초기화
dart = OpenDartReader(settings.DART_API_KEY)  # 환경변수 또는 settings에서 불러오세요.

def find_dividends(stock_name, year):
    """
    특정 주식(stock_name)과 연도(year)의 배당금 정보를 가져옵니다.
    """
    try:
        stock_name_report = dart.report(stock_name, "배당", year, "11011")  # 사업보고서
    except Exception:
        stock_name_report = None

    if stock_name_report is None:
        return np.nan, np.nan, np.nan
    else:
        try:
            # '주당 현금배당금(원)' 필터링
            stock_name_report = stock_name_report.loc[
                stock_name_report['se'] == '주당 현금배당금(원)'
            ]
            thstrm_dividends = int(stock_name_report['thstrm'].replace('-', '0').replace(',', ''))
            frmtrm_dividends = int(stock_name_report['frmtrm'].replace('-', '0').replace(',', ''))
            lwfr_dividends = int(stock_name_report['lwfr'].replace('-', '0').replace(',', ''))

            return lwfr_dividends, frmtrm_dividends, thstrm_dividends
        except Exception:
            return np.nan, np.nan, np.nan


def collect_dividend_data(stock_list, years):
    """
    여러 주식과 연도에 대해 배당금 데이터를 수집합니다.
    """
    data = []
    for idx, stock_name in enumerate(stock_list):
        print(f"Processing {idx + 1}/{len(stock_list)}: {stock_name}")  # 진행 상황 출력
        for year in years:
            lwfr_dividends, frmtrm_dividends, thstrm_dividends = find_dividends(stock_name, year)
            # 데이터베이스 저장
            Dividend.objects.update_or_create(
                stock_name=stock_name,
                year=year,
                defaults={
                    "lwfr_dividends": lwfr_dividends,
                    "frmtrm_dividends": frmtrm_dividends,
                    "thstrm_dividends": thstrm_dividends,
                },
            )
        time.sleep(0.5)  # API 호출 간격 조정
    return True

def split_text_into_chunks(text, chunk_size=2000):
    """
    긴 텍스트를 chunk_size 길이로 나누는 함수
    """
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def clean_text(text):
    """
    텍스트에서 불필요한 공백 및 특정 키워드 제거
    """
    # 공백 정리
    text = ' '.join(text.split())

    # 불필요한 키워드 제거 (예: "참고하시기 바랍니다", "없음")
    filter_keywords = ["참고하시기 바랍니다", "없음"]
    for keyword in filter_keywords:
        text = text.replace(keyword, "")

    return text



# GPT 요약 함수
def summarize_business_data(report_content):
    """
    GPT API를 사용하여 'II. 사업의 내용'을 요약
    """
    try:
        openai.api_key = settings.OPENAI_API_KEY

        # 1. 텍스트 정제
        cleaned_content = clean_text(report_content)

        # 2. 텍스트를 나눔
        chunks = split_text_into_chunks(cleaned_content, chunk_size=2000)

        summaries = []
        for chunk in chunks:
            # 3. 각 청크별 GPT 요청
            messages = [
                {"role": "system", "content": "You are a financial report summarization assistant."},
                {
                    "role": "user",
                    "content": f"""
                    아래는 기업의 'II. 사업의 내용' 중 일부입니다. 이를 요약해 주세요:

                    {chunk}
                    """
                }
            ]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # 모델 설정 확인
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )
            summaries.append(response['choices'][0]['message']['content'].strip())

        # 4. 나뉜 요약을 하나로 합침
        return "<br>".join(summaries)

    except Exception as e:
        return f"GPT 요약 중 오류 발생: {str(e)}"

def calculate_income_ratio_and_atmosphere(income_level, family_size):
    # 하드코딩된 중위소득 데이터
    median_income = {
        1: 2228445,
        2: 3682609,
        3: 4714657,
        4: 5729913,
        5: 6695735,
        6: 7618369,
    }

    if family_size not in median_income:
        raise ValueError("지원되지 않는 가구원 수입니다.")

    # 중위소득 계산
    median = median_income[family_size]

    # 소득 비율 계산
    income_ratio = (income_level / 12) / median * 100

    # 분위 계산
    if income_ratio <= 30:
        income_atmosphere = "1분위"
    elif income_ratio <= 50:
        income_atmosphere = "2분위"
    elif income_ratio <= 70:
        income_atmosphere = "3분위"
    elif income_ratio <= 90:
        income_atmosphere = "4분위"
    elif income_ratio <= 100:
        income_atmosphere = "5분위"
    elif income_ratio <= 130:
        income_atmosphere = "6분위"
    elif income_ratio <= 150:
        income_atmosphere = "7분위"
    elif income_ratio <= 200:
        income_atmosphere = "8분위"
    elif income_ratio <= 300:
        income_atmosphere = "9분위"
    else:
        income_atmosphere = "10분위"

    return income_ratio, income_atmosphere