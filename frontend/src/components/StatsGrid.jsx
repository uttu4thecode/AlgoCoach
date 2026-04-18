function StatsGrid({ stats = [] }) {
  return (
    <section className="stats-grid">
      {stats.map((stat, index) => (
        <article
          key={stat.label}
          className="surface-card stat-card"
          style={{ animationDelay: `${index * 90}ms` }}
        >
          <span className="stat-card__label">{stat.label}</span>
          <strong className="stat-card__value">{stat.value}</strong>
          <span className="stat-card__change">{stat.change}</span>
        </article>
      ))}
    </section>
  );
}

export default StatsGrid;
