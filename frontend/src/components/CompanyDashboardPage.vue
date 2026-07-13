<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3>Company Dashboard</h3>
      <div>
        <button class="btn btn-outline-secondary btn-sm me-2" @click="showOverviewPopup = true">Company Overview</button>
        <button class="btn btn-danger btn-sm" @click="logout">Logout</button>
      </div>
    </div>
    <div class="alert alert-info">Welcome, {{ profile.company_name || 'Company' }}</div>

    <div class="mb-3 text-end">
      <button class="btn btn-primary" @click="goCreateDrive">Create Drive</button>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h5>Upcoming Drive</h5>
        <table class="table table-bordered">
          <thead>
            <tr><th>Drive No.</th><th>Drive Name</th><th>Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="drive in upcoming" :key="drive.id">
              <td>{{ drive.id }}</td>
              <td>{{ drive.drive_name }}</td>
              <td>
                <button class="btn btn-sm btn-outline-primary me-2" @click="editDrive(drive.id)">Edit Drive</button>
                <button class="btn btn-sm btn-outline-info me-2" @click="viewApplications(drive.id)">View Details</button>
                <button class="btn btn-sm btn-outline-success" @click="markComplete(drive.id)">Mark as Complete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        <h5>Closed Drive</h5>
        <table class="table table-bordered">
          <thead>
            <tr><th>Drive No.</th><th>Drive Name</th><th>Action</th></tr>
          </thead>
          <tbody>
            <tr v-for="drive in closed" :key="drive.id">
              <td>{{ drive.id }}</td>
              <td>{{ drive.drive_name }}</td>
              <td><button class="btn btn-sm btn-outline-secondary" @click="editDrive(drive.id)">Update</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showOverviewPopup" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.2)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-body">
            <h5>Company Overview</h5>
            <textarea v-model="overviewText" class="form-control" rows="5"></textarea>
            <div class="mt-3 text-end">
              <button class="btn btn-secondary me-2" @click="showOverviewPopup = false">Close</button>
              <button class="btn btn-primary" @click="saveOverview">Save</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CompanyDashboardPage',
  data() {
    return {
      profile: {},
      upcoming: [],
      closed: [],
      overviewText: '',
      showOverviewPopup: false,
    };
  },
  async mounted() {
    await this.loadDashboard();
  },
  methods: {
    async loadDashboard() {
      const response = await fetch('/api/dashboard');
      const data = await response.json();
      this.profile = data.profile || {};
      this.upcoming = data.upcoming || [];
      this.closed = data.closed || [];
      this.overviewText = this.profile.overview || '';
    },
    async saveOverview() {
      await fetch('/api/company/overview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ overview: this.overviewText }),
      });
      this.showOverviewPopup = false;
      await this.loadDashboard();
    },
    goCreateDrive() {
      this.$router.push('/company/create-drive');
    },
    editDrive(id) {
      this.$router.push(`/company/edit-drive/${id}`);
    },
    async viewApplications(id) {
      this.$router.push(`/company/applications/${id}`);
    },
    async markComplete(id) {
      if (confirm('Mark this drive as complete?')) {
        await fetch(`/api/company/drives/${id}/complete`, { method: 'POST' });
        await this.loadDashboard();
      }
    },
    async logout() {
      await fetch('/api/logout', { method: 'POST' });
      this.$router.push('/login');
    }
  }
};
</script>
