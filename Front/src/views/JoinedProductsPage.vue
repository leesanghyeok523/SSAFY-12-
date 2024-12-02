<template>
  <div class="joined-products-page">
    <div class="navigation">
      <span @click="goToProfile" class="nav-link">회원 정보 관리</span>
    </div>
    <h1>{{ username }}님의 가입한 상품</h1>

    <div v-if="joinedProducts.length > 0" class="cards-container">
      <div
        v-for="product in joinedProducts"
        :key="product.id"
        class="card"
        @pointermove="handlePointerMove"
        @pointerout="handlePointerOut"
      >
        <div class="overlay"></div>
        <div class="dark-overlay"></div>
        <div class="card-content">
          <h3>{{ product.name }}</h3>
          <p>은행: {{ product.company || "정보 없음" }}</p>
          <p>기본 이율: {{ product.interest_rate || "정보 없음" }}%</p>
          <p>최대 이율: {{ product.max_interest_rate || "정보 없음" }}%</p>
          <p>공시 제출월: {{ product.dcls_month || "정보 없음" }}</p>
          <button class="detail-button" @click="openDetail(product)">
            상세보기
          </button>
        </div>
      </div>
    </div>
    <div v-else>
      <p>가입한 금융 상품이 없습니다.</p>
    </div>

    <!-- 상세보기 모달 -->
    <div v-if="selectedProduct" class="detail-modal">
      <div class="modal-content">
        <button class="close-button" @click="closeDetail">✕</button>
        <h1 class="modal-title">{{ selectedProduct.name || "상품명 없음" }}</h1>
        <table class="modal-table">
          <tbody>
            <tr>
              <th>은행명</th>
              <td>{{ selectedProduct.company || "정보 없음" }}</td>
            </tr>
            <tr>
              <th>기본 이율</th>
              <td>{{ selectedProduct.interest_rate || "정보 없음" }}%</td>
            </tr>
            <tr>
              <th>최대 이율</th>
              <td>{{ selectedProduct.max_interest_rate || "정보 없음" }}%</td>
            </tr>
            <tr>
              <th>공시 제출월</th>
              <td>{{ selectedProduct.dcls_month || "정보 없음" }}</td>
            </tr>
            <tr>
              <th>추가 설명</th>
              <td>{{ selectedProduct.etc_note || "정보 없음" }}</td>
            </tr>
          </tbody>
        </table>
        <button class="remove-button" @click="removeProduct(selectedProduct.id, selectedProduct.type)">
          해지하기
        </button>
      </div>
    </div>
  </div>
</template>


<script>
import axios from "axios";

export default {
  data() {
    return {
      username: "사용자",
      joinedProducts: [],
      selectedProduct: null,
    };
  },
  methods: {
    async fetchJoinedProducts() {
      try {
        const response = await axios.get(
          "http://127.0.0.1:8000/api/core/actions/joined-products/",
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("accessToken")}`,
            },
          }
        );
        this.joinedProducts = response.data.joined_products.deposits.concat(
          response.data.joined_products.savings
        );
      } catch (error) {
        console.error("가입한 상품 데이터를 가져오는 중 오류 발생:", error);
        alert("데이터를 불러오지 못했습니다. 다시 시도해주세요.");
      }
    },
    async removeProduct(productId, productType) {
      try {
        await axios.post(
          "http://127.0.0.1:8000/api/core/actions/remove-product/",
          {
            product_id: productId,
            product_type: productType,
          },
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("accessToken")}`,
            },
          }
        );
        this.joinedProducts = this.joinedProducts.filter(
          (product) => product.id !== productId
        );
        alert("상품이 해지되었습니다.");
        this.closeDetail();
      } catch (error) {
        console.error("상품 해지 중 오류 발생:", error);
        alert("상품 해지에 실패했습니다. 다시 시도해주세요.");
      }
    },
    handlePointerMove(e) {
      const card = e.currentTarget;
      const rect = card.getBoundingClientRect();
      const offsetX = e.clientX - rect.left;
      const offsetY = e.clientY - rect.top;
      const rotateY = (offsetX / rect.width - 0.5) * 20;
      const rotateX = (0.5 - offsetY / rect.height) * 20;
      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    },
    handlePointerOut(e) {
      e.currentTarget.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg)";
    },
    openDetail(product) {
      this.selectedProduct = product;
    },
    closeDetail() {
      this.selectedProduct = null;
    },
    goToProfile() {
      window.location.href = "/profile";
    },
  },
  mounted() {
    this.username = localStorage.getItem("username") || "사용자";
    this.fetchJoinedProducts();
  },
};
</script>


<style scoped>
.joined-products-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding-top: 85px;
  background-color: #121212;
  color: white;
}

.navigation {
  margin-bottom: 20px;
}

.nav-link {
  cursor: pointer;
  color: white;
  text-decoration: underline;
  margin-bottom: 10px;
  padding-top: 15px;
  font-size: 1.5rem;
}

.cards-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
}

.card {
  width: 250px;
  height: 350px;
  background: linear-gradient(145deg, #333333, #222222);
  color: white;
  border-radius: 15px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5);
  perspective: 1000px;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7);
}

.card-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
  padding: 20px;
}

.detail-button {
  padding: 10px 20px;
  font-size: 1rem;
  color: white;
  background: linear-gradient(to right, #6a11cb, #2575fc);
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.detail-button:hover {
  background: linear-gradient(to right, #5a0eab, #1f5fc8);
}

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
}

.modal-content {
  background: #ffffff;
  color: #000000;
  padding: 30px;
  border-radius: 15px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  position: relative;
}

.close-button {
  position: absolute;
  top: 15px;
  right: 15px;
  font-size: 1.5rem;
  background: none;
  color: black;
  border: none;
  cursor: pointer;
}

.close-button:hover {
  color: red;
}

.remove-button {
  margin-top: 20px;
  padding: 10px 20px;
  font-size: 1rem;
  color: white;
  background: linear-gradient(to right, #6a11cb, #2575fc);
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.remove-button:hover {
  background: linear-gradient(to right, #5a0eab, #1f5fc8);
}

</style>