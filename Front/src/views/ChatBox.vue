<template>
  <div class="chat-page">
    <div class="ai-chat-container">
      <div class="chat-box">
        <div class="chat-messages">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="message.role === 'user' ? 'user-message' : 'ai-message'"
            v-html="message.content"
          ></div>
        </div>
        <form @submit.prevent="sendMessage" class="chat-input-container">
          <input
            v-model="userInput"
            type="text"
            placeholder="요약 받고싶은 기업명을 입력해주세요."
            class="chat-input"
          />
          <button type="submit" class="send-button">전송</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      userInput: "",
      messages: [], // 대화 기록 저장
    };
  },
  methods: {
    sendMessage() {
      if (!this.userInput.trim()) return;

      // 사용자 메시지를 대화창에 추가
      this.messages.push({
        role: "user",
        content: this.userInput,
      });

      const userMessage = this.userInput.trim();
      this.userInput = ""; // 입력창 초기화

      // Axios 요청을 처리
      axios
        .get("http://127.0.0.1:8000/api/core/actions/fetch-and-summarize-business/", {
          params: { corp_name: userMessage },
        })
        .then((response) => {
          const summary = typeof response.data.summary === "string" 
            ? response.data.summary 
            : JSON.stringify(response.data.summary, null, 2);

          this.messages.push({
            role: "ai",
            content: summary || "요약 데이터가 없습니다.",
          });
        })
        .catch((error) => {
          this.messages.push({
            role: "ai",
            content: "요약 요청 중 오류가 발생했습니다. 다시 시도해주세요.",
          });
          console.error("Error fetching summary:", error);
        });
    },
  },
};
</script>

<style scoped>
/* 특정 페이지 배경 설정 */
.chat-page {
  background: url('@/assets/Ai-page.jpg') no-repeat center center fixed;
  background-size: 2100px 1100px;
  min-height: 100vh;
  padding-top: 80px; /* 네브바 높이를 고려한 패딩 */
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 전체 대화창 스타일 */
.ai-chat-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  max-width: 800px;
  height: calc(100vh - 80px); /* 네브바 높이 제외한 전체 높이 */
  background: rgba(0, 0, 0, 0.6); /* 배경 위에 어두운 투명 레이어 */
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
}

/* 채팅 박스 */
.chat-box {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: rgba(42, 42, 42, 0.8); /* 반투명 효과 추가 */
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
}

/* 채팅 메시지 */
.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  color: white;
  font-family: Arial, sans-serif;
  font-size: 16px;
}

.chat-messages .user-message {
  text-align: right;
  color: #4caf50;
  margin-bottom: 10px;
}

.chat-messages .ai-message {
  text-align: left;
  color: white;
  margin-bottom: 20px; /* 문단 간격 추가 */
  line-height: 1.6; /* 줄 간격 */
  font-size: 18px; /* 글씨 크기 조정 */
  white-space: pre-wrap; /* 줄바꿈 유지 */
}


/* 입력 폼 */
.chat-input-container {
  display: flex;
  padding: 15px;
  background: rgba(30, 30, 30, 0.8); /* 반투명 효과 추가 */
}

.chat-input {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 5px;
  margin-right: 10px;
  background: #333;
  color: white;
  font-size: 16px;
}

.send-button {
  padding: 10px 20px;
  border: none;
  background: #4caf50;
  color: white;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

.send-button:hover {
  background: #45a049;
}
</style>
