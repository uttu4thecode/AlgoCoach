import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ActivityFeed from '../components/ActivityFeed';
import DailyPlan from '../components/DailyPlan';
import DashboardHero from '../components/DashboardHero';
import Navbar from '../components/Navbar';
import PracticeWorkspace from '../components/PracticeWorkspace';
import RoadmapPanel from '../components/RoadmapPanel';
import StatsGrid from '../components/StatsGrid';
import { fetchCurrentUser, getCurrentUser, logoutUser } from '../services/authService';
import { fetchDashboardOverview, fetchPracticeProblems } from '../services/dashboardService';

function Home() {
  const navigate = useNavigate();
  const [user, setUser] = useState(() => getCurrentUser());
  const [overview, setOverview] = useState(null);
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let isMounted = true;

    const loadDashboard = async () => {
      setLoading(true);
      setError('');

      try {
        const [freshUser, dashboardOverview, practiceProblems] = await Promise.all([
          fetchCurrentUser(),
          fetchDashboardOverview(),
          fetchPracticeProblems(),
        ]);

        if (!isMounted) {
          return;
        }

        setUser((currentUser) => ({
          ...currentUser,
          ...freshUser,
        }));
        setOverview(dashboardOverview);
        setProblems(practiceProblems);
      } catch (err) {
        if (!isMounted) {
          return;
        }

        const message =
          err.response?.data?.detail ||
          err.response?.data?.message ||
          'We could not load your dashboard right now.';

        setError(message);

        if (err.response?.status === 401) {
          logoutUser();
          navigate('/login', { replace: true });
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadDashboard();

    return () => {
      isMounted = false;
    };
  }, [navigate]);

  const handleLogout = () => {
    logoutUser();
    navigate('/login', { replace: true });
  };

  return (
    <div className="app-shell dashboard-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />
      <Navbar user={user} onLogout={handleLogout} />

      <main className="page page-dashboard">
        <DashboardHero user={user} overview={overview} />

        {loading ? (
          <section className="surface-card dashboard-section status-panel">
            <p className="eyebrow">Loading</p>
            <h2>Preparing your dashboard and coding workspace...</h2>
          </section>
        ) : null}

        {error ? (
          <section className="surface-card dashboard-section status-panel status-panel--error">
            <p className="eyebrow">Connection issue</p>
            <h2>{error}</h2>
            <p>Make sure the FastAPI server is running on `http://localhost:8000` or update `VITE_PYTHON_API_URL`.</p>
          </section>
        ) : null}

        {!loading && !error ? (
          <>
            <StatsGrid stats={overview?.stats} />
            <PracticeWorkspace problems={problems} />
            <section className="dashboard-columns">
              <DailyPlan items={overview?.daily_plan} />
              <ActivityFeed items={overview?.recent_activity} />
            </section>
            <RoadmapPanel steps={overview?.roadmap} />
          </>
        ) : null}
      </main>
    </div>
  );
}

export default Home;
