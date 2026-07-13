<template>
  <div class="container py-5">
    <h2 class="mb-4">Admin Portal</h2>
    <div class="alert alert-primary">Manage companies, students, and placement drives.</div>
    <div class="card p-3">
      <h5>Pending drives</h5>
      <ul class="mb-0">
        <li v-for="drive in pendingDrives" :key="drive.id">{{ drive.job_title }} - {{ drive.status }}</li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminPage',
  data() {
    return {
      pendingDrives: [],
    };
  },
  async mounted() {
    const response = await fetch('/api/dashboard');
    const data = await response.json();
    this.pendingDrives = data.pending_drives || [];
  }
};
</script>
