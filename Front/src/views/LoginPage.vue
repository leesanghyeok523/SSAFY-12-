<template>
  <div class="login-page">
    <div class="login-container">
      <h1>로그인</h1>
      <form @submit.prevent="logIn">
        <div class="form-group">
          <label for="username">아이디</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="아이디를 입력하세요"
            required
          />
        </div>
        <div class="form-group">
          <label for="password">비밀번호</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="비밀번호를 입력하세요"
            required
          />
        </div>
        <button type="submit" class="login-button">로그인</button>
      </form>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth';
import { ref } from 'vue';

export default {
  setup() {
    const authStore = useAuthStore();
    const username = ref('');
    const password = ref('');

    const logIn = async () => {
      try {
        await authStore.login(username.value, password.value);
        alert('로그인 성공!');
        window.location.href = '/';
      } catch (error) {
        console.error('로그인 실패:', error.message || error);
        alert('로그인 실패. 아이디와 비밀번호를 확인하세요.');
      }
    };

    return { username, password, logIn };
  },
};
</script>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: url('@/assets/007.jpg') no-repeat center center/cover; /* 배경 이미지 */
  font-family: 'Roboto', sans-serif;
}

.login-container {
  background: rgba(0, 0, 0, 0.5); /* 회원가입 컨테이너와 동일한 색감 */
  padding: 40px 50px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  text-align: center;
  width: 100%;
  max-width: 400px;
}

h1 {
  font-size: 2rem;
  color: #ffffff; /* 흰색 텍스트 */
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #ffffff; /* 흰색 텍스트 */
}

input {
  width: 100%;
  padding: 12px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 5px;
  outline: none;
  background-color: rgba(255, 255, 255, 0.8); /* 기본 배경색 */
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* 포커스 시 배경색과 텍스트 색 변경 */
input:focus {
  background-color: #fff; /* 흰색 배경 */
  color: #000; /* 검정 텍스트 */
  border-color: #6a11cb; /* 포커스 시 테두리 색상 */
}

button {
  width: 100%;
  padding: 12px 20px;
  font-size: 1rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.login-button {
  background: linear-gradient(to right, #6a11cb, #2575fc); /* 회원가입 버튼과 동일한 색상 */
  color: white;
}

.login-button:hover {
  background: linear-gradient(to right, #5a0eab, #1f5fc8); /* 호버 효과도 동일 */
}
</style>
