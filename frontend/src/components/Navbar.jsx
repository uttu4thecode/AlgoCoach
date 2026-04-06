function Navbar({ user, onLogout }) {
  return (
    <header className="navbar">
      <div>
        <p className="navbar-brand">AlgoCoach</p>
        <p className="navbar-subtitle">Smart coding interview preparation</p>
      </div>

      <div className="navbar-actions">
        <div className="user-chip">
          <span className="user-name">{user?.name || 'Guest'}</span>
          <span className="user-role">{user?.role || 'Learner'}</span>
        </div>
        <button className="secondary-button" type="button" onClick={onLogout}>
          Logout
        </button>
      </div>
    </header>
  );
}

export default Navbar;
