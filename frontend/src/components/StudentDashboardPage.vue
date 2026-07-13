<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3>Student Dashboard</h3>
      <button class="btn btn-danger btn-sm" @click="logout">Logout</button>
    </div>
    <div class="alert alert-info">Welcome, {{ profile.display_name || 'Student' }}</div>
    <div class="mb-3">
      <button class="btn btn-outline-secondary me-2" @click="showProfile = true">Edit Profile</button>
      <button class="btn btn-outline-primary" @click="goHistory">History</button>
    </div>
    <div class="card mb-4">
      <div class="card-body">
        <h5>Organisation</h5>
        <table class="table table-bordered">
          <thead><tr><th>Company Name</th><th>Action</th></tr></thead>
          <tbody>
            <tr v-for="company in companies" :key="company.id">
              <td>{{ company.company_name }}</td>
              <td><button class="btn btn-sm btn-outline-info" @click="viewCompany(company.id)">View Details</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showProfile" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.2)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-body">
            <h5>Edit Profile</h5>
            <div class="mb-3">
              <label class="form-label">Student Name</label>
              <input v-model="profile.display_name" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">Department</label>
              <input v-model="profile.department" class="form-control" />
            </div>
            <div class="text-end">
              <button class="btn btn-secondary me-2" @click="showProfile = false">Close</button>
              <button class="btn btn-primary" @click="saveProfile">Save</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentDashboardPage',
  data() {
    return { profile: {}, companies: [], showProfile: false };
  },
  async mounted() {
    await this.load();
  },
  methods: {
    async load() {
      const response = await fetch('/api/dashboard');
      const data = await response.json();
      this.profile = data.profile || {};
      this.companies = data.companies || [];
    },
    async saveProfile() {
      await fetch('/api/student/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.profile),
      });
      this.showProfile = false;
      await this.load();
    },
    viewCompany(id) {
      this.$router.push(`/student/company/${id}`);
    },
    goHistory() {
      this.$router.push('/student/history');
    },
    async logout() {
      await fetch('/api/logout', { method: 'POST' });
      this.$router.push('/login');
    }
  }
};
</script>
