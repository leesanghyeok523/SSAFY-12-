//  import { defineStore } from 'pinia';
//  import axios from 'axios';
 
//  export const useAuthStore = defineStore('auth', {
//      state: () => ({
//          isAuthenticated: !!localStorage.getItem('accessToken'),
//          accessToken: localStorage.getItem('accessToken') || null,
//          profile: null, // 사용자 프로필 데이터
//      }),
//      actions: {
//          async login(username, password) {
//              try {
//                  const response = await axios.post('http://127.0.0.1:8000/api/auth/login/', {
//                      username,
//                      password,
//                  });
 
//                  const { key } = response.data;
//                  this.accessToken = key;
//                  localStorage.setItem('accessToken', key);
//                  this.isAuthenticated = true;
 
//                  console.log('로그인 성공:', response.data);
 
//                  // 로그인 후 프로필 가져오기
//                  await this.fetchProfile();
//              } catch (error) {
//                  console.error('로그인 실패:', error.response?.data || error.message);
//                  throw new Error('로그인 실패');
//              }
//          },
//          async logout() {
//              try {
//                  if (!this.accessToken) {
//                      throw new Error('로그아웃 실패: 토큰이 없습니다.');
//                  }
 
//                  const response = await axios.post(
//                      'http://127.0.0.1:8000/api/auth/logout/',
//                      null,
//                      {
//                          headers: {
//                              Authorization: `Token ${this.accessToken}`,
//                          },
//                      }
//                  );
 
//                  console.log('로그아웃 성공:', response.data);
//                  this.clearSession();
//              } catch (error) {
//                  if (error.response?.status === 401) {
//                      console.error('로그아웃 실패: 유효하지 않은 토큰. 세션 초기화');
//                      this.clearSession();
//                  } else {
//                      console.error('로그아웃 실패:', error.response?.data || error.message);
//                      throw new Error('로그아웃 실패');
//                  }
//              }
//          },
//          clearSession() {
//              this.isAuthenticated = false;
//              this.accessToken = null;
//              this.profile = null; // 프로필 데이터 초기화
//              localStorage.removeItem('accessToken');
//          },
//          async fetchProfile() {
//              try {
//                  const response = await axios.get('http://127.0.0.1:8000/api/core/actions/profile/', {
//                      headers: {
//                          Authorization: `Token ${this.accessToken}`,
//                      },
//                  });
//                  this.profile = response.data;
//                  console.log('프로필 데이터:', response.data);
//              } catch (error) {
//                  console.error('프로필 데이터 가져오기 실패:', error.response?.data || error.message);
//                  throw new Error('프로필 데이터 가져오기 실패');
//              }
//          },
//      },
//  });


import { defineStore } from 'pinia';
import axios from 'axios';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        isAuthenticated: !!localStorage.getItem('accessToken'),
        accessToken: localStorage.getItem('accessToken') || null,
        profile: null, // 사용자 프로필 데이터
    }),
    actions: {
        async login(username, password) {
            try {
                const response = await axios.post('http://127.0.0.1:8000/api/auth/login/', {
                    username,
                    password,
                });

                const { key } = response.data;
                this.accessToken = key;
                localStorage.setItem('accessToken', key);
                this.isAuthenticated = true;

                console.log('로그인 성공:', response.data);

                // 로그인 후 프로필 가져오기
                await this.fetchProfile();
            } catch (error) {
                console.error('로그인 실패:', error.response?.data || error.message);
                throw new Error('로그인 실패');
            }
        },
        async logout() {
            try {
                if (!this.accessToken) {
                    console.warn('로그아웃 시도: 토큰이 없습니다. 세션을 초기화합니다.');
                    this.clearSession();
                    return;
                }

                const response = await axios.post(
                    'http://127.0.0.1:8000/api/auth/logout/',
                    null,
                    {
                        headers: {
                            Authorization: `Token ${this.accessToken}`,
                        },
                    }
                );

                console.log('로그아웃 성공:', response.data);
                this.clearSession();
            } catch (error) {
                if (error.response?.status === 401) {
                    console.warn('로그아웃 실패: 유효하지 않은 토큰. 세션을 초기화합니다.');
                    this.clearSession();
                } else {
                    console.error('로그아웃 실패:', error.response?.data || error.message);
                    throw new Error('로그아웃 실패');
                }
            }
        },
        clearSession() {
            this.isAuthenticated = false;
            this.accessToken = null;
            this.profile = null; // 프로필 데이터 초기화
            localStorage.removeItem('accessToken');
            console.log('세션이 초기화되었습니다.');
        },
        async fetchProfile() {
            try {
                if (!this.accessToken) {
                    throw new Error('토큰이 없습니다. 프로필 데이터를 가져올 수 없습니다.');
                }

                const response = await axios.get('http://127.0.0.1:8000/api/core/actions/profile/', {
                    headers: {
                        Authorization: `Token ${this.accessToken}`,
                    },
                });
                this.profile = response.data;
                console.log('프로필 데이터:', response.data);
            } catch (error) {
                console.error('프로필 데이터 가져오기 실패:', error.response?.data || error.message);

                // 인증 실패 시 세션 초기화
                if (error.response?.status === 401) {
                    console.warn('인증이 만료되었습니다. 세션을 초기화합니다.');
                    this.clearSession();
                }

                throw new Error('프로필 데이터 가져오기 실패');
            }
        },
    },
});
