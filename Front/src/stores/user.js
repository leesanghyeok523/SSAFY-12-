import { defineStore } from 'pinia';
import axios from 'axios';

export const useUserStore = defineStore('user', {
  state: () => ({
    userProfile: {
      username: null,
      email: null,
      age: null,
      nickname: null,
    },
    isLoading: false,
  }),
  actions: {
    fetchUserProfile() {
      console.log('fetchUserProfile 호출됨');
      const token = localStorage.getItem('accessToken');
      if (!token) {
        console.error('토큰이 없습니다. 로그인이 필요합니다.');
        throw new Error('인증 토큰이 누락되었습니다.');
      }

      this.isLoading = true; // 로딩 시작
      return axios
        .get('http://127.0.0.1:8000/api/core/actions/profile/', {
          headers: { Authorization: `Token ${token}` },
        })
        .then((response) => {
          console.log('프로필 응답 데이터:', response.data);
          this.userProfile = response.data;
          return response.data;
        })
        .catch((error) => {
          console.error('프로필 데이터 로드 실패:', error);
          if (error.response && error.response.status === 401) {
            console.log('인증 에러 발생: 로그인 페이지로 이동합니다.');
            window.location.href = '/login';
          }
          throw error;
        })
        .finally(() => {
          this.isLoading = false; // 로딩 종료
        });
    },
  },
});
