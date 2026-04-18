function RoadmapPanel({ steps = [] }) {
  return (
    <section className="surface-card dashboard-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Roadmap</p>
          <h2>How frontend and backend connect</h2>
        </div>
      </div>

      <div className="roadmap-list">
        {steps.map((step) => (
          <article key={step.phase} className="roadmap-step">
            <span className="roadmap-step__phase">{step.phase}</span>
            <h3>{step.title}</h3>
            <p>{step.description}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

export default RoadmapPanel;
