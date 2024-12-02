<template>
  <div class="create-post-page">
    <h1>글쓰기</h1>
    <form @submit.prevent="submitPost">
      <div>
        <label for="title">제목:</label>
        <input type="text" id="title" v-model="title" required />
      </div>
      <div>
        <label for="content">내용:</label>
        <textarea id="content" v-model="content" required></textarea>
      </div>
      <div>
        <label for="stock-name">종목명:</label>
        <input type="text" id="stock-name" v-model="stockName" placeholder="예: 삼성전자" />
      </div>
      <button type="submit" class="submit-button">작성 완료</button>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useCommunityStore } from '@/stores/community';
import { useRouter } from 'vue-router';

export default {
  setup() {
    const communityStore = useCommunityStore();
    const router = useRouter();

    const title = ref('');
    const content = ref('');
    const stockName = ref(''); // 종목명 필드 추가

    const submitPost = async () => {
      try {
        const postData = {
          title: title.value,
          content: content.value,
          stock_name: stockName.value, // 종목명 전달
        };
        console.log('전송 데이터:', postData);
        await communityStore.createPost(postData);
        alert('게시글이 작성되었습니다.');
        router.push('/community_posts');
      } catch (error) {
        console.error('게시글 작성 중 오류 발생:', error);
        alert('게시글 작성에 실패했습니다.');
      }
    };

    return { title, content, stockName, submitPost };
  },
};
</script>

<style scoped>
.create-post-page {
  padding: 20px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.submit-button {
  padding: 10px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.submit-button:hover {
  background: #0056b3;
}
</style>
