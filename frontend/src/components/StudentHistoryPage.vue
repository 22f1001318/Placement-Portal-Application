<template>
  <div class="container py-4">
    <h3>Student Application History</h3>
    <p><strong>Student Name:</strong> {{ profile.display_name }}</p>
    <p><strong>Department:</strong> {{ profile.department }}</p>
    <table class="table table-bordered">
      <thead>
        <tr><th>Drive No.</th><th>Job Title</th><th>Company</th><th>Results</th><th>Remarks</th></tr>
      </thead>
      <tbody>
        <tr v-for="item in history" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.job_title }}</td>
          <td>{{ item.company_name }}</td>
          <td>{{ item.result }}</td>
          <td>{{ item.remarks }}</td>
        </tr>
      </tbody>
    </table>
    <button class="btn btn-secondary" @click="goBack">Back</button>
  </div>
</template>

<script>
export default {
  name: 'StudentHistoryPage',
  data() {
    return { profile: {}, history: [] };
  },
  async mounted() {
    const response = await fetch('/api/student/history');
    const data = await response.json();
    this.profile = data;
    this.history = data.history || [];
  },
  methods: {
    goBack() {
      this.$router.push('/student/dashboard');
    }
  }
};
</script>
