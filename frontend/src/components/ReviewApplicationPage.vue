<template>
  <div class="container py-4">
    <h3>Student Application</h3>
    <div class="card p-4">
      <p><strong>Student Name:</strong> {{ application.student_name }}</p>
      <p><strong>Department:</strong> {{ application.department }}</p>
      <p><strong>Drive:</strong> {{ application.drive_name }}</p>
      <p><strong>Job Title:</strong> {{ application.job_title }}</p>
      <div class="mb-3">
        <label class="form-label">Status</label>
        <select v-model="application.status" class="form-select">
          <option value="shortlist">Shortlist</option>
          <option value="waiting">Waiting</option>
          <option value="reject">Reject</option>
        </select>
      </div>
      <div class="mb-3">
        <label class="form-label">Remarks</label>
        <textarea v-model="application.remarks" class="form-control" rows="3"></textarea>
      </div>
      <div class="mb-3">
        <button class="btn btn-outline-secondary" @click="goBack">Back</button>
        <button class="btn btn-primary ms-2" @click="save">Save</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ReviewApplicationPage',
  data() {
    return { application: {} };
  },
  async mounted() {
    const id = this.$route.params.id;
    const response = await fetch(`/api/company/applications/${id}`);
    this.application = await response.json();
  },
  methods: {
    async save() {
      await fetch(`/api/company/applications/${this.application.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: this.application.status, remarks: this.application.remarks }),
      });
      this.$router.push('/company/dashboard');
    },
    goBack() {
      this.$router.push('/company/dashboard');
    }
  }
};
</script>
