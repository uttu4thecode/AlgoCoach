function DailyPlan({ items = [] }) {
  return (
    <section className="surface-card dashboard-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Today</p>
          <h2>Structured session plan</h2>
        </div>
      </div>

      <div className="timeline-list">
        {items.map((item) => (
          <article key={`${item.time}-${item.title}`} className="timeline-card">
            <span className="timeline-card__time">{item.time}</span>
            <div>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default DailyPlan;
