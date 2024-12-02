<template>
  <section class="independent-section">
    <!-- 버튼 컨테이너 -->
    <div class="button-container">
      <router-link to="/report-summary" class="navigate-button">
        AI에게 기업보고서 요약 받기
      </router-link>
    </div>
  </section>
</template>

<script>
export default {
  name: "IndependentSection",
};
</script>

<style scoped>
.independent-section {
  display: flex;
  justify-content: center; /* 수평 중앙 정렬 */
  align-items: center; /* 수직 중앙 정렬 */
  padding: 0; /* 내부 여백 제거 */
  margin: 0; /* 외부 여백 제거 */
  background: url("@/assets/AIMain.jpg") no-repeat center center;
  background-size: 2100px 950px;
  height: 100vh; /* 화면 전체 높이 */
  width: 100vw; /* 화면 전체 너비 */
  padding-top: 400px;
}

/* 버튼 컨테이너 */
.button-container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  gap: 20px;
}

/* 버튼 스타일 */
.navigate-button {
  display: inline-block;
  padding: 15px 30px;
  font-size: 1.2rem;
  font-weight: bold;
  color: white;
  background: linear-gradient(to right, #2575fc, #25f5fc);
  border: none;
  border-radius: 10px;
  text-decoration: none; /* 텍스트 밑줄 제거 */
  text-align: center;
  transition: background-color 0.3s ease, transform 0.3s ease;
  cursor: pointer;
  box-shadow: 0px 6px 12px rgba(0, 123, 255, 0.2);
  margin-top: 50%;
}

/* 버튼 호버 효과 */
.navigate-button:hover {
  background-color: #0056b3;
  transform: scale(1.05);
  box-shadow: 0px 8px 15px rgba(0, 123, 255, 0.4);
}
</style>
