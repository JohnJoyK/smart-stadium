import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { useState, useEffect } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

function QueueCard({ data }) {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await axios.get(`${API_URL}/sensors/queue_wait`);
        const formatted = res.data.map(item => ({
          time: item.timestamp.slice(11, 19),
          avg: item.data.avg_wait_minutes,
          best: item.data.best_wait_minutes
        }));
        setHistory(formatted);
      } catch (err) {
        console.error(err);
      }
    };
    fetchHistory();
  }, [data]);

  if (!data) return <div className="card">Loading queue data...</div>;

  const recommendation = data.data?.recommendation;
  const recColour = recommendation === "go_now" ? "#10b981" : "#f59e0b";

  return (
    <div className="card">
      <div className="card-header">
        <h2>Kiosk Queues</h2>
        <span className="badge" style={{ background: recColour }}>
          {recommendation === "go_now" ? "GO NOW" : "WAIT"}
        </span>
      </div>
      <div className="metrics">
        <div className="metric">
          <span className="metric-value">{data.data?.avg_wait_minutes?.toFixed(1)}</span>
          <span className="metric-label">Avg wait (min)</span>
        </div>
        <div className="metric">
          <span className="metric-value">{data.data?.best_wait_minutes?.toFixed(1)}</span>
          <span className="metric-label">Best wait (min)</span>
        </div>
      </div>
      <p className="best-stand">Best stand: <strong>{data.data?.best_stand}</strong></p>
      {history.length > 0 && (
        <ResponsiveContainer width="100%" height={120}>
          <LineChart data={history}>
            <XAxis dataKey="time" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip />
            <Line type="monotone" dataKey="avg" stroke="#6366f1" dot={false} name="Avg wait" />
            <Line type="monotone" dataKey="best" stroke="#10b981" dot={false} name="Best wait" />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default QueueCard;