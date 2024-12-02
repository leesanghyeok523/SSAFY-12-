<template>
  <div class="recommendations-page">
    <v-tabs class="mb-8 mt-10 custom-bg" variant="outlined" divided>
      <!-- <v-tab @click="fetchRecommendations('user')">나와 비슷한 사용자 추천 상품</v-tab> -->
      <v-tab @click="fetchRecommendations('age')">
        {{ age ? `${age}대 추천 상품` : '추천 상품 불러오는 중...' }}
      </v-tab>
      <v-tab @click="fetchTopProducts">가장 많이 가입된 상품</v-tab>
    </v-tabs>
    
    <!-- 로딩 스피너 -->
    <v-progress-circular v-if="isLoading" indeterminate color="primary" class="my-8"></v-progress-circular>

    <!-- 에러 메시지 -->
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>

    <!-- 추천 리스트 -->
    <v-data-table
      v-if="!isLoading && recommendations.length > 0"
      :items="recommendations"
      class="elevation-2"
      :headers="tableHeaders"
      item-value="상품명"
      dense
      fixed-header
      height="400px"
    >
      <template v-slot:item.action="{ item }">
        <v-btn @click="showDetails(item)" color="primary">상세 보기</v-btn>
        <v-btn @click="joinProduct(item)" color="success">가입</v-btn>
      </template>
    </v-data-table>

    <!-- 데이터 없음 메시지 -->
    <div v-if="!isLoading && recommendations.length === 0" class="no-data">
      <p>추천 데이터가 없습니다.</p>
    </div>

    <!-- 상품 상세 정보 -->
    <v-dialog v-model="dialog" max-width="600px">
      <v-card>
        <v-card-title>{{ selectedProduct.상품명 }}</v-card-title>
        <v-card-text>
          <p>은행: {{ selectedProduct.은행 }}</p>
          <p>유형: {{ selectedProduct.유형 }}</p>
          <p>최대 금리: {{ selectedProduct.최대금리 }}%</p>
          <p>가입 방법: {{ selectedProduct.가입방법 }}</p>
          <p>특별 조건: {{ selectedProduct.특별조건 }}</p>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="dialog = false" color="primary">닫기</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useUserStore } from '@/stores/user'; // Pinia Store import

// API Base URL
const API_BASE_URL = 'http://127.0.0.1:8000/api/core/actions/';

const userStore = useUserStore();
const recommendations = ref([]);
const isLoading = ref(false);
const error = ref(null);
const dialog = ref(false);
const selectedProduct = ref({});

// userProfile 데이터가 없을 경우를 대비하여 기본값 처리
const age = computed(() => {
  return userStore.userProfile.age
    ? Math.floor(userStore.userProfile.age / 10) * 10
    : null;
});

// 테이블 헤더
const tableHeaders = [
  { text: '상품명', value: '상품명' },
  { text: '은행', value: '은행' },
  { text: '유형', value: '유형' },
  { text: '최대 금리', value: '최대금리' },
  { text: '가입 방법', value: '가입방법' },
  { text: '특별 조건', value: '특별조건' },
  { text: '액션', value: 'action', sortable: false },
];

// 공통 헤더 함수
const getAuthHeaders = () => {
  const token = localStorage.getItem('accessToken');
  if (!token) {
    console.error('토큰이 없습니다. 로그인이 필요합니다.');
    alert('로그인이 필요합니다.');
    throw new Error('인증 토큰이 없습니다.');
  }
  return { Authorization: `Token ${token}` };
};

// 추천 데이터 가져오기
const fetchRecommendations = (type) => {
  console.log(`Fetching ${type}-based recommendations...`);
  isLoading.value = true;
  error.value = null;

  // API 경로 결정
  const endpoint =
    type === 'user'
      ? `recommend/deposit/${userStore.userProfile.username}/`
      : `recommend/deposit/age/${userStore.userProfile.username}/`;

  const requestUrl = `${API_BASE_URL}${endpoint}`;
  console.log('Request URL:', requestUrl);

  axios
    .get(requestUrl, { headers: getAuthHeaders() })
    .then((response) => {
      console.log('Response Data:', response.data);

      if (Array.isArray(response.data)) {
        recommendations.value = response.data.map((item) => ({
          상품명: item.financial_product_name,
          은행: item.financial_company_name,
          유형: type === 'user' ? '사용자 기반' : '연령 기반',
          최대금리: item.max_interest_rate,
          가입방법: item.join_way || 'N/A',
          특별조건: item.spcl_cnd || '없음',
        }));
      } else {
        throw new Error('API가 올바른 데이터를 반환하지 않았습니다.');
      }
    })
    .catch((err) => {
      console.error(err);
      error.value = '추천 데이터를 불러오는 중 문제가 발생했습니다.';
    })
    .finally(() => {
      isLoading.value = false;
    });
};

// 가장 많이 가입된 상품 데이터 가져오기
const fetchTopProducts = () => {
  console.log('Fetching top joined products...');
  isLoading.value = true;

  axios
    .get(`${API_BASE_URL}top-joined-products/`, {
      headers: getAuthHeaders(),
    })
    .then((response) => {
      console.log('Response Data:', response.data);

      // 응답 데이터가 객체인지 확인
      if (response.data && response.data.top_joined_products) {
        recommendations.value = response.data.top_joined_products.map((item) => ({
          상품명: item.name,
          은행: item.company,
          유형: item.type === "savings" ? "적금" : "예금",
          가입수: item.join_count,
        }));
      } else {
        console.error('API 응답 데이터가 예상 형식이 아님:', response.data);
        alert('API가 올바른 데이터를 반환하지 않았습니다.');
      }
    })
    .catch((error) => {
      console.error('Error fetching top products:', error);
      alert('상품 데이터를 가져오는 중 문제가 발생했습니다.');
    })
    .finally(() => {
      isLoading.value = false;
    });
};

// 가입 요청
const joinProduct = (item) => {
  console.log('가입 요청:', item.상품명);
  axios
    .post(
      `${API_BASE_URL}join-product/`,
      { product_id: item.id, product_type: 'deposit' }, // 적절한 유형 전달
      { headers: getAuthHeaders() }
    )
    .then(() => {
      alert(`${item.상품명} 가입 완료!`);
    })
    .catch((error) => {
      console.error('가입 실패:', error);
      alert('상품 가입 중 문제가 발생했습니다.');
    });
};

// 상세 보기
const showDetails = (item) => {
  selectedProduct.value = item;
  dialog.value = true;
};

// 컴포넌트 로드 시 사용자 프로필 확인 후 데이터 가져오기
onMounted(() => {
  console.log('컴포넌트 로드됨, 프로필 가져오기 시작');
  if (!userStore.userProfile.username) {
    userStore
      .fetchUserProfile()
      .then(() => {
        console.log('프로필 가져오기 완료');
        fetchRecommendations('user');
      })
      .catch((error) => {
        console.error('프로필 데이터를 가져오지 못했습니다:', error);
      });
  } else {
    console.log('프로필이 이미 로드됨.');
    fetchRecommendations('user');
  }
});
</script>


<style scoped>
.recommendations-page {
  padding-top: 80px; /* Add padding to prevent overlapping with the navbar */
  padding-left: 20px;
  padding-right: 20px;
}

.custom-bg {
  background-color: #f7ecd3;
}

.my-8 {
  margin: 32px 0;
}

.error-message {
  color: red;
  font-weight: bold;
  text-align: center;
}

.no-data {
  text-align: center;
  color: gray;
  font-size: 1.2rem;
}
</style>
