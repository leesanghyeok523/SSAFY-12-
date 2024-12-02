<!-- <template>
  <div class="profile-page">
    <div class="header">
      <span class="nav-link" @click="goToProfilePage">회원 정보 관리</span>
      <span class="divider">|</span>
      <span class="nav-link" @click="goToJoinedProducts">내가 가입한 상품</span>
    </div>
    <div class="content">
      <div class="profile-image-section">
        <img :src="profileImageUrl" alt="프로필 이미지" class="profile-image" />
        <label for="profile-image-upload" class="upload-button">프로필 이미지 변경</label>
        <input
          id="profile-image-upload"
          type="file"
          @change="changeProfileImage"
          style="display: none;"
        />
      </div>
      <div class="profile-details-section">
        <h1>{{ profile?.username || "사용자" }}님 환영합니다</h1>
        <table class="profile-table">
          <tbody>
            <tr>
              <td><strong>ID</strong></td>
              <td>{{ profile?.username || "불러오는 중..." }}</td>
            </tr>
            <tr>
              <td><strong>Email</strong></td>
              <td>{{ profile?.email || "불러오는 중..." }}</td>
            </tr>
            <tr>
              <td><strong>닉네임</strong></td>
              <td>{{ profile?.nickname || "불러오는 중..." }}</td>
            </tr>
            <tr>
              <td><strong>생년월일</strong></td>
              <td>{{ profile?.date_of_birth || "불러오는 중..." }}</td>
            </tr>
            <tr>
              <td><strong>나이</strong></td>
              <td>{{ age || "계산 중..." }}</td>
            </tr>
            <tr>
              <td><strong>자산</strong></td>
              <td>
                <span v-if="!isEditingAssets">{{ profile?.current_assets || "0" }}</span>
                <div v-else class="edit-section">
                  <input
                    type="number"
                    v-model="editedAssets"
                    class="editable-input"
                  />
                  <button @click="saveAssets" class="save-button">확인</button>
                </div>
                <span @click="startEditingAssets" class="edit-icon" v-if="!isEditingAssets">✏️</span>
              </td>
            </tr>
            <tr>
              <td><strong>연봉</strong></td>
              <td>
                <span v-if="!isEditingIncome">{{ profile?.income_level || "0" }}</span>
                <div v-else class="edit-section">
                  <input
                    type="number"
                    v-model="editedIncome"
                    class="editable-input"
                  />
                  <button @click="saveIncome" class="save-button">확인</button>
                </div>
                <span @click="startEditingIncome" class="edit-icon" v-if="!isEditingIncome">✏️</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import axios from "axios";

