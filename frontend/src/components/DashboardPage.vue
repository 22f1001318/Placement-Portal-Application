<template>
  <div class="container py-5">
    <h2 class="mb-4">Placement Portal Dashboard</h2>
    <div v-if="loading" class="text-muted">Loading...</div>
    <div v-else>
      <div class="alert alert-info">Welcome, {{ user.username }}. Role: {{ user.role }}</div>
      <pre class="bg-light p-3 rounded">{{ JSON.stringify(data, null, 2) }}</pre>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardPage',
  data() {
    return {
      loading: true,
      user: {},
      data: {},
    };
  },
  async mounted() {
    const me = await fetch('/api/me');
    this.user = await me.json();
    const response = await fetch('/api/dashboard');
    this.data = await response.json();
    this.loading = false;
  }
};
</script>
