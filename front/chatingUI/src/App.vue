<template>
  <div id="app">
    <!-- 상단 바 추가 -->
    <header class="top-bar">
      <div class="brand-logo">
        <img src="../public/images/logo.png" alt="로고" />
      </div>
      <div class="user-options">
        <a href="/login">로그인</a>
        <a href="/mypage">마이페이지</a>
      </div>
    </header>

    <!-- 사이드바 배경 및 토글 버튼 추가 -->
    <div class="sidebar-background">
      <button @click="toggleSidebar" class="toggle-sidebar">
        <img :src="isSidebarOpen ? 'public/images/sidebar-toggle-white.svg' : 'public/images/sidebar-toggle-white.svg'" alt="토글 버튼" />
      </button>
    </div>

    <!-- 실제 사이드바 -->
    <div class="sidebar" :class="{ open: isSidebarOpen }">
      <div v-if="isSidebarOpen" class="sidebar-content">
        <ul>
          <li @click="navigateTo('찜한 정책')">찜한 정책</li>
          <li @click="navigateTo('최근 뉴스')">최근 뉴스</li>
          <li @click="navigateTo('사용 방법')">사용 방법</li>
          <li @click="navigateTo('고객 문의')">고객 문의</li>
        </ul>
      </div>
    </div>

    <!-- 기존 채팅 UI -->
    <div class="container chat-section" :class="{ 'with-sidebar': isSidebarOpen }">
      <div class="chat-card card">
        <div class="card-header text-center">
          지원 정책 찾기
        </div>
        <div class="card-body">
          <div class="messages mb-3" ref="messagesContainer">
            <div
              v-for="(msg, index) in messages"
              :key="index"
              :class="['d-flex', msg.type === 'user' ? 'justify-content-end' : 'justify-content-start', 'mb-2']"
            >
              <!-- 상대방 메시지일 때 프로필 사진과 이름 표시 -->
              <div v-if="msg.type === 'bot'" class="d-flex flex-column align-items-start">
                <div class="d-flex align-items-center mb-1">
                  <img :src="msg.profileImage" alt="프로필 이미지" class="profile-img" />
                  <span class="profile-name ms-2">{{ msg.name }}</span>
                </div>
                <div class="message-bubble bot-message" v-html="msg.text"></div>
              </div>

              <!-- 사용자 메시지일 때 텍스트만 표시 -->
              <div v-else>
                <div class="message-bubble user-message">
                  <div v-html="msg.text"></div>
                </div>
              </div>
            </div>
            <div v-if="loading" class="text-center text-muted">로딩중...</div>
          </div>
          <div class="input-group">
            <textarea
              v-model="inputText"
              ref="messageInput"
              class="form-control"
              placeholder="메시지를 입력하세요..."
              @keyup.enter="submitText"
              rows="1"
              style="resize: none;"
            ></textarea>
            <!-- 전송 버튼 -->
            <button class="send-button" @click="submitText">전송</button>
          </div>
          <div class="mt-3">
            <label for="imageUpload" class="form-label">사진 업로드</label>
            <input type="file" id="imageUpload" @change="handleImageUpload" accept="image/*" class="form-control" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      inputText: '',
      messages: [
        {
          text:
            '안녕하세요, 지원이에요! 😇\n제가 정책을 알려드리기 전에\n몇 가지 정보가 필요해요.\n\n정보는 저장되지 않으니 안심하고 작성하세요!',
          type: 'bot',
          name: '지원이',
          profileImage: 'public/images/bot-profile.png', // 챗봇 프로필 사진 경로
        }
      ],
      userInfo: {},
      questions: [
        "1. 지역",
        "2. 취업상태",
        "3. 학력",
        "4. 특화분야",
        "5. 개인/가구 특성",
        `소중한 정보 감사합니다!😊\n\n원하는 정책 또는 금융 정보를 입력하세요\n\n- 정책: 일자리, 주거, 교육, 복지, 문화, 보육, 법률\n- 금융: 예금, 적금, 담보대출, 자금대출, 신용대출, 보험`
      ],
      currentQuestionIndex: 0,
      loading: false,
      imageFile: null,
      imagePreview: null,
      isSidebarOpen: false, // 사이드바 열림/닫힘 상태
    };
  },
  methods: {
    submitText() {
      if (!this.inputText) return;
      this.messages.push({ text: this.inputText, type: 'user' });

      if (this.currentQuestionIndex < this.questions.length) {
        this.handleAnswer(this.inputText);
        this.inputText = '';
        this.$nextTick(() => {
          this.$refs.messageInput.focus();
          this.$refs.messagesContainer.scrollTop = this.$refs.messagesContainer.scrollHeight;
        });
      }
    },
    handleAnswer(answer) {
      const questionKey = this.getQuestionKey(this.currentQuestionIndex);
      this.userInfo[questionKey] = answer;
      this.currentQuestionIndex++;

      if (this.currentQuestionIndex < this.questions.length) {
        this.messages.push({
          text: this.questions[this.currentQuestionIndex],
          type: 'bot',
          name: '지원이',
          profileImage: 'public/images/bot-profile.png'
        });
      } else {
        this.messages.push({
          text: "소중한 정보 감사합니다! 😊",
          type: 'bot',
          name: '지원이',
          profileImage: 'public/images/bot-profile.png'
        });
        this.sendUserInfo();
      }

      this.$nextTick(() => {
        this.$refs.messagesContainer.scrollTop = this.$refs.messagesContainer.scrollHeight;
      });
    },
    async sendUserInfo() {
      this.loading = true;
      try {
        const formData = new FormData();
        for (const key in this.userInfo) {
          formData.append(key, this.userInfo[key]);
        }
        if (this.imageFile) {
          formData.append('image', this.imageFile); // 이미지는 전송하되 표시하지 않음
        }

        const response = await axios.post('http://127.0.0.1:5000/run-script', formData);
        this.messages.push({
          text: `서버 응답: ${response.data.output}`,
          type: 'bot',
          name: '지원이',
          profileImage: 'public/images/bot-profile.png'
        });
      } catch (error) {
        this.messages.push({
          text: `서버 오류: ${error.response ? error.response.data.error : error.message}`,
          type: 'bot',
          name: '지원이',
          profileImage: 'public/images/bot-profile.png'
        });
      } finally {
        this.loading = false;
      }

      this.$nextTick(() => {
        this.$refs.messagesContainer.scrollTop = this.$refs.messagesContainer.scrollHeight;
      });
    },
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.imageFile = file;
        // 이미지 미리보기 제거
      }
    },
    getQuestionKey(index) {
      const keys = ['location', 'employment_status', 'education', 'specialization', 'household_features', 'info'];
      return keys[index];
    },
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen; // 사이드바 열고 닫기
    },
    navigateTo(section) {
      console.log(`${section} 탭으로 이동합니다.`);
    },
  },
  mounted() {
    this.messages.push({
      text: this.questions[this.currentQuestionIndex],
      type: 'bot',
      name: '지원이',
      profileImage: 'public/images/bot-profile.png'
    });
    this.$nextTick(() => {
      this.$refs.messageInput.focus();
    });
  }
};
</script>

