<template>
  <div id="app">
    <!-- 상단 바 추가 -->
    <header class="top-bar">
      <div class="brand-logo">
        <a href="/">
          <img src="/images/logo.png" alt="로고" />
        </a>
      </div>
      <div class="user-options">
        <a href="/login">로그인</a>
        <a href="/mypage">마이페이지</a>
      </div>
    </header>

    <!-- 사이드바 배경 -->
    <div class="sidebar-background"></div>

    <!-- 토글 버튼을 사이드바 배경 밖으로 이동 -->
    <button @click="toggleSidebar" class="toggle-sidebar">
      <img src="/images/sidebar-toggle-white.svg" alt="토글 버튼" />
    </button>

    <!-- 실제 사이드바 -->
    <div class="sidebar" :class="{ open: isSidebarOpen }">
      <transition name="sidebar-content-transition">
        <div v-show="isSidebarContentVisible" class="sidebar-content">
          <ul>
            <li @click="navigateTo('찜한 정책')">찜한 정책</li>
            <li @click="navigateTo('최근 뉴스')">최근 뉴스</li>
            <li @click="navigateTo('사용 방법')">사용 방법</li>
            <li @click="navigateTo('고객 문의')">고객 문의</li>
          </ul>
        </div>
      </transition>
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
              :class="['message-row', msg.type === 'user' ? 'justify-end' : 'justify-start']"
            >
              <!-- 상대방 메시지일 때 프로필 사진과 이름 표시 -->
              <div v-if="msg.type === 'bot'" class="message-content bot-message-content">
                <img src="/images/bot-profile.png" alt="프로필 이미지" class="profile-img" />
                <div class="message-bubble bot-message" v-html="renderMarkdown(msg.text)"></div>
              </div>

              <!-- 사용자 메시지일 때 텍스트만 표시 -->
              <div v-else class="message-content user-message-content">
                <div class="message-bubble user-message">
                  {{ msg.text }}
                </div>
              </div>
            </div>
          </div>
          <div class="input-group">
            <textarea
              v-model="inputText"
              ref="messageInput"
              class="form-control"
              placeholder="메시지를 입력하세요..."
              @keydown.enter.prevent="submitText"
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
import * as marked from 'marked'; // marked의 ESM 방식 named import
import DOMPurify from 'dompurify'; // DOMPurify 임포트

