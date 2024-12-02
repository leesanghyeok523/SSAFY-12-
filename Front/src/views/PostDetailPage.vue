<template>
  <div class="post-detail-page">
    <h1>{{ post.title }}</h1>
    <p>종목명: {{ post.stock_name }}</p>
    <p>{{ post.content }}</p>
    <div v-if="isAuthor">
      <button @click="editPost">수정</button>
      <button @click="deletePost">삭제</button>
    </div>
  </div>
</template>


<script>
import { useCommunityStore } from '@/stores/community';
import { computed, ref } from 'vue';

export default {
  props: ['id'],
  setup(props) {
    const communityStore = useCommunityStore();
    const post = computed(() =>
      communityStore.posts.find((p) => p.id === parseInt(props.id))
    );
    const isAuthor = true; // Replace with actual logic
    const newComment = ref('');

    const deletePost = async () => {
      await communityStore.deletePost(props.id);
    };

    const addComment = async () => {
      if (!newComment.value) return;
      await communityStore.addComment(props.id, newComment.value);
      newComment.value = '';
    };

    const deleteComment = async (commentId) => {
      await communityStore.deleteComment(commentId);
    };

    return { post, isAuthor, deletePost, newComment, addComment, deleteComment };
  },
};
</script>

<style scoped>
.post-detail-page {
  padding: 20px;
}

.comments-section {
  margin-top: 20px;
}

input {
  width: 100%;
  margin-bottom: 10px;
}

button {
  margin-right: 10px;
}
</style>
