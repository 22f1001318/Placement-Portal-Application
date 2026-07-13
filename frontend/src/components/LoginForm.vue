<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card shadow-sm">
          <div class="card-body p-4">
            <h2 class="text-center mb-4">Login Form</h2>
            <form @submit.prevent="submitLogin">
              <div class="mb-3">
                <label class="form-label">Username</label>
                <input v-model="username" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input v-model="password" type="password" class="form-control" required />
              </div>
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
</template>

<script>
export default {
  name: 'LoginForm',
  data() {
    return {
      username: '',
      password: '',
    };
  },
  methods: {
    async submitLogin() {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: this.username, password: this.password })
      });
      const data = await response.json();
      if (data.success) {
        this.$router.push(data.role === 'admin' ? '/admin' : '/dashboard');
      } else {
        alert(data.message || 'Login failed');
      }
    }
  }
};
</script>
