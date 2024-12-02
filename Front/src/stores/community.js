import { defineStore } from 'pinia';
import axios from 'axios';

export const useCommunityStore = defineStore('community', {
  state: () => ({
    posts: [], // 게시글 목록 상태
  }),
  actions: {
    // 게시글 목록 가져오기
    async fetchPosts() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/core/router/posts/');
        this.posts = response.data;
        console.log('게시글 가져오기 성공:', response.data);
      } catch (error) {
        console.error('게시글을 가져오는 데 실패했습니다:', error.response?.data || error);
        throw new Error('게시글 로드 실패');
      }
    },
    // 게시글 생성
    async createPost(postData) {
      try {
        const token = localStorage.getItem('accessToken'); // 인증 토큰 가져오기
        if (!token) throw new Error('로그인이 필요합니다.');

        // 필요한 필드를 모두 포함하여 전송
        const dataToSend = {
          title: postData.title,
          content: postData.content,
          stock_name: postData.stock_name || '기본 종목', // 기본값 추가
        };

        console.log('전송 데이터:', dataToSend);

        const response = await axios.post(
          'http://127.0.0.1:8000/api/core/router/posts/',
          dataToSend,
          {
            headers: {
              Authorization: `Token ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );
        console.log('게시글 작성 성공:', response.data);
        this.posts.unshift(response.data); // 새 글 추가
      } catch (error) {
        console.error('게시글 작성 실패:', error.response?.data || error);
        throw new Error('게시글 작성 실패');
      }
    },
  },
});
