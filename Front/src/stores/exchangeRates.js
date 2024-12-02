import { defineStore } from 'pinia';
import axios from 'axios';

export const useExchangeRatesStore = defineStore('exchangeRates', {
  state: () => ({
    rates: [], // 환율 데이터 저장
    loading: false, // 로딩 상태 관리
    error: null, // 에러 메시지
  }),
  getters: {
    getCurrencies(state) {
      return state.rates.map((rate) => ({
        code: rate.cur_unit,
        name: rate.cur_nm,
      }));
    },
  },
  actions: {
    async fetchRates() {
      this.loading = true;
      this.error = null;

      try {
        const token = localStorage.getItem('accessToken');
        if (!token) throw new Error('로그인이 필요합니다.');

        const response = await axios.get('http://127.0.0.1:8000/api/core/actions/exchange-rates/', {
          headers: {
            Authorization: `Token ${token}`, // 인증 토큰 추가
          },
        });

        if (response.data.rates) {
          this.rates = response.data.rates;
        } else {
          throw new Error('응답 데이터가 올바르지 않습니다.');
        }
      } catch (error) {
        console.error('환율 데이터를 가져오는 중 오류 발생:', error);
        this.error = '환율 데이터를 불러올 수 없습니다.';
      } finally {
        this.loading = false;
      }
    },
    getRate(currencyCode) {
      const rate = this.rates.find((rate) => rate.cur_unit === currencyCode);
      return rate ? parseFloat(rate.deal_bas_r) : null;
    },
  },
});
