<template>
  <div class="container py-4">
    <h3>Update Application for the Drive</h3>
    <div class="alert alert-secondary">Job Title: {{ drive.job_title }}</div>
    <h5>Received Applications</h5>
    <table class="table table-bordered">
      <thead>
        <tr><th>Student Name</th><th>Action</th></tr>
      </thead>
      <tbody>
        <tr v-for="app in applications" :key="app.id">
          <td>{{ app.student_name }}</td>
          <td><button class="btn btn-sm btn-outline-primary" @click="review(app.id)">Review Application</button></td>
        </tr>
      </tbody>
    </table>
    <button class="btn btn-secondary" @click="goBack">Back</button>
  </div>
</template>

<script>
export default {
  name: 'DriveApplicationsPage',
  data() {
    return { drive: {}, applications: [] };
  },
  async mounted() {
    const id = this.$route.params.id;
    const response = await fetch(`/api/company/drives/${id}/applications`);
    const data = await response.json();
    this.drive = data.drive || {};
    this.applications = data.applications || [];
  },
  methods: {
    review(id) {
      this.$router.push(`/company/application/${id}`);
    },
    goBack() {
      this.$router.push('/company/dashboard');
    }
  }
};
</script>
