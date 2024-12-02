<!-- Front/src/views/IncomeLevelCal.vue -->

<template>
  <div class="income-calculator">
    <h1>소득 계산기</h1>
    <div class="form-group">
      <label for="income-level">연 소득 (원):</label>
      <input
        id="income-level"
        type="number"
        v-model="incomeLevel"
        placeholder="연 소득을 입력하세요"
      />
    </div>

    <div class="form-group">
      <label for="family-size">가구원 수:</label>
      <input
        id="family-size"
        type="number"
        v-model="familySize"
        placeholder="가구원 수를 입력하세요"
      />
    </div>

    <button @click="calculateIncomeLevel" class="calculate-button">
      계산하기
    </button>

    <div v-if="calculatedData" class="result-section">
      <h2>계산 결과</h2>
      <p><strong>연 소득:</strong> {{ calculatedData.income_level.toLocaleString() }}원</p>
      <p><strong>중위소득 비율:</strong> {{ calculatedData.income_ratio.toFixed(2) }}%</p>
      <p><strong>소득 분위:</strong> {{ calculatedData.income_atmosphere }}</p>
    </div>

    <div class="form-group">
      <label for="save-income">연 소득 저장:</label>
      <input
        id="save-income"
        type="number"
        v-model="incomeLevelToSave"
        placeholder="저장할 연 소득을 입력하세요"
      />
    </div>

    <button @click="saveIncomeLevel" class="save-button">소득 저장</button>

    <div v-if="saveSuccess" class="success-message">
      소득이 성공적으로 저장되었습니다!
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";

const incomeLevel = ref(null); // 사용자가 입력한 연 소득
const familySize = ref(1); // 사용자가 입력한 가구원 수
const calculatedData = ref(null); // 계산된 결과 저장
const incomeLevelToSave = ref(null); // 저장할 연 소득
const saveSuccess = ref(false); // 저장 성공 메시지

const calculateIncomeLevel = async () => {
  if (!incomeLevel.value || !familySize.value) {
    alert("연 소득과 가구원 수를 모두 입력해주세요.");
    return;
  }

  try {
    const response = await axios.get("http://127.0.0.1:8000/api/core/actions/income-ratio/", {
      headers: { Authorization: `Token ${localStorage.getItem("accessToken")}` },
      params: { family_size: familySize.value, income_level: incomeLevel.value },
    });

    calculatedData.value = response.data;
  } catch (error) {
    console.error("소득 계산 중 오류 발생:", error);
    alert("소득 계산에 실패했습니다.");
  }
};

const saveIncomeLevel = async () => {
  if (!incomeLevelToSave.value) {
    alert("저장할 연 소득을 입력해주세요.");
    return;
  }

  try {
    await axios.post(
      "http://127.0.0.1:8000/api/core/actions/income-ratio/",
      { income_level: incomeLevelToSave.value, family_size: familySize.value },
      { headers: { Authorization: `Token ${localStorage.getItem("accessToken")}` } }
    );

    saveSuccess.value = true;
    setTimeout(() => {
      saveSuccess.value = false;
    }, 3000); // 3초 후 성공 메시지 숨김
  } catch (error) {
    console.error("소득 저장 중 오류 발생:", error);
    alert("소득 저장에 실패했습니다.");
  }
};

</script>


<style>
body {
  margin: 0; /* 기본 여백 제거 */
  padding: 0; /* 기본 패딩 제거 */
  font-family: Arial, sans-serif; /* 기본 폰트 설정 */
  background-image: url('@/assets/profile.jpg'); /* 배경 이미지 추가 */
  background-size: 2000px 950px; /* 배경 이미지를 화면 전체에 맞춤 */
  background-position: center; /* 이미지를 중앙 정렬 */
  background-repeat: no-repeat; /* 이미지 반복 방지 */
  background-attachment: fixed; /* 스크롤 시 배경 고정 */
  color: #fff; /* 기본 텍스트 색상을 흰색으로 설정 */
}
</style>


<style scoped>

.income-calculator {
  font-family: Arial, sans-serif;
  max-width: 700px; /* 계산기 전체 너비를 확장 */
  margin: 100px auto; /* 위쪽 여백과 중앙 정렬 유지 */
  padding: 60px; /* 내부 여백을 늘려 크기 확장 */
  border: 1px solid rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  background-color: rgba(0, 0, 0, 0.7);
  color: #fff;
}

h1 {
  font-size: 2.5rem; /* 제목 크기를 키움 */
  text-align: center;
  margin-bottom: 30px;
}

input {
  width: 100%;
  padding: 12px; /* 입력 필드 크기를 늘림 */
  border: 1px solid #ccc;
  border-radius: 6px;
  box-sizing: border-box;
  font-size: 1.2rem; /* 입력 텍스트 크기를 확대 */
  background-color: #f9f9f9; /* 기본 배경색 */
  transition: background-color 0.3s ease, border-color 0.3s ease; /* 부드러운 전환 효과 */
}

input:focus {
  background-color: #ffffff; /* 포커스 상태에서 흰색 배경 */
  border-color: #007bff; /* 포커스 상태에서 테두리 색상 변경 */
  outline: none; /* 기본 outline 제거 */
}


.form-group {
  margin-bottom: 20px; /* 입력 필드 사이의 간격 설정 */
}

button {
  display: block;
  width: 100%;
  padding: 14px; /* 버튼 크기 */
  margin-bottom: 20px; /* 버튼과 다음 요소 사이 간격 */
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 8px; /* 버튼 모서리를 둥글게 */
  font-size: 1.4rem; /* 버튼 텍스트 크기 */
  cursor: pointer;
  text-align: center;
}

button:hover {
  background-color: #0056b3;
}

.result-section {
  margin-top: 30px; /* 결과 섹션과 버튼 사이의 간격 확대 */
  padding: 20px; /* 내부 여백 */
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.1);
  font-size: 1.2rem;
}

</style>
