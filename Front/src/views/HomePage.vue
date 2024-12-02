<template>
  <div class="home-page">
    <HeroSection />
    <IndependentSection />
    <IndependentSection2 />
    <IndependentSection3 />
    <IndependentSection4 />
    <IndependentSection5 />
  </div>
</template>

<script>
import HeroSection from '../components/HeroSection.vue';
import IndependentSection from '../components/IndependentSection.vue';
import IndependentSection2 from '../components/IndependentSection2.vue';
import IndependentSection3 from '../components/IndependentSection3.vue';
import IndependentSection4 from '../components/IndependentSection4.vue';
import IndependentSection5 from '../components/IndependentSection5.vue';

export default {
  components: {
    HeroSection,
    IndependentSection,
    IndependentSection2,
    IndependentSection3,
    IndependentSection4,
    IndependentSection5,
  },
};
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
}
</style>
