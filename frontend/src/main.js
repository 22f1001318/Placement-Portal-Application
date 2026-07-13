const CompanyDashboardPage = {
  template: `
    <div class="container py-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h3>Company Dashboard</h3>
        <div>
          <button class="btn btn-outline-secondary btn-sm me-2" @click="showOverviewPopup = true">Company Overview</button>
          <button class="btn btn-danger btn-sm" @click="logout">Logout</button>
        </div>
      </div>
      <div class="alert alert-info">Welcome, {{ profile.company_name || 'Company' }}</div>
      <div class="mb-3 text-end"><button class="btn btn-primary" @click="goCreateDrive">Create Drive</button></div>
      <div class="card mb-4"><div class="card-body"><h5>Upcoming Drive</h5><table class="table table-bordered"><thead><tr><th>Drive No.</th><th>Drive Name</th><th>Actions</th></tr></thead><tbody><tr v-for="drive in upcoming" :key="drive.id"><td>{{ drive.id }}</td><td>{{ drive.drive_name }}</td><td><button class="btn btn-sm btn-outline-primary me-2" @click="editDrive(drive.id)">Edit Drive</button><button class="btn btn-sm btn-outline-info me-2" @click="viewApplications(drive.id)">View Details</button><button class="btn btn-sm btn-outline-success" @click="markComplete(drive.id)">Mark as Complete</button></td></tr></tbody></table></div></div>
      <div class="card"><div class="card-body"><h5>Closed Drive</h5><table class="table table-bordered"><thead><tr><th>Drive No.</th><th>Drive Name</th><th>Action</th></tr></thead><tbody><tr v-for="drive in closed" :key="drive.id"><td>{{ drive.id }}</td><td>{{ drive.drive_name }}</td><td><button class="btn btn-sm btn-outline-secondary" @click="editDrive(drive.id)">Update</button></td></tr></tbody></table></div></div>
      <div v-if="showOverviewPopup" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.2)">
        <div class="modal-dialog"><div class="modal-content"><div class="modal-body"><h5>Company Overview</h5><textarea v-model="overviewText" class="form-control" rows="5"></textarea><div class="mt-3 text-end"><button class="btn btn-secondary me-2" @click="showOverviewPopup = false">Close</button><button class="btn btn-primary" @click="saveOverview">Save</button></div></div></div></div>
      </div>
    </div>
  `,
  data() { return { profile: {}, upcoming: [], closed: [], overviewText: '', showOverviewPopup: false }; },
  async mounted() { await this.loadDashboard(); },
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
      await fetch('/api/company/overview', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ overview: this.overviewText }) });
      this.showOverviewPopup = false;
      await this.loadDashboard();
    },
    goCreateDrive() { this.$router.push('/company/create-drive'); },
    editDrive(id) { this.$router.push(`/company/edit-drive/${id}`); },
    viewApplications(id) { this.$router.push(`/company/applications/${id}`); },
    async markComplete(id) { if (confirm('Mark this drive as complete?')) { await fetch(`/api/company/drives/${id}/complete`, { method: 'POST' }); await this.loadDashboard(); } },
    async logout() { await fetch('/api/logout', { method: 'POST' }); this.$router.push('/login'); }
  }
};

