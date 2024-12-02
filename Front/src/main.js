import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import BootstrapVue3 from 'bootstrap-vue-3';

import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue-3/dist/bootstrap-vue-3.css';

import { createVuetify } from 'vuetify';
import 'vuetify/styles'; // Vuetify 기본 스타일
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import { ko } from 'vuetify/locale'
import 'vuetify/styles'

const vuetify = createVuetify({
    components,
    directives,
    locale: {
        locale: 'ko',
        messages: { ko },
    }
})

const app = createApp(App)

app.use(BootstrapVue3);
app.use(createPinia()) // Pinia 사용
app.use(router) // Vue Router 사용
app.use(vuetify)


app.mount('#app')