export default {
  setup() {
    const profile = ref(null);
    const profileImageUrl = ref("/default-profile-image.webp"); // 기본 프로필 이미지
    const age = ref(null); // 나이 저장

    // 편집 상태 관리
    const isEditingAssets = ref(false);
    const isEditingIncome = ref(false);
    const editedAssets = ref(0);
    const editedIncome = ref(0);

    // 프로필 데이터 가져오기
    const fetchProfile = () => {
      axios
        .get("http://127.0.0.1:8000/api/core/actions/profile/", {
          headers: {
            Authorization: `Token ${localStorage.getItem("accessToken")}`,
          },
        })
        .then((response) => {
          profile.value = response.data;

          // 프로필 이미지 URL 업데이트
          if (response.data.profile_picture) {
            profileImageUrl.value = `http://127.0.0.1:8000${response.data.profile_picture}`;
          }

          // 생년월일로 나이 계산
          if (response.data.date_of_birth) {
            calculateAge(response.data.date_of_birth);
          }
        })
        .catch((error) => {
          console.error("프로필 데이터를 가져오는 중 오류 발생:", error);
        });
    };

    // 나이 계산 함수
    const calculateAge = (dateOfBirth) => {
      if (!dateOfBirth) return; // 생년월일이 없는 경우 처리

      const birthDate = new Date(dateOfBirth);
      const today = new Date();
      let calculatedAge = today.getFullYear() - birthDate.getFullYear();

      // 생일이 아직 지나지 않은 경우 나이에서 1을 뺌
      const monthDiff = today.getMonth() - birthDate.getMonth();
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        calculatedAge--;
      }

      age.value = calculatedAge;
    };

    // 프로필 이미지 변경
    const changeProfileImage = (event) => {
      const file = event.target.files[0];
      if (!file) return;

      // 미리보기 URL 생성
      const previewUrl = URL.createObjectURL(file);
      profileImageUrl.value = previewUrl;

      // 서버로 파일 업로드
      const formData = new FormData();
      formData.append("profile_picture", file);

      axios
        .put("http://127.0.0.1:8000/api/core/actions/update_profile_img/", formData, {
          headers: {
            Authorization: `Token ${localStorage.getItem("accessToken")}`,
          },
        })
        .then((response) => {
          console.log("프로필 이미지 변경 성공:", response.data);
          if (response.data.profile_picture) {
            profileImageUrl.value = `http://127.0.0.1:8000${response.data.profile_picture}`;
          }
        })
        .catch((error) => {
          console.error("프로필 이미지 변경 중 오류 발생:", error.response);
        });
    };

    // 자산 편집 시작
    const startEditingAssets = () => {
      isEditingAssets.value = true;
      editedAssets.value = profile.value?.current_assets || 0; // 값이 없으면 기본값 0
    };

    // 자산 저장
    const saveAssets = () => {
      axios
        .put(
          "http://127.0.0.1:8000/api/core/actions/profile/",
          { current_assets: editedAssets.value },
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("accessToken")}`,
              "Content-Type": "application/json",
            },
          }
        )
        .then(() => {
          profile.value.current_assets = editedAssets.value; // UI 갱신
          isEditingAssets.value = false; // 편집 모드 종료
        })
        .catch((error) => {
          console.error("자산 업데이트 중 오류 발생:", error);
        });
    };

    // 연봉 편집 시작
    const startEditingIncome = () => {
      isEditingIncome.value = true;
      editedIncome.value = profile.value?.income_level || 0; // 값이 없으면 기본값 0
    };

    // 연봉 저장
    const saveIncome = () => {
      axios
        .put(
          "http://127.0.0.1:8000/api/core/actions/profile/",
          { income_level: editedIncome.value },
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("accessToken")}`,
              "Content-Type": "application/json",
            },
          }
        )
        .then(() => {
          profile.value.income_level = editedIncome.value; // UI 갱신
          isEditingIncome.value = false; // 편집 모드 종료
        })
        .catch((error) => {
          console.error("연봉 업데이트 중 오류 발생:", error);
        });
    };

    const goToProfilePage = () => {
      window.location.href = "/profile";
    };

    const goToJoinedProducts = () => {
      window.location.href = "/joined-products";
    };

    // 컴포넌트가 로드되면 프로필 데이터를 가져옴
    onMounted(() => {
      fetchProfile();
    });

    return {
      profile,
      profileImageUrl,
      age,
      fetchProfile,
      changeProfileImage,
      startEditingAssets,
      saveAssets,
      startEditingIncome,
      saveIncome,
      isEditingAssets,
      isEditingIncome,
      editedAssets,
      editedIncome,
      goToProfilePage,
      goToJoinedProducts,
    };
  },
};
</script>

 -->




 <template>
  <div class="profile-page">
    <div class="header">
      <span class="nav-link" @click="goToProfilePage">회원 정보 관리</span>
      <span class="divider">|</span>
      <span class="nav-link" @click="goToJoinedProducts">내가 가입한 상품</span>
    </div>
    <div class="content">
      <div class="profile-image-section">
        <img
          :src="profileImageUrl"
          alt="프로필 이미지"
          class="profile-image"
        />
        <label for="profile-image-upload" class="upload-button">프로필 이미지 변경</label>
        <input
          id="profile-image-upload"
          type="file"
          @change="changeProfileImage"
          style="display: none;"
        />
      </div>
      <div class="profile-details-section">
        <h1>{{ profile?.username || "사용자" }}님 환영합니다</h1>
        <table class="profile-table">
          <tbody>
            <tr>
              <td><strong>ID</strong></td>
              <td>{{ profile?.username || "불러오는 중..." }}</td>
            </tr>
            <tr>
              <td><strong>Email</strong></td>
              <td>{{ profile?.email || "불러오는 중..." }}</td>
            </tr>
            <tr>
              <td><strong>닉네임</strong></td>
              <td>{{ profile?.nickname || "불러오는 중..." }}</td>
            </tr>
            <tr>
              <td><strong>생년월일</strong></td>
              <td>{{ profile?.date_of_birth || "불러오는 중..." }}</td>
            </tr>
            <tr>
              <td><strong>나이</strong></td>
              <td>{{ age || "계산 중..." }}</td>
            </tr>
            <tr>
              <td><strong>자산</strong></td>
              <td>
                <span v-if="!isEditingAssets">{{ profile?.current_assets || "0" }}</span>
                <div v-else class="edit-section">
                  <input
                    type="number"
                    v-model="editedAssets"
                    class="editable-input"
                  />
                  <button @click="saveAssets" class="save-button">확인</button>
                </div>
                <span @click="startEditingAssets" class="edit-icon" v-if="!isEditingAssets">✏️</span>
              </td>
            </tr>
            <tr>
              <td><strong>연봉</strong></td>
              <td>
                <span v-if="!isEditingIncome">{{ profile?.income_level || "0" }}</span>
                <div v-else class="edit-section">
                  <input
                    type="number"
                    v-model="editedIncome"
                    class="editable-input"
                  />
                  <button @click="saveIncome" class="save-button">확인</button>
                </div>
                <span @click="startEditingIncome" class="edit-icon" v-if="!isEditingIncome">✏️</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import axios from "axios";
