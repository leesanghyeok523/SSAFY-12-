<template>
  <div class="currency-selector">
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
</template>

<script>
export default {
  props: {
    currencies: {
      type: Array,
      required: true,
    },
    modelValue: {
      type: String,
      required: true,
    },
  },
  emits: ["update:modelValue"],
  computed: {
    selectedCurrency: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit("update:modelValue", value);
      },
    },
  },
};
</script>

<style scoped>
.currency-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

label {
  font-weight: bold;
}

select {
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
</style>
