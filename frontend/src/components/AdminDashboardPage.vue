<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3>Admin Dashboard</h3>
      <button class="btn btn-danger btn-sm" @click="logout">Logout</button>
    </div>
    <div class="alert alert-info">Welcome, {{ adminName }}</div>

    <div class="row mb-3">
      <div class="col-md-8">
        <input v-model="searchText" class="form-control" placeholder="Search company or student" />
      </div>
      <div class="col-md-4">
        <button class="btn btn-outline-primary w-100" @click="search">Search</button>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h5>Company Applications</h5>
        <ul class="list-group">
          <li v-for="company in pendingCompanies" :key="company.id" class="list-group-item d-flex justify-content-between align-items-center">
            <span>{{ company.company_name }}</span>
            <button class="btn btn-sm btn-success" @click="approveCompany(company.id)">Approve</button>
          </li>
          <li v-if="pendingCompanies.length === 0" class="list-group-item text-muted">No pending company applications.</li>
        </ul>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h5>Registered Company</h5>
        <ul class="list-group">
          <li v-for="company in approvedCompanies" :key="company.id" class="list-group-item d-flex justify-content-between align-items-center">
            <span>{{ company.company_name }}</span>
            <button class="btn btn-sm btn-warning" @click="toggleCompany(company.id, company.active)">{{ company.active ? 'Blocklist' : 'Unblock' }}</button>
          </li>
        </ul>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h5>Registered Students</h5>
        <ul class="list-group">
          <li v-for="student in students" :key="student.id" class="list-group-item d-flex justify-content-between align-items-center">
            <span>{{ student.display_name }}</span>
            <button class="btn btn-sm btn-warning" @click="toggleStudent(student.id, student.active)">{{ student.active ? 'Blocklist' : 'Unblock' }}</button>
          </li>
        </ul>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h5>Ongoing Drive</h5>
        <table class="table table-bordered">
          <thead>
            <tr><th>Drive No.</th><th>Drive Name</th><th>Action</th></tr>
          </thead>
          <tbody>
            <tr v-for="drive in drives" :key="drive.id">
              <td>{{ drive.id }}</td>
              <td>{{ drive.drive_name }}</td>
              <td>
                <button class="btn btn-sm btn-outline-info me-2" @click="viewDrive(drive.id)">View Details</button>
                <button class="btn btn-sm btn-outline-success" @click="completeDrive(drive.id)">Mark As Complete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        <h5>Student Applications</h5>
        <table class="table table-bordered">
          <thead>
            <tr><th>Sr. No</th><th>Name</th><th>Drive Name</th><th>Company Name</th><th>Date</th><th>Action</th></tr>
          </thead>
          <tbody>
            <tr v-for="application in applications" :key="application.id">
              <td>{{ application.id }}</td>
              <td>{{ application.student_name }}</td>
              <td>{{ application.drive_name }}</td>
              <td>{{ application.company_name }}</td>
              <td>{{ application.date }}</td>
              <td><button class="btn btn-sm btn-outline-info" @click="viewApplication(application.id)">View</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showDriveModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.2)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-body">
            <h5>Drive Details</h5>
            <p><strong>Drive Name:</strong> {{ selectedDrive.drive_name }}</p>
            <p><strong>Job Title:</strong> {{ selectedDrive.job_title }}</p>
            <p><strong>Job Description:</strong> {{ selectedDrive.job_description }}</p>
            <p><strong>Eligibility:</strong> {{ selectedDrive.eligibility }}</p>
            <p><strong>Deadline:</strong> {{ selectedDrive.application_deadline }}</p>
            <div class="text-end">
              <button class="btn btn-secondary" @click="showDriveModal = false">Back</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showApplicationModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.2)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-body">
            <h5>Student Application</h5>
            <p><strong>Name:</strong> {{ selectedApplication.student_name }}</p>
            <p><strong>Drive:</strong> {{ selectedApplication.drive_name }}</p>
            <p><strong>Company:</strong> {{ selectedApplication.company_name }}</p>
            <p><strong>Status:</strong> {{ selectedApplication.status }}</p>
            <p><strong>Date:</strong> {{ selectedApplication.date }}</p>
            <div class="text-end">
              <button class="btn btn-secondary" @click="showApplicationModal = false">Back</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboardPage',
  data() {
    return {
      adminName: 'Admin',
      pendingCompanies: [],
      approvedCompanies: [],
      students: [],
      drives: [],
      applications: [],
      searchText: '',
      showDriveModal: false,
      showApplicationModal: false,
      selectedDrive: {},
      selectedApplication: {},
    };
  },
  async mounted() {
    await this.load();
    const me = await fetch('/api/me');
    const user = await me.json();
    this.adminName = user.display_name || 'Admin';
  },
  methods: {
    async load() {
      const response = await fetch('/api/admin/dashboard');
      const data = await response.json();
      this.pendingCompanies = data.pending_companies || [];
      this.approvedCompanies = data.approved_companies || [];
      this.students = data.students || [];
      this.drives = data.drives || [];
      this.applications = data.applications || [];
    },
    async search() {
      const response = await fetch(`/api/admin/search?q=${encodeURIComponent(this.searchText)}`);
      const data = await response.json();
      if (data.results) {
        this.approvedCompanies = data.results;
      } else {
        await this.load();
      }
    },
    async approveCompany(id) {
      if (confirm('Approve this company?')) {
        await fetch(`/api/admin/companies/${id}/approve`, { method: 'POST' });
        await this.load();
      }
    },
    async toggleCompany(id, active) {
      const action = active ? 'block' : 'unblock';
      if (confirm(`Do you want to ${action} this company?`)) {
        await fetch(`/api/admin/companies/${id}/${action}`, { method: 'POST' });
        await this.load();
      }
    },
    async toggleStudent(id, active) {
      const action = active ? 'block' : 'unblock';
      if (confirm(`Do you want to ${action} this student?`)) {
        await fetch(`/api/admin/students/${id}/${action}`, { method: 'POST' });
        await this.load();
      }
    },
    async completeDrive(id) {
      if (confirm('Mark this drive as complete?')) {
        await fetch(`/api/admin/drives/${id}/complete`, { method: 'POST' });
        await this.load();
      }
    },
    async viewDrive(id) {
      const response = await fetch(`/api/admin/drives/${id}`);
      this.selectedDrive = await response.json();
      this.showDriveModal = true;
    },
    async viewApplication(id) {
      const response = await fetch(`/api/admin/applications/${id}`);
      this.selectedApplication = await response.json();
      this.showApplicationModal = true;
    },
    async logout() {
      await fetch('/api/logout', { method: 'POST' });
      this.$router.push('/login');
    }
  }
};
</script>
