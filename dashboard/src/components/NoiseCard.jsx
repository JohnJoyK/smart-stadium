import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { useState, useEffect } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

const categoryColours = {
  quiet: "#10b981",
  normal: "#3b82f6",
  loud: "#f59e0b",
  very_loud: "#ef4444"
};

function NoiseCard({ data }) {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await axios.get(`${API_URL}/sensors/noise_level`);
        const formatted = res.data.map(item => ({
          time: item.timestamp.slice(11, 19),
          avg: item.data.avg_decibels,
          max: item.data.max_decibels
        }));
        setHistory(formatted);
      } catch (err) {
        console.error(err);
      }
    };
    fetchHistory();
  }, [data]);

  if (!data) return <div className="card">Loading noise data...</div>;

  const category = data.data?.category || "normal";
  const colour = categoryColours[category] || "#888";

  return (
    <div className="card">
      <div className="card-header">
        <h2>Noise Level</h2>
        <span className="badge" style={{ background: colour }}>
          {category.replace("_", " ").toUpperCase()}
        </span>
      </div>
      <div className="metrics">
        <div className="metric">
          <span className="metric-value">{data.data?.avg_decibels?.toFixed(1)}</span>
          <span className="metric-label">Avg dB</span>
        </div>
        <div className="metric">
          <span className="metric-value">{data.data?.max_decibels?.toFixed(1)}</span>
          <span className="metric-label">Max dB</span>
        </div>
      </div>
      {history.length > 0 && (
        <ResponsiveContainer width="100%" height={120}>
          <BarChart data={history}>
            <XAxis dataKey="time" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip />
            <Bar dataKey="avg" fill="#3b82f6" name="Avg dB" />
            <Bar dataKey="max" fill="#ef4444" name="Max dB" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default NoiseCard;