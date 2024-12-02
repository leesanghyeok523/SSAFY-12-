<template>
  <div class="savings-comparison-page">
    <h1>예적금 상품 조회</h1>
    <p>다양한 예적금 상품을 비교해 보세요.</p>

    <!-- 필터 버튼 -->
    <div class="filter-buttons">
      <button :class="{ active: selectedType === 'deposit' }" @click="setType('deposit')">예금</button>
      <button :class="{ active: selectedType === 'saving' }" @click="setType('saving')">적금</button>
    </div>

    <!-- 검색 입력 필드 -->
    <div class="search-bar">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="은행명을 입력하세요"
        class="search-input"
      />
    </div>

    <!-- 카드 컨테이너 -->
    <div class="cards-container">
      <div
        v-for="item in filteredProducts"
        :key="item.financial_product_code"
        class="card"
        @pointermove="handlePointerMove($event)"
        @pointerout="handlePointerOut"
      >
        <div class="overlay"></div>
        <div class="dark-overlay"></div>
        <div class="card-content">
          <h3>{{ item.financial_product_name || "상품명 없음" }}</h3>
          <p>은행명: {{ item.financial_company_name || "은행명 없음" }}</p>
          <p>기본 이율: {{ item.basic_interest_rate || "정보 없음" }}</p>
          <p>최대 이율: {{ item.max_interest_rate || "정보 없음" }}</p>
          <p>가입 방법: {{ item.join_way || "정보 없음" }}</p>
          <v-btn
            :disabled="item.alreadyJoined"
            color="success"
            @click="openDetail(item)"
          >
            {{ item.alreadyJoined ? "이미 가입됨" : "가입하기" }}
          </v-btn>
        </div>
      </div>
    </div>

    <!-- 상세보기 모달 -->
    <div v-if="selectedProduct" class="detail-modal">
      <div class="modal-content">
        <button class="close-button" @click="closeDetail">✕</button>
        <h1 class="modal-title">{{ selectedProduct.financial_product_name || "상품명 없음" }} 상세정보</h1>
        <table class="modal-table">
          <tbody>
            <tr>
              <th>은행명</th>
              <td>{{ selectedProduct.financial_company_name || "은행명 없음" }}</td>
            </tr>
            <tr>
              <th>기본 이율</th>
              <td>{{ selectedProduct.basic_interest_rate ? `${selectedProduct.basic_interest_rate}%` : "정보 없음" }}</td>
            </tr>
            <tr>
              <th>최대 이율</th>
              <td>{{ selectedProduct.max_interest_rate ? `${selectedProduct.max_interest_rate}%` : "정보 없음" }}</td>
            </tr>
            <tr>
              <th>가입 방법</th>
              <td>{{ selectedProduct.join_way || "정보 없음" }}</td>
            </tr>
            <tr>
              <th>우대조건</th>
              <td>{{ selectedProduct.spcl_cnd || "정보 없음" }}</td>
            </tr>
            <tr>
              <th>만기 후 이율</th>
              <td>{{ selectedProduct.mtrt_int || "정보 없음" }}</td>
            </tr>
            <tr>
              <th>추가설명</th>
              <td>{{ selectedProduct.etc_note || "정보 없음" }}</td>
            </tr>
          </tbody>
        </table>
        <v-btn
          v-if="!selectedProduct.alreadyJoined"
          class="join-button"
          @click="joinProduct"
        >
          가입하기
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useSavingsStore } from "@/stores/savings";
import axios from "axios";