import defaultProfileImage from "@/assets/none-profile-image.jpg"; // 기본 이미지 가져오기
import { useRouter } from "vue-router";

export default {
  setup() {
    const profile = ref(null);
    const profileImageUrl = ref(null);
    const age = ref(null);
    const router = useRouter();

    // 편집 상태 관리
    const isEditingAssets = ref(false);
    const isEditingIncome = ref(false);
    const editedAssets = ref(0);
    const editedIncome = ref(0);

    // 나이 계산 함수
    const calculateAge = (dateOfBirth) => {
      if (!dateOfBirth) return;

      const birthDate = new Date(dateOfBirth);
      const today = new Date();
      let calculatedAge = today.getFullYear() - birthDate.getFullYear();

      const monthDiff = today.getMonth() - birthDate.getMonth();
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        calculatedAge--;
      }

      age.value = calculatedAge; // 계산된 나이를 저장
    };

    // 프로필 데이터 가져오기
    const fetchProfile = () => {
      axios
        .get("http://127.0.0.1:8000/api/core/actions/profile/", {
          headers: {
            Authorization: `Token ${localStorage.getItem("accessToken")}`,
          },
        })
        .then((response) => {
          profile.value = response.data;

          // 프로필 이미지 설정
          if (response.data.profile_picture) {
            profileImageUrl.value = `http://127.0.0.1:8000${response.data.profile_picture}`;
          } else {
            profileImageUrl.value = defaultProfileImage; // 기본 이미지
          }

          // 생년월일로 나이 계산
          if (response.data.date_of_birth) {
            calculateAge(response.data.date_of_birth);
          }
        })
        .catch((error) => {
          console.error("프로필 데이터를 가져오는 중 오류 발생:", error);
        });
    };

    const changeProfileImage = (event) => {
      const file = event.target.files[0];
      if (!file) return;

      const previewUrl = URL.createObjectURL(file);
      profileImageUrl.value = previewUrl;

      const formData = new FormData();
      formData.append("profile_picture", file);

      axios
        .put("http://127.0.0.1:8000/api/core/actions/update_profile_img/", formData, {
          headers: {
            Authorization: `Token ${localStorage.getItem("accessToken")}`,
          },
        })
        .then((response) => {
          if (response.data.profile_picture) {
            profileImageUrl.value = `http://127.0.0.1:8000${response.data.profile_picture}`;
          }
        })
        .catch((error) => {
          console.error("프로필 이미지 변경 중 오류 발생:", error.response);
        });
    };

    // 자산 편집 시작
    const startEditingAssets = () => {
      isEditingAssets.value = true;
      editedAssets.value = profile.value?.current_assets || 0; // 값이 없으면 기본값 0
    };

    // 자산 저장
    const saveAssets = () => {
      axios
        .put(
          "http://127.0.0.1:8000/api/core/actions/profile/",
          { current_assets: editedAssets.value },
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("accessToken")}`,
              "Content-Type": "application/json",
            },
          }
        )
        .then(() => {
          profile.value.current_assets = editedAssets.value; // UI 갱신
          isEditingAssets.value = false; // 편집 모드 종료
        })
        .catch((error) => {
          console.error("자산 업데이트 중 오류 발생:", error);
        });
    };

    // 연봉 편집 시작
    const startEditingIncome = () => {
      isEditingIncome.value = true;
      editedIncome.value = profile.value?.income_level || 0; // 값이 없으면 기본값 0
    };

    // 연봉 저장
    const saveIncome = () => {
      axios
        .put(
          "http://127.0.0.1:8000/api/core/actions/profile/",
          { income_level: editedIncome.value },
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("accessToken")}`,
              "Content-Type": "application/json",
            },
          }
        )
        .then(() => {
          profile.value.income_level = editedIncome.value; // UI 갱신
          isEditingIncome.value = false; // 편집 모드 종료
        })
        .catch((error) => {
          console.error("연봉 업데이트 중 오류 발생:", error);
        });
    };

    const goToProfilePage = () => {
      router.push("/profile");
    };

    const goToJoinedProducts = () => {
      router.push("/joined-products");
    };

    onMounted(() => {
      fetchProfile();
    });

    return {
      profile,
      profileImageUrl,
      age, // age 변수를 반환
      fetchProfile,
      calculateAge, // 함수 반환
      changeProfileImage,
      goToProfilePage,
      goToJoinedProducts,
      startEditingAssets,
      saveAssets,
      startEditingIncome,
      saveIncome,
      isEditingAssets,
      isEditingIncome,
      editedAssets,
      editedIncome,
    };
  },
};

