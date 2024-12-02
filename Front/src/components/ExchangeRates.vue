<template>
  <div class="exchange-rates">
    <h1>환율 계산기</h1>
    <div class="calculation-container">
      <!-- 환율 계산 -->
      <div class="rate-options">
        <label>
          <input type="radio" v-model="rateType" value="기준환율" /> 외화 기준
        </label>
        <label>
          <input type="radio" v-model="rateType" value="현찰환율" /> 현찰 기준
        </label>
      </div>

      <CurrencySelector :currencies="currencies" v-model="selectedCurrency" />

      <RateInput v-model:amount="amount" @calculate="handleCalculate" />

      <div class="result" v-if="convertedAmount !== null">
        <p>환전 결과: <strong>{{ convertedAmount }}</strong> {{ selectedCurrency }}</p>
      </div>
    </div>


  </div>
</template>

<script>
import { ref, computed } from "vue";
import CurrencySelector from "./CurrencySelector.vue";
import RateInput from "./RateInput.vue";
import { useExchangeRatesStore } from "@/stores/exchangeRates";


export default {
  components: { CurrencySelector, RateInput, IncomeLevelCal },
  setup() {
    const rateType = ref("기준환율");
    const amount = ref(0);
    const selectedCurrency = ref("USD");
    const store = useExchangeRatesStore();

    const convertedAmount = computed(() => {
      const rate = store.getRate(selectedCurrency.value, rateType.value);
      return rate ? amount.value * rate : null;
    });

    const handleCalculate = () => {
      store.fetchRates();
    };

    return {
      rateType,
      amount,
      selectedCurrency,
      convertedAmount,
      handleCalculate,
    };
  },
};
</script>

<style scoped>
.exchange-rates {
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
  max-width: 600px;
  margin: 0 auto;
}

.calculation-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result {
  padding: 10px;
  background: #e3f2fd;
  border-radius: 5px;
}
</style>
