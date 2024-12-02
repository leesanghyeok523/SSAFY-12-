<template>
  <div class="hero-container">
    <!-- Main Section -->
    <section class="content-section">
      <div class="image-box">
        <img src="@/assets/main-page-bg.jpg" alt="Main Page Background" class="main-image" />
      </div>
      <div class="text-box">
        <p class="sub-heading">
          <span>시간 낭비 없는<br /><span class="highlight-bold">스마트 금융관리</span></span>
        </p>
        <h2>
          <strong>복잡하고 귀찮은 금융</strong>
          <br />
          <span class="highlight-bold">한눈에!!</span>
          <br>
          <span class="highlight">확인</span>하자
        </h2>
      </div>
    </section>

    <section class="image-section">
      <img src="@/assets/banner.jpg" alt="Featured Image" class="featured-image" />
    </section>


    <!-- Services Section -->
    <section class="services-section">
      <div class="divider"></div>
      <div class="services-container">
        <div class="services-header">
          <h3>주요 서비스 소개</h3>
        </div>
        <div class="services-list">
          <div
            class="service-card"
            v-for="(service, index) in services"
            :key="index"
            :class="{ flipped: flippedIndex === index }"
            @click="toggleFlip(index)"
            @mousemove="(e) => handlePointerMove(e, index)"
            @mouseleave="handlePointerOut(index)"
          >
            <div class="card-inner" :style="index === activeIndex ? transformStyle : ''">
              <!-- Front Side -->
              <div class="card-front">
                <div class="card-header">
                  <img :src="service.image" alt="서비스 이미지" class="service-image" />
                </div>
                <p class="card-label">{{ service.name }}</p>
              </div>
              <!-- Back Side -->
              <div class="card-back">
                <p class="card-back-text">{{ service.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>


  </div>
</template>

<script>
import { reactive, ref } from "vue";
import AIImage from "@/assets/AI.jpg";
import exchangeIcon from "@/assets/exchange-icon.jpg";
import savingsIcon from "@/assets/savings-icon.jpg";
import mapIcon from "@/assets/map-icon.jpg";
import recommendIcon from "@/assets/recommend-icon.jpg";

export default {
  name: "HeroSection",
  setup() {
    const services = reactive([
      {
        name: "환율 계산기",
        image: exchangeIcon,
        description: "환율 정보를 제공하는 서비스입니다.",
      },
      {
        name: "예적금 비교",
        image: savingsIcon,
        description: "다양한 예적금 상품을 조회해보고 비교해보세요.",
      },
      {
        name: "AI 보고서",
        image: AIImage,
        description: "AI가 분석한 기업의 분기 보고서입니다.",
      },
      {
        name: "은행 지도",
        image: mapIcon,
        description: "주변의 은행 위치를 쉽게 찾아보세요.",
      },
      {
        name: "추천 금융 상품",
        image: recommendIcon,
        description: "당신에게 맞는 금융 상품을 알고리즘 기반으로 추천합니다.",
      },
    ]);

    const flippedIndex = ref(null);
    const activeIndex = ref(null);
    const transformStyle = ref("");

    const toggleFlip = (index) => {
      flippedIndex.value = flippedIndex.value === index ? null : index;
    };

    const handlePointerMove = (e, index) => {
      if (flippedIndex.value !== index) {
        const card = e.currentTarget;
        const rect = card.getBoundingClientRect();
        const offsetX = e.clientX - rect.left;
        const offsetY = e.clientY - rect.top;
        const rotateY = (offsetX / rect.width - 0.5) * 15;
        const rotateX = (0.5 - offsetY / rect.height) * 15;

        transformStyle.value = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        activeIndex.value = index;
      }
    };

    const handlePointerOut = (index) => {
      if (flippedIndex.value !== index) {
        transformStyle.value = "perspective(1000px) rotateX(0deg) rotateY(0deg)";
        activeIndex.value = null;
      }
    };

    return {
      services,
      flippedIndex,
      activeIndex,
      transformStyle,
      toggleFlip,
      handlePointerMove,
      handlePointerOut,
    };
  },
};
</script>




<style scoped>
/* 전체 컨테이너 */
.hero-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;
  height: 100%;
  background-color: white;
  padding: 120px 10%;
}

/* Background Section */
.background-section {
  width: 100%;
  height: 100vh; /* 화면 전체 높이 */
  background: url("@/assets/exchange-page.jpg") no-repeat center center;
  background-size: cover; /* 이미지가 요소를 꽉 채우도록 설정 */
  margin: 0; /* 여백 제거 */
  padding: 0; /* 패딩 제거 */
}

/* 이미지와 텍스트 섹션 */
.content-section {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: 40px;
  gap: 50px;
}

.image-box {
  flex: 1;
}


/* 이미지와 텍스트 섹션 */
.content-section {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: 40px;
  gap: 50px;
}

.image-box {
  flex: 1;
}

.main-image {
  width: 100%;
  max-width: 1200px;
  border-radius: 20px;
  box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.1);
  object-fit: cover;
}

.text-box {
  flex: 1;
  padding: 30px;
  background-color: white;
  border-radius: 20px;
  max-width: 600px;
  text-align: left;
  margin: 0;
}

.text-box h2 {
  margin-bottom: 20px;
  font-size: 3rem;
  font-weight: 700;
  line-height: 1.;
  color: #333;
}

.text-box p {
  font-size: 1.2rem;
  color: #666;
  line-height: 1.6;
  margin: 10px 0;
}

.highlight {
  color: #007bff;
  font-weight: 600;
}

.highlight-bold {
  color: #0056b3;
  font-weight: 700;
}

.cta-button {
  font-size: 1.2rem;
  margin-top: 20px;
  padding: 12px 24px;
  color: #fff;
  background-color: #007bff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0px 6px 12px rgba(0, 123, 255, 0.2);
}

.cta-button:hover {
  background-color: #0056b3;
  box-shadow: 0px 8px 15px rgba(0, 123, 255, 0.4);
}

/* 주요 서비스 섹션 */
.services-section {
  width: 100%;
  margin-top: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.services-header {
  text-align: center;
  margin-bottom: 30px;
}

.services-header h3 {
  font-size: 2rem;
  font-weight: 700;
  color: #0056b3;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 0;
}

.divider {
  width: 80%;
  height: 1px;
  background-color: #ddd;
  margin: 10px 0;
}

.services-container {
  width: 100%;
  padding: 20px;
  border-radius: 20px;
  background-color: white;
  box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.1);
}

.services-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 20px;
  width: 100%;
}

/* 카드 스타일 */
.service-card {
  width: 220px;
  height: 320px;
  perspective: 1000px;
  position: relative;
}

.card-inner {
  width: 100%;
  height: 100%;
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.6s;
}

.service-card.flipped .card-inner {
  transform: rotateY(180deg);
}

.card-front,
.card-back {
  width: 100%;
  height: 100%;
  position: absolute;
  backface-visibility: hidden;
  border-radius: 15px;
  overflow: hidden;
}

.card-front {
  background: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.card-back {
  background: #f8f9fa;
  transform: rotateY(180deg);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.card-back-text {
  font-size: 1rem;
  color: #333;
  text-align: center;
}

.card-label {
  margin-top: 10px;
  font-size: 1.2rem;
  font-weight: bold;
  text-align: center;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .content-section {
    flex-direction: column;
    gap: 30px;
  }

  .services-list {
    justify-content: center;
  }

  .service-card {
    width: 200px;
    height: 300px;
  }
}

.image-section {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 50px 0;
}

.featured-image {
  width: 100%;
  max-width: 1000x;
  border-radius: 15px;
  box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.1);
}

</style>