</script>




<style scoped>
/* 전체 페이지 */
.profile-page {
  height: 100vh;
  background-image: url('@/assets/profile.jpg');
  background-size: 2100px 950px;
  background-position: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  font-family: Arial, sans-serif;
  color: white;
  padding-top: 100px;
}

/* 헤더 스타일 */
.header {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

.nav-link {
  cursor: pointer;
  font-size: 1.2rem;
  color: white;
}

.nav-link:hover {
  text-decoration: underline;
}

/* 페이지 컨텐츠 */
.content {
  display: flex;
  align-items: flex-start;
  gap: 80px; /* 섹션 간격 조정 */
  margin-top: 30px;
}

/* 프로필 이미지 섹션 */
.profile-image-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.profile-image-wrapper {
  width: 200px; /* 크기 증가 */
  height: 200px; /* 크기 증가 */
  background-color: rgba(0, 0, 0, 0.3);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
}

.profile-image {
  width: 180px; /* 이미지 크기 증가 */
  height: 180px; /* 이미지 크기 증가 */
  border-radius: 50%;
  object-fit: cover;
}

.upload-button {
  display: inline-block;
  cursor: pointer;
  color: white;
  background: linear-gradient(to right, #5a0eab, #1f5fc8);
  padding: 12px 25px; /* 버튼 크기 증가 */
  border-radius: 5px;
  text-align: center;
  font-size: 1rem; /* 버튼 텍스트 크기 증가 */
  margin-top: 15px; /* 버튼 위치 아래로 조정 */
}


.upload-button:hover {
  background: linear-gradient(to right, #490d96, #14439e);
}

/* 프로필 디테일 섹션 */
.profile-details-section {
  background: rgba(0, 0, 0, 0.7);
  border-radius: 10px;
  padding: 30px; /* 내부 여백 증가 */
  width: 500px; /* 섹션 너비 증가 */
}

.profile-details-section h1 {
  font-size: 1.8rem; /* 타이틀 크기 증가 */
  text-align: center;
  margin-bottom: 20px;
}

.profile-table {
  width: 100%;
  border-collapse: collapse;
}

.profile-table th,
.profile-table td {
  padding: 12px; /* 셀 간격 증가 */
  font-size: 1rem; /* 텍스트 크기 증가 */
}

.editable-input {
  width: 120px; /* 입력 필드 크기 증가 */
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: white; /* 입력 필드 배경색 */
  color: black; /* 텍스트 색상 */
}

.editable-input:focus {
  outline: 2px solid #007bff;
}

.edit-icon {
  cursor: pointer;
  margin-left: 10px;
  color: white;
}

.edit-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.save-button {
  margin-left: 10px;
  padding: 8px 15px; /* 버튼 크기 증가 */
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem; /* 버튼 텍스트 크기 증가 */
}

.save-button:hover {
  background: #0056b3;
}
</style>


