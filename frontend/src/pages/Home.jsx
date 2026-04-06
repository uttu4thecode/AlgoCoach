import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { getCurrentUser, logoutUser } from '../services/authService';

const highlights = [
  {
    title: 'Practice with structure',
    description: 'Track your prep with guided problem solving, focused sessions, and a cleaner feedback loop.',
  },
  {
    title: 'Stay interview ready',
    description: 'Keep your notes, role context, and coding momentum in one place while you prepare.',
  },
  {
    title: 'Build consistency',
    description: 'Use a steady routine instead of last-minute cramming before placements or interviews.',
  },
];

function Home() {
  const navigate = useNavigate();
  const user = getCurrentUser();

  const handleLogout = () => {
    logoutUser();
    navigate('/login', { replace: true });
  };

  return (
    <div className="app-shell">
      <Navbar user={user} onLogout={handleLogout} />
      <main className="page page-home">
        <section className="hero-card">
          <div className="hero-copy">
            <p className="eyebrow">AlgoCoach</p>
            <h1>Interview prep that feels calm, focused, and repeatable.</h1>
            <p className="hero-text">
              Welcome back{user?.name ? `, ${user.name}` : ''}. Your workspace is ready for practice,
              revision, and sharper problem solving.
            </p>
            <div className="hero-meta">
              <span className="pill">Logged in</span>
              <span className="pill">Role: {user?.role || 'Learner'}</span>
            </div>
          </div>
        </section>

        <section className="grid-section">
          {highlights.map((item) => (
            <article key={item.title} className="info-card">
              <h2>{item.title}</h2>
              <p>{item.description}</p>
            </article>
          ))}
        </section>
      </main>
    </div>
  );
}

export default Home;