export default {
  data() {
    return {
      inputText: '',
      messages: [
        {
          text:
            "**안녕하세요, 지원이에요! 😇**\n\n제가 정책을 알려드리기 전에\n몇 가지 **정보가 필요해요.**\n\n정보는 저장되지 않으니 안심하고 작성하세요!\n\n해당 사항이 없다면 안 적으셔도 됩니다.",
          type: 'bot',
        }
      ],
      userInfo: {},
      questions: [
        "**1\\. 지역**\n예) 서울, 부산, 대구",
        "**2\\. 취업상태**\n예) 재직자, 자영업자, 미취업자, 프리랜서, 예비(창업자), 단기근로자",
        "**3\\. 학력**\n예) 고졸 미만, 고교 재학, 대학 졸업, 석·박사",
        "**4\\. 특화분야**\n예) 중소기업, 저소득층, 장애인, 군인, 농업인, 지역인재",
        "**5\\. 개인/가구 특성**\n예) 조손가정, 소년소녀가정, 확대가족여부 (3대이상), 소상공인,\n무주택세대, 예비창업자, 가정위탁아동, 입양아동, 사회복지시설 입소자,\n난임, 대학생, 구직자, 치매, 다문화가정",
      ],
      currentQuestionIndex: 0,
      loading: false,
      imageFile: null,
      isSidebarOpen: false,
      isSidebarContentVisible: false,
      loadingMessages: [
        "정책을 찾는 중입니다.",
        "필요하실 것 같은 몇 가지 정책을 찾았어요!",
        "조금만 더 추려볼게요!"
      ],
      currentLoadingMessageIndex: 0,
      loadingTimeouts: [],
    };
  },
  methods: {
    submitText() {
      if (!this.inputText) return;
      this.messages.push({ text: this.inputText, type: 'user' });
      const userInput = this.inputText;
      this.inputText = '';
      this.$nextTick(() => {
        this.$refs.messageInput.focus();
        this.$refs.messagesContainer.scrollTop = this.$refs.messagesContainer.scrollHeight;
      });

      if (this.currentQuestionIndex < this.questions.length) {
        this.handleAnswer(userInput);
      } else {
        // 모든 질문에 답변한 후 사용자 입력 처리
        this.userInfo['info'] = userInput;
        this.sendUserInfo();
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
        });
      } else if (this.currentQuestionIndex === this.questions.length) {
        // 질문이 끝났을 때 메시지 추가
        this.messages.push({
          text: `소중한 정보 감사합니다!😊\n\n**원하는 정책 또는 금융 정보를 입력하세요**\n\n- 정책: 일자리, 주거, 교육, 복지, 문화, 보육, 법률\n- 금융: 예금, 적금, 담보대출, 자금대출, 신용대출, 보험`,
          type: 'bot',
        });
      }

      this.$nextTick(() => {
        this.$refs.messagesContainer.scrollTop = this.$refs.messagesContainer.scrollHeight;
      });
    },
    async sendUserInfo() {
      this.loading = true;

      // 로딩 메시지 시작
      this.startLoadingMessages();

      try {
        const formData = new FormData();
        for (const key in this.userInfo) {
          formData.append(key, this.userInfo[key]);
        }
        if (this.imageFile) {
          formData.append('image', this.imageFile); // 이미지는 전송하되 표시하지 않음
        }

        const response = await axios.post('http://127.0.0.1:5000/run-script', formData);

        // 로딩 메시지 중지
        this.stopLoadingMessages();

        // 마크다운으로 받은 데이터를 렌더링
        this.messages.push({
          text: response.data.output,
          type: 'bot',
        });
      } catch (error) {
        // 로딩 메시지 중지
        this.stopLoadingMessages();

        this.messages.push({
          text: `서버 오류: ${error.response ? error.response.data.error : error.message}`,
          type: 'bot',
        });
      } finally {
        this.loading = false;
      }

      this.$nextTick(() => {
        this.$refs.messagesContainer.scrollTop = this.$refs.messagesContainer.scrollHeight;
      });
    },
    startLoadingMessages() {
      this.currentLoadingMessageIndex = 0;
      this.loadingTimeouts = [];

      const displayNextMessage = () => {
        if (this.currentLoadingMessageIndex < this.loadingMessages.length && this.loading) {
          const messageText = this.loadingMessages[this.currentLoadingMessageIndex];
          this.messages.push({
            text: messageText,
            type: 'bot',
            isLoadingMessage: true,
          });

          this.currentLoadingMessageIndex++;

          this.$nextTick(() => {
            this.$refs.messagesContainer.scrollTop = this.$refs.messagesContainer.scrollHeight;
          });

          const timeout = setTimeout(displayNextMessage, 6000); // 6초 후 다음 메시지
          this.loadingTimeouts.push(timeout);
        }
      };

      displayNextMessage();
    },
    stopLoadingMessages() {
      // 모든 타이머 제거
      this.loadingTimeouts.forEach(timeout => clearTimeout(timeout));
      this.loadingTimeouts = [];

      // 로딩 메시지 제거
      this.messages = this.messages.filter(msg => !msg.isLoadingMessage);
    },
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.imageFile = file;
      }
    },
    getQuestionKey(index) {
      const keys = ['location', 'employment_status', 'education', 'specialization', 'household_features', 'info'];
      return keys[index];
    },
    renderMarkdown(markdownText) {
      let cleanMarkdownText = markdownText.trim();
      
      // 텍스트 끝의 불필요한 줄바꿈 제거
      cleanMarkdownText = cleanMarkdownText.replace(/\n+$/, '');

      // \n을 <br>로 변환하여 줄바꿈을 명시적으로 적용
      cleanMarkdownText = cleanMarkdownText.replace(/\n/g, '<br>');

      // 마크다운을 HTML로 변환
      const dirtyHTML = marked.parse(cleanMarkdownText);

      // DOMPurify로 HTML을 정화하여 XSS 방지
      return DOMPurify.sanitize(dirtyHTML);
    },
    toggleSidebar() {
      if (this.isSidebarOpen) {
        // 사이드바 닫기
        this.isSidebarContentVisible = false;
        setTimeout(() => {
          this.isSidebarOpen = false;
        }, 300);
      } else {
        // 사이드바 열기
        this.isSidebarOpen = true;
        setTimeout(() => {
          this.isSidebarContentVisible = true;
        }, 300);
      }
    },
    navigateTo(section) {
      console.log(`${section} 탭으로 이동합니다.`);
    },
  },
  mounted() {
    this.messages.push({
      text: this.questions[this.currentQuestionIndex],
      type: 'bot',
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
  font-family: 'Noto Sans KR', sans-serif !important;
  font-size: 18px; /* 기본 폰트 크기 */
  line-height: 1.6; /* 가독성을 위해 줄 간격 조정 */
}

#app {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.container {
  max-width: 500px;
  height: calc(100vh - 60px);
  display: flex;
  transition: margin-left 0.3s ease;
}

.chat-section.with-sidebar {
  margin-left: 250px;
}

.chat-section {
  max-width: 600px;
  width: 100%;
  margin-left: 100px !important;
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
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
}

.brand-logo img {
  height: 40px;
}

.user-options a {
  margin-left: 15px;
  color: #333;
  text-decoration: none;
}

.user-options a:hover {
  text-decoration: underline;
}

.sidebar-background {
  position: fixed;
  left: 0;
  top: 60px;
  background-color: #9cd2d9;
  height: 100%;
  width: 100px;
  z-index: 0;
}

.sidebar {
  background-color: #9cd2d9;
  width: 250px;
  height: 100%;
  position: fixed;
  top: 60px;
  left: 0;
  transition: transform 0.3s ease;
  z-index: 1;
  transform: translateX(-250px);
}

.sidebar.open {
  transform: translateX(0);
}

.sidebar-content {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  padding: 20px;
  margin-top: 50px;
}

.sidebar-content ul {
  list-style: none;
  padding: 0;
  text-align: center;
}

.sidebar-content li {
  padding: 10px;
  cursor: pointer;
  margin-bottom: 10px;
  background-color: #fff;
  border-radius: 8px;
  transition: background-color 0.3s;
  text-align: center;
}

.sidebar-content li:hover {
  background-color: #e0eaff;
}

.sidebar-content-transition-enter-active,
.sidebar-content-transition-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.sidebar-content-transition-enter-from,
.sidebar-content-transition-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.sidebar-content-transition-enter-to,
.sidebar-content-transition-leave-from {
  opacity: 1;
  transform: translateX(0);
}

.toggle-sidebar {
  position: fixed;
  top: 80px;
  left: 25px;
  background-color: transparent;
  border: none;
  cursor: pointer;
  z-index: 1000;
}

.toggle-sidebar img {
  width: 30px;
  height: 30px;
}

/* 채팅 카드 스타일 */
.chat-card {
  width: 85vh;
  display: flex;
  flex-direction: column;
  margin-top: 80px;
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  height: calc(85vh - 60px); /* 상단 바를 제외한 높이 */
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 5px;
  display: flex;
  flex-direction: column;
}

.input-group {
  display: flex;
  width: 100%;
  margin-bottom: 10px;
  flex-shrink: 0;
  overflow: hidden;
}

textarea {
  flex-grow: 1;
  border-top-left-radius: 20px !important;
  border-bottom-left-radius: 20px !important;
  padding: 10px;
  border: 1px solid #ccc;
  max-width: 100%;
  box-sizing: border-box;
}

textarea:focus {
  outline: none !important;
  box-shadow: none !important;
  border: 1px solid #9cd2d9 !important;
}

.send-button {
  border-top-right-radius: 20px !important;
  border-bottom-right-radius: 20px !important;
  border-top-left-radius: 0 !important;
  border-bottom-left-radius: 0 !important;
  background-color: #9cd2d9 !important;
  color: white !important;
  border: none;
  padding: 10px 20px;
  outline: none;
  box-shadow: none;
  margin-left: 0;
}

.profile-img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
}

