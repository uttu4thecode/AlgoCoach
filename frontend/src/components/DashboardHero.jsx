function DashboardHero({ user, overview }) {
  return (
    <section className="dashboard-hero surface-card">
      <div className="dashboard-hero__content">
        <p className="eyebrow">Personal dashboard</p>
        <h1>{overview?.headline || `Welcome back${user?.name ? `, ${user.name}` : ''}`}</h1>
        <p className="hero-text">
          {overview?.subheadline ||
            'Keep your interview prep focused with one workspace for coding practice, review, and placement readiness.'}
        </p>
        <div className="hero-badges">
          <span className="pill">Role: {user?.role || 'Learner'}</span>
          <span className="pill">{user?.college || 'Interview prep mode'}</span>
          <span className="pill">{user?.batch ? `Batch ${user.batch}` : 'Daily momentum'}</span>
        </div>
      </div>

      <div className="dashboard-hero__panel">
        <p className="dashboard-hero__label">Current focus</p>
        <div className="hero-orbit">
          {(overview?.focus_areas || []).slice(0, 3).map((area) => (
            <article key={area.title} className="hero-orbit__card">
              <span>{area.level}</span>
              <strong>{area.title}</strong>
              <p>{area.detail}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

export default DashboardHero;
