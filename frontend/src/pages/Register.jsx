import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { registerUser } from '../services/authService';

function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    college: '',
    batch: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await registerUser(form.name, form.email, form.password, form.college, form.batch);
      navigate('/', { replace: true });
    } catch (err) {
      setError(
        err.response?.data?.detail || err.response?.data?.message || 'Registration failed. Please try again.',
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-copy">
          <p className="eyebrow">Create account</p>
          <h1>Set up your AlgoCoach workspace.</h1>
          <p className="auth-text">
            Register once, keep your learning context organized, and start preparing with a cleaner flow.
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="field">
            <span>Full name</span>
            <input name="name" placeholder="Your full name" value={form.name} onChange={handleChange} required />
          </label>

          <label className="field">
            <span>Email</span>
            <input
              name="email"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={handleChange}
              required
            />
          </label>

          <label className="field">
            <span>Password</span>
            <input
              name="password"
              type="password"
              placeholder="Create a password"
              value={form.password}
              onChange={handleChange}
              required
            />
          </label>

          <label className="field">
            <span>College</span>
            <input
              name="college"
              placeholder="Your college name"
              value={form.college}
              onChange={handleChange}
            />
          </label>

          <label className="field">
            <span>Batch</span>
            <input name="batch" placeholder="e.g. 2026" value={form.batch} onChange={handleChange} />
          </label>

          {error ? <p className="form-error">{error}</p> : null}

          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </section>
    </main>
  );
}

export default Register;