export default {
  setup() {
    const savingsStore = useSavingsStore();
    const selectedType = ref("saving");
    const searchQuery = ref("");
    const selectedProduct = ref(null);
    const joinedProductIds = ref(new Set());

    // 가입한 상품 ID 가져오기
    const fetchJoinedProducts = async () => {
      try {
        const { data } = await axios.get(
          "http://127.0.0.1:8000/api/core/actions/joined-products/",
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("accessToken")}`,
            },
          }
        );

        const deposits = data.joined_products.deposits.map((p) => p.id);
        const savings = data.joined_products.savings.map((p) => p.id);

        joinedProductIds.value = new Set([...deposits, ...savings]);
      } catch (error) {
        console.error("가입한 상품 데이터를 가져오지 못했습니다:", error);
      }
    };

    // 상품 필터링
    const filteredProductsByType = computed(() =>
      selectedType.value === "deposit"
        ? savingsStore.deposits
        : savingsStore.savings
    );

    const filteredProducts = computed(() => {
      const query = searchQuery.value.toLowerCase();
      return filteredProductsByType.value.map((product) => ({
        ...product,
        alreadyJoined: joinedProductIds.value.has(product.id),
      })).filter((product) =>
        product.financial_company_name?.toLowerCase().includes(query)
      );
    });

    const setType = (type) => {
      selectedType.value = type;
    };

    const openDetail = (product) => {
      selectedProduct.value = product;
    };

    const closeDetail = () => {
      selectedProduct.value = null;
    };

    const joinProduct = async () => {
  if (!selectedProduct.value || !selectedProduct.value.financial_product_code) {
    alert("상품 ID가 유효하지 않습니다.");
    return;
  }

  const productId = selectedProduct.value.financial_product_code;
  const productType = selectedType.value === "deposit" ? "deposit" : "savings";

  console.log("가입 요청 데이터:", { product_id: productId, product_type: productType });

  try {
    const response = await axios.post(
      "http://127.0.0.1:8000/api/core/actions/join-product/",
      { product_id: productId, product_type: productType },
      {
        headers: {
          Authorization: `Token ${localStorage.getItem("accessToken")}`,
        },
      }
    );
    console.log("응답 데이터:", response.data);
    alert(`${selectedProduct.value.financial_product_name}에 가입이 완료되었습니다!`);
    closeDetail();
  } catch (error) {
    console.error("가입 요청 중 오류 발생:", error);
    console.error("응답 데이터:", error.response?.data);
    alert("가입에 실패했습니다. 다시 시도해 주세요.");
  }
};






    const handlePointerMove = (e) => {
      const card = e.currentTarget;
      const rect = card.getBoundingClientRect();
      const offsetX = e.clientX - rect.left;
      const offsetY = e.clientY - rect.top;
      const rotateY = (offsetX / rect.width - 0.5) * 30;
      const rotateX = (0.5 - offsetY / rect.height) * 30;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    };

    const handlePointerOut = (e) => {
      const card = e.currentTarget;
      card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg)";
    };

    onMounted(async () => {
      await fetchJoinedProducts();
      await savingsStore.fetchSavingsData();
    });

    return {
      selectedType,
      searchQuery,
      filteredProducts,
      selectedProduct,
      setType,
      openDetail,
      closeDetail,
      joinProduct,
      handlePointerMove,
      handlePointerOut,
    };
  },
};
</script>


<style scoped>
/* 기존 스타일 유지 */
.savings-comparison-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20px;
  padding-top: 100px;
  font-family: "Roboto", sans-serif;
  background: linear-gradient(to right, #6a11cb, #2575fc);
  color: #ffffff;
}

h1 {
  font-size: 2.5rem;
  color: black;
  margin-bottom: 10px;
}

p {
  font-size: 1rem;
  color: #eee;
  margin-bottom: 20px;
}

/* 필터 버튼 스타일 */
.filter-buttons {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.filter-buttons button {
  padding: 10px 20px;
  font-size: 1rem;
  color: white;
  background: linear-gradient(to right, #6a11cb, #2575fc);
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.filter-buttons button.active {
  background: #0056b3;
  font-weight: bold;
}

.filter-buttons button:hover {
  background: linear-gradient(to right, #5a0eab, #1f5fc8);
}

/* 검색 입력 필드 */
.search-bar {
  margin-bottom: 20px;
}

.search-input {
  width: 300px;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #ffffff;
  color: #000;
  outline: none;
  transition: box-shadow 0.2s ease;
}

.search-input::placeholder {
  color: #888;
}

.search-input:focus {
  box-shadow: 0 0 5px #6a11cb;
  border-color: #6a11cb;
}

/* 카드 컨테이너 */
.cards-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
  margin-top: 20px;
}

/* 카드 스타일 */
.card {
  width: 250px;
  height: 350px;
  background: linear-gradient(145deg, #212121, #101010);
  color: white;
  border-radius: 15px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5);
  perspective: 1000px;
  transform-style: preserve-3d;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.card .overlay {
  position: absolute;
  width: 100%;
  height: 100%;
  background: linear-gradient(120deg, rgba(255, 255, 255, 0.3), transparent);
  z-index: 1;
}

.card .dark-overlay {
  position: absolute;
  width: 100%;
  height: 100%;
  background: linear-gradient(150deg, rgba(50, 50, 50, 1) 0%, rgba(20, 20, 20, 1) 100%);
  z-index: 0;
}

.card-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* 콘텐츠 간 간격 균등 배분 */
  align-items: center;
  height: 100%; /* 카드 높이에 맞게 설정 */
  padding: 20px; /* 내부 여백 추가 */
}

.card-content h3,
.card-content p {
  margin: 10px 0; /* 요소 간 일정한 간격 */
}

.card-content p {
  font-size: 0.9rem;
}

.card-content v-btn {
  margin-top: auto; /* 버튼을 카드 하단에 고정 */
  width: 100%; /* 버튼 너비를 카드에 맞게 설정 */
  padding: 10px 15px; /* 버튼 내부 여백 */
  font-size: 1rem; /* 버튼 텍스트 크기 */
  text-align: center;
}

/* 모달 스타일 */
.detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  max-width: 600px; /* 고정된 가로 크기 */
  width: 100%;
  background: rgba(50, 50, 50, 0.95);
  padding: 20px 30px;
  border-radius: 12px;
  color: white;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow-y: auto; /* 세로 스크롤 활성화 */
  overflow-x: hidden; /* 가로 스크롤 비활성화 */
  max-height: 80vh; /* 최대 높이 설정 */
  word-wrap: break-word;
  word-break: break-word;
  white-space: normal;
}

.modal-table {
  width: 100%;
  table-layout: fixed; /* 고정된 테이블 레이아웃 */
  border-spacing: 5px; /* 테이블 셀 간격 조정 */
}

.modal-table th,
.modal-table td {
  padding: 5px 10px; /* 세로와 가로 간격 줄이기 */
  text-align: left;
  font-size: 1rem;
  word-wrap: break-word; /* 텍스트 줄바꿈 */
  word-break: break-word; /* 긴 단어 강제 줄바꿈 */
  white-space: normal; /* 텍스트가 한 줄로 고정되지 않도록 설정 */
}

.modal-title {
  font-size: 1.8rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 10px; /* 타이틀과 테이블 간 간격 조정 */
  color: white;
}

.join-button {
  margin-top: 20px;
  padding: 10px 20px;
  font-size: 1rem;
  font-weight: bold;
  color: white;
  background: linear-gradient(to right, #6a11cb, #2575fc);
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.join-button:hover {
  background: linear-gradient(to right, #5a0eab, #1f5fc8);
}

hr {
  margin: 10px 0;
  border: 0;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.close-button {
  position: absolute;
  top: 10px;
  right: 15px;
  background: none;
  color: white;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.close-button:hover {
  color: red;
}


</style>
