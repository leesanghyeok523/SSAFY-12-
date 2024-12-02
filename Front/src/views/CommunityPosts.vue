<template>
  <div class="community-page">
    <h1>커뮤니티</h1>
    <div class="header">
      <input
        type="text"
        v-model="searchQuery"
        placeholder="검색어를 입력하세요"
      />
      <button @click="goToCreatePost" class="create-button">글쓰기</button>
    </div>
    <div v-if="filteredPosts.length === 0">게시글이 없습니다.</div>
    <div v-for="post in filteredPosts" :key="post.id" class="post-item">
      <h2 @click="goToPostDetail(post.id)">{{ post.title }}</h2>
      <p>{{ post.content }}</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useCommunityStore } from '@/stores/community';
import { useRouter } from 'vue-router';

export default {
  setup() {
    const communityStore = useCommunityStore();
    const searchQuery = ref('');
    const router = useRouter();

    const fetchPosts = async () => {
      try {
        await communityStore.fetchPosts();
      } catch (error) {
        console.error('게시글 로드 중 오류 발생:', error);
      }
    };

    const filteredPosts = computed(() =>
      communityStore.posts.filter((post) =>
        post.title.includes(searchQuery.value)
      )
    );

    const goToPostDetail = (id) => {
      router.push(`/community_posts/${id}`);
    };

    const goToCreatePost = () => {
      router.push('/community_posts/create');
    };

    onMounted(() => {
      fetchPosts();
    });

    return { searchQuery, filteredPosts, goToPostDetail, goToCreatePost };
  },
};
</script>

<style scoped>
.community-page {
  padding: 20px;
  padding-top: 100px;
}

.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.create-button {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
}

.create-button:hover {
  background: #0056b3;
}

.post-item {
  margin-bottom: 20px;
  cursor: pointer;
}

.post-item:hover {
  background: #f9f9f9;
}
</style>
