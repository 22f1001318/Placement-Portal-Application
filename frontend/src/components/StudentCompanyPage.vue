<template>
  <div class="container py-4">
    <h3>{{ company.company_name }}</h3>
    <div class="alert alert-secondary">Overview: {{ company.overview || 'No overview yet.' }}</div>
    <h5>Current Drives</h5>
    <ul>
      <li v-for="drive in company.drives" :key="drive.id">
        {{ drive.drive_name }}
        <button class="btn btn-sm btn-outline-primary ms-2" @click="viewDrive(drive.id)">View Details</button>
      </li>
    </ul>
    <button class="btn btn-secondary" @click="goBack">Back</button>
  </div>
</template>

<script>
export default {
  name: 'StudentCompanyPage',
  data() {
    return { company: {} };
  },
  async mounted() {
    const id = this.$route.params.id;
    const response = await fetch(`/api/student/company/${id}/drives`);
    this.company = await response.json();
  },
  methods: {
    viewDrive(id) {
      this.$router.push(`/student/drive/${id}`);
    },
    goBack() {
      this.$router.push('/student/dashboard');
    }
  }
};
</script>
