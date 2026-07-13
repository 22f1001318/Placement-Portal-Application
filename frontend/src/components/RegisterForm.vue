<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card shadow-sm">
          <div class="card-body p-4">
            <h2 class="text-center mb-4">Register Form</h2>
            <form @submit.prevent="submitRegister">
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
</template>

<script>
export default {
  name: 'RegisterForm',
  data() {
    return {
      username: '',
      password: '',
      confirmPassword: '',
      userType: 'Student',
    };
  },
  methods: {
    async submitRegister() {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: this.username,
          password: this.password,
          confirm_password: this.confirmPassword,
          user_type: this.userType,
        })
      });
      const data = await response.json();
      if (data.success) {
        alert('Registration successful. Please login.');
        this.$router.push('/login');
      } else {
        alert(data.message || 'Registration failed');
      }
    }
  }
};
</script>
