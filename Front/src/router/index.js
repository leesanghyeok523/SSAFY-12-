import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

import HomePage from '@/views/HomePage.vue';
import LoginPage from '@/views/LoginPage.vue';
import SignupPage from '@/views/SignupPage.vue';
import MapPage from '@/views/MapPage.vue';
import SavingsComparisonPage from '@/views/SavingsComparisonPage.vue';
// import SavingsDetailPage from '@/views/SavingsDetailPage.vue';
import ProfilePage from '@/views/ProfilePage.vue';
import ExchangeRates from '@/views/ExchangeRatesPage.vue';
import CommunityPosts from '@/views/CommunityPosts.vue';
import CreatePostPage from '@/views/CreatePostPage.vue';
import JoinedProductsPage from '@/views/JoinedProductsPage.vue';
import ChatBox from '@/views/ChatBox.vue'; // ChatBox 연결
import IncomeLevelCal from '@/views/IncomeLevelCal.vue'
import Recommend from "@/views/Recommend.vue";

import HeroSection from '@/components/HeroSection.vue'; // components 폴더에서 가져옴
import IndependentSection from '@/components/IndependentSection.vue'; // components 폴더에서 가져옴

const routes = [
  { path: '/', component: HomePage },
  { path: '/login', component: LoginPage },
  { path: '/signup', component: SignupPage },
  { path: '/map', component: MapPage, meta: { requiresAuth: true } },
  { path: '/savings-comparison', component: SavingsComparisonPage, meta: { requiresAuth: true } },
  // { path: '/savings-detail/:id', component: SavingsDetailPage, props: true, meta: { requiresAuth: true } },
  { path: '/profile', component: ProfilePage, meta: { requiresAuth: true } },
  { path: '/exchange-rates', component: ExchangeRates, meta: { requiresAuth: true } },
  { path: '/community_posts', component: CommunityPosts, meta: { requiresAuth: true } },
  { path: '/community_posts/create', component: CreatePostPage, meta: { requiresAuth: true } },
  { path: '/joined-products', component: JoinedProductsPage, meta: { requiresAuth: true } },
  { path: '/report-summary', component: ChatBox, meta: { requiresAuth: true } }, // ChatBox 전용 경로 추가
  { path: '/income-level-calculator', component: IncomeLevelCal, meta: { requiresAuth: true } }, // 소득분위 계산기 경로 추가
  { path: '/recommend', component: Recommend, meta: { requiresAuth: true } }, // ChatBox 전용 경로 추가

  { path: '/hero', component: HeroSection }, // 히어로 섹션
  { path: '/independent', component: IndependentSection }, // 독립 섹션
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 라우터 가드
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login');
  } else {
    next();
  }
});

export default router;
