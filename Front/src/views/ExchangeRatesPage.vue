<template>
  <div class="exchange-rates-page">
    <div class="exchange-rates">
      <h1>실시간 환율 계산기</h1>

      <!-- 환율 기준 -->
      <div class="rate-options">
        <label>
          <input type="radio" v-model="rateType" value="외화 기준" /> 외화 기준
        </label>
        <label>
          <input type="radio" v-model="rateType" value="원화 기준" /> 원화 기준
        </label>
      </div>

      <!-- 통화 및 금액 입력 -->
      <div class="calculation-container">
        <div class="currency-selection">
          <label for="currency">통화 선택:</label>
          <select id="currency" v-model="selectedCurrency">
            <option
              v-for="currency in currencies"
              :key="currency.code"
              :value="currency.code"
            >
              {{ currency.name }} ({{ currency.code }})
            </option>
          </select>
        </div>

        <div class="input-fields">
          <div>
            <label for="foreign-amount">외국 통화:</label>
            <input
              id="foreign-amount"
              type="number"
              v-model.number="foreignAmount"
              :disabled="rateType === '원화 기준'"
              placeholder="외국 통화 입력"
            />
          </div>

          <div>
            <label for="local-amount">원화:</label>
            <input
              id="local-amount"
              type="number"
              v-model.number="localAmount"
              :disabled="rateType === '외화 기준'"
              placeholder="원화 입력"
            />
          </div>
        </div>
      </div>

      <!-- 계산 버튼 -->
      <button class="calculate-button" @click="calculateRate">환율 계산</button>

      <!-- 결과 출력 -->
      <div class="result" v-if="result !== null">
        <p>환전 결과: <strong>{{ result.toFixed(2) }}</strong> {{ resultCurrency }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useExchangeRatesStore } from "@/stores/exchangeRates";

export default {
  setup() {
    const store = useExchangeRatesStore();

    const rateType = ref("외화 기준");
    const selectedCurrency = ref("USD"); // 기본 통화
    const foreignAmount = ref(0); // 외국 통화 금액
    const localAmount = ref(0); // 원화 금액
    const result = ref(null);
    const resultCurrency = ref(""); // 결과 통화 단위

    const currencies = computed(() => store.getCurrencies);
    const loading = computed(() => store.loading);
    const error = computed(() => store.error);

    // 환율 계산 함수
    const calculateRate = () => {
      const rate = store.getRate(selectedCurrency.value);
      if (rate !== null) {
        if (rateType.value === "외화 기준") {
          result.value = foreignAmount.value * rate;
          resultCurrency.value = "원";
        } else {
          result.value = localAmount.value / rate;
          resultCurrency.value = selectedCurrency.value;
        }
      } else {
        alert("선택한 통화의 환율 정보를 찾을 수 없습니다.");
      }
    };

    onMounted(() => {
      store.fetchRates();
    });

    return {
      rateType,
      selectedCurrency,
      foreignAmount,
      localAmount,
      result,
      resultCurrency,
      currencies,
      calculateRate,
      loading,
      error,
    };
  },
};
</script>

<style scoped>
.exchange-rates-page {
  /* 배경 이미지 */
  background-image: url('@/assets/exchangePage.jpg');
  background-size: 2150px 1100px;
  background-position: center;
  background-repeat: no-repeat;
  height: 100vh; /* 화면 전체 높이 */
  display: flex;
  justify-content: center;
  align-items: center;
}

.exchange-rates {
  padding: 20px;
  max-width: 600px;
  background: rgba(0, 0, 0, 0.5); /* 반투명 검정 배경 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  font-family: "Roboto", sans-serif;
  color: #ffffff;
  width: 100%;
}

h1 {
  font-size: 2rem;
  color: #ffffff;
  text-align: center;
  margin-bottom: 20px;
}

.rate-options {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 20px;
}

.rate-options label {
  font-size: 1rem;
  color: #dddddd;
  cursor: pointer;
}

.currency-selection {
  margin-bottom: 20px;
}

.currency-selection label {
  font-size: 1rem;
  font-weight: 500;
  margin-right: 10px;
}

.currency-selection select {
  padding: 10px;
  width: 100%;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  background: #f9f9f9;
}

.input-fields {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
}

.input-fields div {
  flex: 1;
}

.input-fields label {
  display: block;
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 8px;
}

.input-fields input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  background: #f9f9f9;
}

.calculate-button {
  width: 100%;
  padding: 15px;
  background: linear-gradient(to right, #5a0eab, #1f5fc8); /* 버튼 그라디언트 색상 */
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.calculate-button:hover {
  background: #0056b3;
}

.result {
  margin-top: 20px;
  padding: 15px;
  background: #e3f2fd;
  border-radius: 8px;
  text-align: center;
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
}
</style>