const CreateDrivePage = {
  template: `
    <div class="container py-4">
      <h3>Create a Drive</h3>
      <div class="card p-4 shadow-sm">
        <form @submit.prevent="saveDrive">
          <div class="mb-3"><label class="form-label">Drive Name</label><input v-model="drive.drive_name" class="form-control" required /></div>
          <div class="mb-3"><label class="form-label">Job Title</label><input v-model="drive.job_title" class="form-control" required /></div>
          <div class="mb-3"><label class="form-label">Job Description</label><textarea v-model="drive.job_description" class="form-control" rows="4" required></textarea></div>
          <div class="mb-3"><label class="form-label">Eligibility Criteria</label><textarea v-model="drive.eligibility" class="form-control" rows="3" required></textarea></div>
          <div class="row">
            <div class="col-md-6 mb-3"><label class="form-label">Salary</label><input v-model="drive.salary" type="number" min="0" class="form-control" required /></div>
            <div class="col-md-6 mb-3"><label class="form-label">Location</label><input v-model="drive.location" class="form-control" required /></div>
          </div>
          <div class="mb-3"><label class="form-label">Application Deadline</label><input v-model="drive.application_deadline" type="date" class="form-control" required /></div>
          <button class="btn btn-primary" type="submit">Save</button>
          <button class="btn btn-secondary ms-2" type="button" @click="goBack">Back</button>
        </form>
      </div>
    </div>
  `,
  data() { return { drive: { drive_name: '', job_title: '', job_description: '', eligibility: '', application_deadline: '', salary: 0, location: '' }, editId: null }; },
  async mounted() { const id = this.$route.params.id; if (id) { this.editId = Number(id); const response = await fetch(`/api/company/drives/${id}`); this.drive = await response.json(); } },
  methods: {
    async saveDrive() {
      const url = this.editId ? `/api/company/drives/${this.editId}` : '/api/company/drives';
      const method = this.editId ? 'PUT' : 'POST';
      const response = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(this.drive) });
      const data = await response.json();
      if (data.success) this.$router.push('/company/dashboard');
    },
    goBack() { this.$router.push('/company/dashboard'); }
  }
};

const DriveApplicationsPage = {
  template: `
    <div class="container py-4">
      <h3>Update Application for the Drive</h3>
      <div class="alert alert-secondary">Job Title: {{ drive.job_title }}</div>
      <h5>Received Applications</h5>
      <table class="table table-bordered"><thead><tr><th>Student Name</th><th>Action</th></tr></thead><tbody><tr v-for="app in applications" :key="app.id"><td>{{ app.student_name }}</td><td><button class="btn btn-sm btn-outline-primary" @click="review(app.id)">Review Application</button></td></tr></tbody></table>
      <button class="btn btn-secondary" @click="goBack">Back</button>
    </div>
  `,
  data() { return { drive: {}, applications: [] }; },
  async mounted() { const id = this.$route.params.id; const response = await fetch(`/api/company/drives/${id}/applications`); const data = await response.json(); this.drive = data.drive || {}; this.applications = data.applications || []; },
  methods: { review(id) { this.$router.push(`/company/application/${id}`); }, goBack() { this.$router.push('/company/dashboard'); } }
};

