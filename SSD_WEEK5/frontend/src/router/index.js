import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import CredentialLeak from '../components/CredentialLeak.vue';
import NetworkIntelligence from '../components/NetworkIntelligence.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/credential-leak',
    name: 'CredentialLeak',
    component: CredentialLeak
  },
  {
    path: '/network-intelligence',
    name: 'NetworkIntelligence',
    component: NetworkIntelligence
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router; 