<style>
html, body {
  height: 100%;
  margin: 0;
}

#app {
  display: flex;
  flex-direction: column; /* 세로 정렬 */
  align-items: center; /* 중앙 정렬 */
}

.container {
  max-width: 500px;
  height: calc(100vh - 60px); /* 상단 바를 제외한 높이 */
  display: flex;
  align-items: center;
  justify-content: center;
  transition: margin-left 0.3s ease; /* 사이드바 열림/닫힘 시의 자연스러운 이동 */
}

.chat-section.with-sidebar {
  margin-left: 250px; /* 사이드바가 열렸을 때 공간 확보 */
}

.chat-section {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
  transition: margin-left 0.3s ease;
}

/* 상단 바 스타일 */
.top-bar {
  background-color: #ffffff;
  height: 60px;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
}

.brand-logo img {
  height: 40px;
}

.user-options a {
  margin-left: 15px;
  color: #333; /* 글씨 색상 변경 */
  text-decoration: none;
}

.user-options a:hover {
  text-decoration: underline;
}

/* 사이드바 배경 */
.sidebar-background {
  position: fixed;
  left: 0;
  top: 60px; /* 상단 바 아래에 배치 */
  background-color: #9cd2d9;
  height: 100%;
  width: 100px; /* 토글 버튼용 사이드바 배경 */
  z-index:1;
}

/* 실제 사이드바 */
.sidebar {
  background-color: #9cd2d9;
  width: 250px;
  height: 100%;
  position: fixed;
  top: 60px; /* 상단 바 바로 아래에 고정 */
  left: 50px; /* 토글 버튼 배경 뒤에 사이드바 배치 */
  transition: transform 0.3s ease;
  z-index: 1;
  transform: translateX(-250px); /* 사이드바 닫힘 상태 */
}

.sidebar.open {
  transform: translateX(0); /* 사이드바 열림 상태 */
}

.sidebar-content {
  padding: 20px;
}

.sidebar-content ul {
  list-style: none;
  padding: 0;
}

.sidebar-content li {
  padding: 10px;
  cursor: pointer;
  margin-bottom: 10px;
  background-color: #fff;
  border-radius: 8px;
  transition: background-color 0.3s;
}

.sidebar-content li:hover {
  background-color: #e0eaff;
}

/* 토글 버튼 */
.toggle-sidebar {
  position: absolute;
  top: 20px;
  left: 10px;
  background-color: transparent;
  border: none;
  cursor: pointer;
  z-index: 2;
}

.toggle-sidebar img {
  width: 30px;
  height: 30px;
  border-radius: 0; /* 사각형 */
}

/* 채팅 UI */
.chat-card {
  height: calc(85vh - 60px); /* 상단 바를 제외한 채팅 카드 높이 */
  width: 60%;
  display: flex;
  flex-direction: column;
}

.card-body {
  flex: 1;
  display: flex;
  height: calc(85vh - 60px); /* 상단 바 제외 */
  width: 95vh;
  flex-direction: column;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
}

.message-bubble {
  max-width: 100%;
  padding: 10px 15px;
  border-radius: 20px;
  position: relative;
  word-wrap: break-word;
  white-space: pre-wrap;
  word-break: keep-all;
  margin-bottom: 12px;
}

.user-message {
  background-color: #9cd2d9;
  color: white;
  border-radius: 20px;
}

.bot-message {
  background-color: #e5e5ea;
  color: black;
  border-radius: 20px;
}

.profile-img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.profile-name {
  font-size: 0.9rem;
  font-weight: bold;
  color: #555;
}

.send-button {
  border-radius: 20px;
  background-color: #9cd2d9 !important; /* 전송 버튼 색상 */
  color: white !important; /* 텍스트 색상 */
  border: none; /* 테두리 제거 */
  padding: 10px 20px;
  outline: none;
  box-shadow: none; /* 그림자 제거 */
}

.send-button:hover {
  background-color: #78c0c7 !important; /* 호버 시 색상 변경 */
}

.send-button:focus {
  outline: none; /* 포커스 시 테두리 제거 */
  box-shadow: none; /* 포커스 시 그림자 제거 */
}

textarea:focus {
  outline: none; /* 입력창 포커스 시 테두리 제거 */
  box-shadow: none; /* 입력창 포커스 시 그림자 제거 */
}
</style>
