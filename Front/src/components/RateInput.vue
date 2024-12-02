<template>
  <div class="rate-input">
    <label for="amount">환전 금액:</label>
    <input
      id="amount"
      type="number"
      v-model="localAmount"
      placeholder="금액 입력"
    />
  </div>
</template>

<script>
export default {
  props: {
    modelValue: {
      type: Number,
      required: true,
    },
  },
  emits: ["update:modelValue"],
  computed: {
    localAmount: {
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
.rate-input {
  display: flex;
  align-items: center;
  gap: 10px;
}

label {
  font-weight: bold;
}

input {
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
  width: 100%;
}
</style>