.profile-name {
  font-size: 0.9rem;
  font-weight: bold;
  color: #555;
}

.message-row {
  display: flex;
  margin-bottom: 10px;
}

.message-row.justify-end {
  justify-content: flex-end;
}

.message-row.justify-start {
  justify-content: flex-start;
}

.message-content {
  display: flex;
  align-items: flex-end;
}

.bot-message-content {
  align-items: flex-end;
}

.user-message-content {
  align-items: flex-end;
}

/* 메시지 버블 스타일 */
.message-bubble {
  max-width: 100%; /* 말풍선의 최대 너비를 75%로 설정하여 여백 확보 */
  padding: 10px 15px;
  border-radius: 20px;
  position: relative;
  word-wrap: break-word; /* 단어가 너무 길면 줄바꿈 */
  word-break: break-word; /* 단어가 너무 길면 줄바꿈 */
  margin-bottom: 2px;
  white-space: normal; /* 줄바꿈을 지원하도록 설정 */
}

/* 사용자 메시지 버블 스타일 */
.user-message {
  background-color: #9cd2d9;
  color: white;
  text-align: left;
  margin-left: auto; /* 추가 */
}


/* 봇 메시지 버블 스타일 */
.bot-message {
  background-color: #e5e5ea;
  color: black;
  text-align: left;
}

/* 봇 메시지 내 마크다운 스타일링 */
.bot-message p {
  margin: 0;
  padding: 0;
}

.bot-message ul, .bot-message ol {
  padding-left: 20px;
}

.bot-message li {
  margin-bottom: 5px;
}

.bot-message strong {
  font-weight: bold;
}

.bot-message em {
  font-style: italic;
}

.bot-message a {
  color: #007bff;
  text-decoration: none;
}

.bot-message a:hover {
  text-decoration: underline;
}
</style>
