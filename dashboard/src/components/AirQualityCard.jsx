import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { useState, useEffect } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

const aqiColours = {
  good: "#10b981",
  moderate: "#f59e0b",
  poor: "#f97316",
  hazardous: "#ef4444"
};

function AirQualityCard({ data }) {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await axios.get(`${API_URL}/sensors/air_quality`);
        const formatted = res.data.map(item => ({
          time: item.timestamp.slice(11, 19),
          co2: item.data.avg_co2_ppm,
          pm25: item.data.avg_pm2_5
        }));
        setHistory(formatted);
      } catch (err) {
        console.error(err);
      }
    };
    fetchHistory();
  }, [data]);

  if (!data) return <div className="card">Loading air quality...</div>;

  const aqi = data.data?.latest_aqi || "unknown";
  const colour = aqiColours[aqi] || "#888";

  return (
    <div className="card">
      <div className="card-header">
        <h2>Air Quality</h2>
        <span className="badge" style={{ background: colour }}>
          {aqi.toUpperCase()}
        </span>
      </div>
      <div className="metrics">
        <div className="metric">
          <span className="metric-value">{data.data?.avg_co2_ppm?.toFixed(1)}</span>
          <span className="metric-label">CO2 (ppm)</span>
        </div>
        <div className="metric">
          <span className="metric-value">{data.data?.avg_pm2_5?.toFixed(1)}</span>
          <span className="metric-label">PM2.5</span>
        </div>
      </div>
      {history.length > 0 && (
        <ResponsiveContainer width="100%" height={120}>
          <LineChart data={history}>
            <XAxis dataKey="time" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip />
            <Line type="monotone" dataKey="co2" stroke="#6366f1" dot={false} name="CO2" />
            <Line type="monotone" dataKey="pm25" stroke="#f97316" dot={false} name="PM2.5" />
          </LineChart>
        </ResponsiveContainer>
      )}
      {data.data?.alert && (
        <p className="alert-text">Air quality alert active</p>
      )}
    </div>
  );
}

export default AirQualityCard;