<template>
  <div class="container py-4">
    <h3>{{ drive.drive_name }}</h3>
    <p><strong>Job Title:</strong> {{ drive.job_title }}</p>
    <p><strong>Job Description:</strong> {{ drive.job_description }}</p>
    <div class="mt-3">
      <button class="btn btn-primary" @click="apply">Apply</button>
      <button class="btn btn-secondary ms-2" @click="goBack">Back</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentDrivePage',
  data() {
    return { drive: {} };
  },
  async mounted() {
    const id = this.$route.params.id;
    const response = await fetch(`/api/student/drives/${id}`);
    this.drive = await response.json();
  },
  methods: {
    async apply() {
      const response = await fetch(`/api/student/apply/${this.drive.id}`, { method: 'POST' });
      const data = await response.json();
      alert(data.message || 'Applied');
    },
    goBack() {
      this.$router.push('/student/dashboard');
    }
  }
};
</script>
