function AlertsBanner({ alerts }) {
  if (!alerts || alerts.length === 0) return null;

  const colours = {
    warning: "#f59e0b",
    info: "#3b82f6",
    success: "#10b981",
    danger: "#ef4444"
  };

  return (
    <div className="alerts-banner">
      {alerts.map((alert, i) => (
        <div
          key={i}
          className="alert-item"
          style={{ borderLeft: `4px solid ${colours[alert.severity]}` }}
        >
          <span className="alert-message">{alert.message}</span>
        </div>
      ))}
    </div>
  );
}

export default AlertsBanner;