<template>
  <header class="header-nav">
    <nav>
      <ul class="menu">
        <!-- STOCKSNAP -->
        <li class="brand-link">
          <router-link to="/">STOCKSNAP</router-link>
        </li>

          <!-- 비로그인 상태 -->
        <template v-if="!authStore.isAuthenticated">
          <li>
            <router-link to="/login" class="nav-button">로그인</router-link>
          </li>
          <li>
            <router-link to="/signup" class="nav-button signup-button">회원가입</router-link>
          </li>
        </template>

        <!-- 로그인 상태 -->
        <template v-else>
          <li><router-link to="/report-summary">보고서 요약</router-link></li>
          <li><router-link to="/recommend">추천 상품</router-link></li>
          <li><router-link to="/income-level-calculator">소득분위 계산기</router-link></li>
          <li><router-link to="/savings-comparison">예적금 비교</router-link></li>
          <li><router-link to="/exchange-rates">환율 계산기</router-link></li>
          <li><router-link to="/map">은행찾기</router-link></li>
          <li><router-link to="/profile">프로필</router-link></li>
          <li><a @click.prevent="handleLogout">로그아웃</a></li>
        </template>
      </ul>
    </nav>
  </header>
</template>

<script>
import { useAuthStore } from "@/stores/auth";

export default {
  setup() {
    const authStore = useAuthStore();

    const handleLogout = async () => {
      try {
        await authStore.logout();
        alert("로그아웃 되었습니다!");
        window.location.href = "/";
      } catch (error) {
        console.error("로그아웃 실패:", error.message || error);
        alert("로그아웃에 실패했습니다. 다시 시도해주세요.");
      }
    };

    return { authStore, handleLogout };
  },
};
</script>

<style scoped>
/* Navbar 스타일 */
.header-nav {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 80px;
  padding: 20px 40px;
  background-color: #ffffff; /* 흰색 배경 */
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.menu {
  list-style: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0;
  padding: 0;
}

.brand-link {
  margin-right: auto;
}

.brand-link a {
  text-decoration: none;
  color: #232323; /* 기본 글자색: 어두운 회색 */
  font-size: 1.8rem; /* 글자 크기 증가 */
  font-style: italic; /* 기울기 효과 */
  font-weight: bold; /* 굵게 */
  transition: color 0.3s;
}

.brand-link a:hover {
  color: #2575fc; /* 호버 시 파란색 */
}

.menu li {
  font-size: 1.4rem;
  font-weight: 600; /* 글자를 더 굵게 설정 */
  margin-left: 25px;
}

.menu li a {
  text-decoration: none;
  color: #232323; /* 기본 글자색: 어두운 회색 */
  transition: color 0.3s;
}

.menu li a:hover {
  color: #2575fc; /* 호버 시 파란색 */
}

.menu li a.router-link-active {
  font-weight: bold;
  color: #2575fc; /* 활성화된 메뉴는 파란색 */
}

/* 버튼 스타일 */
.nav-button {
  padding: 10px 20px;
  text-decoration: none;
  color: white;
  background: linear-gradient(to right, #6a11cb, #2575fc);
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: bold;
  transition: background-color 0.3s ease;
  display: inline-block;
  text-align: center;
}

.nav-button:hover {
  background-color: white; /* 호버 시 더 어두운 파란색 */
}

.signup-button {
  background-color: white;
}

.signup-button:hover {
  background-color: white; /* 회원가입 버튼 호버 색상 */
}
</style>
