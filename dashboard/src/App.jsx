import { useState, useEffect } from "react";
import axios from "axios";
import AirQualityCard from "./components/AirQualityCard";
import NoiseCard from "./components/NoiseCard";
import QueueCard from "./components/QueueCard";
import AlertsBanner from "./components/AlertsBanner";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [sensorData, setSensorData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchData = async () => {
    try {
      const [sensorRes, alertsRes] = await Promise.all([
        axios.get(`${API_URL}/sensors/latest`),
        axios.get(`${API_URL}/alerts`)
      ]);
      setSensorData(sensorRes.data);
      setAlerts(alertsRes.data.alerts);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      console.error("Failed to fetch data:", err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app">
      <header className="header">
        <h1>Smart Stadium Dashboard</h1>
        {lastUpdated && <span className="last-updated">Last updated: {lastUpdated}</span>}
      </header>

      <AlertsBanner alerts={alerts} />

      <div className="grid">
        {sensorData ? (
          <>
            <AirQualityCard data={sensorData.air_quality} />
            <NoiseCard data={sensorData.noise_level} />
            <QueueCard data={sensorData.queue_wait} />
          </>
        ) : (
          <p className="loading">Loading sensor data...</p>
        )}
      </div>
    </div>
  );
}

export default App;