const ReviewApplicationPage = {
  template: `
    <div class="container py-4">
      <h3>Student Application</h3>
      <div class="card p-4">
        <p><strong>Student Name:</strong> {{ application.student_name }}</p>
        <p><strong>Department:</strong> {{ application.department }}</p>
        <p><strong>Drive:</strong> {{ application.drive_name }}</p>
        <p><strong>Job Title:</strong> {{ application.job_title }}</p>
        <div class="mb-3"><label class="form-label">Status</label><select v-model="application.status" class="form-select"><option value="shortlist">Shortlist</option><option value="waiting">Waiting</option><option value="reject">Reject</option></select></div>
        <div class="mb-3"><label class="form-label">Remarks</label><textarea v-model="application.remarks" class="form-control" rows="3"></textarea></div>
        <div class="mb-3"><button class="btn btn-outline-secondary" @click="goBack">Back</button><button class="btn btn-primary ms-2" @click="save">Save</button></div>
      </div>
    </div>
  `,
  data() { return { application: {} }; },
  async mounted() { const id = this.$route.params.id; const response = await fetch(`/api/company/applications/${id}`); this.application = await response.json(); },
  methods: {
    async save() { await fetch(`/api/company/applications/${this.application.id}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status: this.application.status, remarks: this.application.remarks }) }); this.$router.push('/company/dashboard'); },
    goBack() { this.$router.push('/company/dashboard'); }
  }
};

const StudentDashboardPage = {
  template: `
    <div class="container py-4">
      <div class="d-flex justify-content-between align-items-center mb-4"><h3>Student Dashboard</h3><button class="btn btn-danger btn-sm" @click="logout">Logout</button></div>
      <div class="alert alert-info">Welcome, {{ profile.display_name || 'Student' }}</div>
      <div class="mb-3"><button class="btn btn-outline-secondary me-2" @click="showProfile = true">Edit Profile</button><button class="btn btn-outline-primary me-2" @click="goHistory">History</button><button class="btn btn-success" @click="exportHistory">Export CSV</button></div>
      <div class="card mb-4"><div class="card-body"><h5>Organisation</h5><table class="table table-bordered"><thead><tr><th>Company Name</th><th>Action</th></tr></thead><tbody><tr v-for="company in companies" :key="company.id"><td>{{ company.company_name }}</td><td><button class="btn btn-sm btn-outline-info" @click="viewCompany(company.id)">View Details</button></td></tr></tbody></table></div></div>
      <div class="card mb-4"><div class="card-body"><h5>Current Drives</h5><ul class="list-group"><li v-for="drive in drives" :key="drive.id" class="list-group-item d-flex justify-content-between align-items-center"><span>{{ drive.drive_name }} — {{ drive.company_name }}</span><button class="btn btn-sm btn-outline-info" @click="viewDrive(drive.id)">View Details</button></li><li v-if="drives.length === 0" class="list-group-item text-muted">No current drives available.</li></ul></div></div>
      <div v-if="showProfile" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.2)"><div class="modal-dialog"><div class="modal-content"><div class="modal-body"><h5>Edit Profile</h5><div class="mb-3"><label class="form-label">Student Name</label><input v-model="profile.display_name" class="form-control" /></div><div class="mb-3"><label class="form-label">Department</label><input v-model="profile.department" class="form-control" /></div><div class="text-end"><button class="btn btn-secondary me-2" @click="showProfile = false">Close</button><button class="btn btn-primary" @click="saveProfile">Save</button></div></div></div></div></div>
      <div v-if="message" class="alert alert-success mt-3">{{ message }}</div>
    </div>
  `,
  data() { return { profile: {}, companies: [], drives: [], showProfile: false, message: '' }; },
  async mounted() { await this.load(); },
  methods: {
    async load() { const response = await fetch('/api/dashboard'); const data = await response.json(); this.profile = data.profile || {}; this.companies = data.companies || []; this.drives = data.drives || []; },
    async saveProfile() { await fetch('/api/student/profile', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(this.profile) }); this.showProfile = false; await this.load(); },
    async exportHistory() { const response = await fetch('/api/student/export'); const data = await response.json(); this.message = data.message || 'Export started'; },
    viewCompany(id) { this.$router.push(`/student/company/${id}`); },
    viewDrive(id) { this.$router.push(`/student/drive/${id}`); },
    goHistory() { this.$router.push('/student/history'); },
    async logout() { await fetch('/api/logout', { method: 'POST' }); this.$router.push('/login'); }
  }
};

const StudentCompanyPage = {
  template: `
    <div class="container py-4">
      <h3>{{ company.company_name }}</h3>
      <div class="alert alert-secondary">Overview: {{ company.overview || 'No overview yet.' }}</div>
      <h5>Current Drives</h5>
      <ul><li v-for="drive in company.drives" :key="drive.id">{{ drive.drive_name }}<button class="btn btn-sm btn-outline-primary ms-2" @click="viewDrive(drive.id)">View Details</button></li></ul>
      <button class="btn btn-secondary" @click="goBack">Back</button>
    </div>
  `,
  data() { return { company: {} }; },
  async mounted() { const id = this.$route.params.id; const response = await fetch(`/api/student/company/${id}/drives`); this.company = await response.json(); },
  methods: { viewDrive(id) { this.$router.push(`/student/drive/${id}`); }, goBack() { this.$router.push('/student/dashboard'); } }
};

const StudentDrivePage = {
  template: `
    <div class="container py-4">
      <h3>{{ drive.drive_name }}</h3>
      <p><strong>Job Title:</strong> {{ drive.job_title }}</p>
      <p><strong>Job Description:</strong> {{ drive.job_description }}</p>
      <p><strong>Salary:</strong> {{ drive.salary }}</p>
      <p><strong>Location:</strong> {{ drive.location }}</p>
      <div class="mt-3"><button class="btn btn-primary" @click="apply">Apply</button><button class="btn btn-secondary ms-2" @click="goBack">Back</button></div>
      <div v-if="message" class="alert alert-info mt-3">{{ message }}</div>
    </div>
  `,
  data() { return { drive: {}, message: '' }; },
  async mounted() { const id = this.$route.params.id; const response = await fetch(`/api/student/drives/${id}`); this.drive = await response.json(); },
  methods: {
    async apply() { const response = await fetch(`/api/student/apply/${this.drive.id}`, { method: 'POST' }); const data = await response.json(); this.message = data.message || 'Applied'; if (data.success) { setTimeout(() => this.$router.push('/student/dashboard'), 700); } },
    goBack() { this.$router.push('/student/dashboard'); }
  }
};

const StudentHistoryPage = {
  template: `
    <div class="container py-4">
      <h3>Student Application History</h3>
      <p><strong>Student Name:</strong> {{ profile.display_name }}</p>
      <p><strong>Department:</strong> {{ profile.department }}</p>
      <table class="table table-bordered"><thead><tr><th>Drive No.</th><th>Job Title</th><th>Company</th><th>Results</th><th>Remarks</th></tr></thead><tbody><tr v-for="item in history" :key="item.id"><td>{{ item.id }}</td><td>{{ item.job_title }}</td><td>{{ item.company_name }}</td><td>{{ item.result }}</td><td>{{ item.remarks }}</td></tr></tbody></table>
      <button class="btn btn-secondary" @click="goBack">Back</button>
    </div>
  `,
  data() { return { profile: {}, history: [] }; },
  async mounted() { const response = await fetch('/api/student/history'); const data = await response.json(); this.profile = data; this.history = data.history || []; },
  methods: { goBack() { this.$router.push('/student/dashboard'); } }
};

const AdminDashboardPage = {
  template: `
    <div class="container py-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h3>Admin Dashboard</h3>
        <button class="btn btn-danger btn-sm" @click="logout">Logout</button>
      </div>
      <div class="alert alert-info d-flex justify-content-between align-items-center">
        <span>Welcome, {{ adminName }}</span>
        <div class="d-flex gap-2 w-50">
          <input v-model="searchText" class="form-control" placeholder="Search company, student, or drive" />
          <button class="btn btn-outline-primary" @click="search">Search</button>
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
            <thead><tr><th>Drive No.</th><th>Drive Name</th><th>Action</th></tr></thead>
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
            <thead><tr><th>Sr. No</th><th>Name</th><th>Drive Name</th><th>Company Name</th><th>Date</th><th>Action</th></tr></thead>
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
              <div class="text-end"><button class="btn btn-secondary" @click="showDriveModal = false">Back</button></div>
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
              <div class="text-end"><button class="btn btn-secondary" @click="showApplicationModal = false">Back</button></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
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
      selectedApplication: {}
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
      const results = data.results || [];
      const companyResults = results.filter(item => item.type === 'company');
      const studentResults = results.filter(item => item.type === 'student');
      const driveResults = results.filter(item => item.type === 'drive');
      this.approvedCompanies = companyResults;
      this.students = studentResults;
      this.drives = driveResults;
      this.pendingCompanies = [];
      this.applications = [];
      if (!this.searchText.trim()) {
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

const LoginForm = {
  template: `
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-5">
          <div class="card shadow-sm">
            <div class="card-body p-4">
              <h2 class="text-center mb-4">Login Form</h2>
              <form @submit.prevent="submitLogin" novalidate>
                <div class="mb-3">
                  <label class="form-label">Username</label>
                  <input v-model="username" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Password</label>
                  <input v-model="password" type="password" class="form-control" required />
                </div>
                <div v-if="errorMessage" class="alert alert-danger py-2">{{ errorMessage }}</div>
                <button class="btn btn-primary w-100" type="submit">Login</button>
              </form>
              <p class="mt-3 text-center">
                <a href="#/register">Do not have an account? Register</a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  data() {
    return { username: '', password: '', errorMessage: '' };
  },
  methods: {
    async submitLogin() {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: this.username, password: this.password }),
      });
      const data = await response.json();
      if (data.success) {
        if (data.role === 'admin') {
          this.$router.push('/admin/dashboard');
        } else if (data.role === 'company') {
          this.$router.push('/company/dashboard');
        } else {
          this.$router.push('/student/dashboard');
        }
      } else {
        this.errorMessage = data.message || 'Login failed';
      }
    }
  }
};

const RegisterForm = {
  template: `
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card shadow-sm">
            <div class="card-body p-4">
              <h2 class="text-center mb-4">Register Form</h2>
              <form @submit.prevent="submitRegister" novalidate>
                <div class="mb-3">
                  <label class="form-label">Username</label>
                  <input v-model="username" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Password</label>
                  <input v-model="password" type="password" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Confirm Password</label>
                  <input v-model="confirmPassword" type="password" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">User Type</label>
                  <select v-model="userType" class="form-select" required>
                    <option value="Student">Student</option>
                    <option value="Company">Company</option>
                  </select>
                </div>
                <div v-if="userType === 'Student'" class="mb-3">
                  <label class="form-label">Student Name</label>
                  <input v-model="displayName" class="form-control" />
                </div>
                <div v-if="userType === 'Company'" class="mb-3">
                  <label class="form-label">Company Name</label>
                  <input v-model="displayName" class="form-control" />
                </div>
                <div class="mb-3">
                  <label class="form-label">Email</label>
                  <input v-model="email" type="email" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Department</label>
                  <input v-model="department" class="form-control" />
                </div>
                <div v-if="errorMessage" class="alert alert-danger py-2">{{ errorMessage }}</div>
                <button class="btn btn-success w-100" type="submit">Register</button>
              </form>
              <p class="mt-3 text-center">
                <a href="#/login">Already have an account? Login</a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  data() {
    return { username: '', password: '', confirmPassword: '', userType: 'Student', displayName: '', department: '', email: '', errorMessage: '' };
  },
  methods: {
    async submitRegister() {
      const payload = {
        username: this.username,
        password: this.password,
        confirm_password: this.confirmPassword,
        user_type: this.userType,
        display_name: this.displayName,
        department: this.department,
        email: this.email,
      };
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (data.success) {
        alert('Registration successful. Please login.');
        this.$router.push('/login');
      } else {
        this.errorMessage = data.message || 'Registration failed';
      }
    }
  }
};

const DashboardPage = {
  template: `
    <div class="container py-5">
      <h2 class="mb-4">Placement Portal Dashboard</h2>
      <div v-if="loading" class="text-muted">Loading...</div>
      <div v-else>
        <div class="alert alert-info">Welcome, {{ user.username }}. Role: {{ user.role }}</div>
        <pre class="bg-light p-3 rounded">{{ JSON.stringify(data, null, 2) }}</pre>
      </div>
    </div>
  `,
  data() {
    return { loading: true, user: {}, data: {} };
  },
  async mounted() {
    const me = await fetch('/api/me');
    this.user = await me.json();
    const response = await fetch('/api/dashboard');
    this.data = await response.json();
    this.loading = false;
  }
};

const AdminPage = {
  template: `
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
  `,
  data() {
    return { pendingDrives: [] };
  },
  async mounted() {
    const response = await fetch('/api/dashboard');
    const data = await response.json();
    this.pendingDrives = data.pending_drives || [];
  }
};

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginForm },
  { path: '/register', component: RegisterForm },
  { path: '/dashboard', component: DashboardPage },
  { path: '/admin', redirect: '/admin/dashboard' },
  { path: '/company/dashboard', component: CompanyDashboardPage },
  { path: '/company/create-drive', component: CreateDrivePage },
  { path: '/company/edit-drive/:id', component: CreateDrivePage },
  { path: '/company/applications/:id', component: DriveApplicationsPage },
  { path: '/company/application/:id', component: ReviewApplicationPage },
  { path: '/student/dashboard', component: StudentDashboardPage },
  { path: '/student/company/:id', component: StudentCompanyPage },
  { path: '/student/drive/:id', component: StudentDrivePage },
  { path: '/student/history', component: StudentHistoryPage },
  { path: '/admin/dashboard', component: AdminDashboardPage },
];

const router = VueRouter.createRouter({
  history: VueRouter.createWebHashHistory(),
  routes,
});

const app = Vue.createApp({
  template: '<router-view />',
});
app.use(router);
app.mount('#app');
