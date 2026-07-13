<template>
  <div class="container py-4">
    <h3>Create a Drive</h3>
    <div class="card p-4">
      <form @submit.prevent="saveDrive">
        <div class="mb-3">
          <label class="form-label">Drive Name</label>
          <input v-model="drive.drive_name" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Job Title</label>
          <input v-model="drive.job_title" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Job Description</label>
          <textarea v-model="drive.job_description" class="form-control" rows="4" required></textarea>
        </div>
        <div class="mb-3">
          <label class="form-label">Eligibility Criteria</label>
          <textarea v-model="drive.eligibility" class="form-control" rows="3" required></textarea>
        </div>
        <div class="mb-3">
          <label class="form-label">Application Deadline</label>
          <input v-model="drive.application_deadline" type="date" class="form-control" required />
        </div>
        <button class="btn btn-primary" type="submit">Save</button>
        <button class="btn btn-secondary ms-2" type="button" @click="goBack">Back</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CreateDrivePage',
  data() {
    return {
      drive: {
        drive_name: '',
        job_title: '',
        job_description: '',
        eligibility: '',
        application_deadline: '',
      },
      editId: null,
    };
  },
  async mounted() {
    const id = this.$route.params.id;
    if (id) {
      this.editId = Number(id);
      const response = await fetch(`/api/company/drives/${id}`);
      const data = await response.json();
      this.drive = data;
    }
  },
  methods: {
    async saveDrive() {
      const url = this.editId ? `/api/company/drives/${this.editId}` : '/api/company/drives';
      const method = this.editId ? 'PUT' : 'POST';
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.drive),
      });
      const data = await response.json();
      if (data.success) {
        this.$router.push('/company/dashboard');
      }
    },
    goBack() {
      this.$router.push('/company/dashboard');
    }
  }
};
</script>
