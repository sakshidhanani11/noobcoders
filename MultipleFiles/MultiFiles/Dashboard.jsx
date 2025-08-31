import React, { useEffect, useState, useRef } from "react";
import { getAlerts } from "../services/api";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import L from "leaflet"; // Import Leaflet

// Ensure Leaflet's CSS is loaded (you might already have it in index.html)
import "leaflet/dist/leaflet.css";

// Fix for default marker icon issue with Webpack/Parcel
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});


export default function Dashboard() {
  const [alerts, setAlerts] = useState([]);
  const [series, setSeries] = useState([]);
  const wsRef = useRef(null);
  const mapRef = useRef(null); // Ref for the map container
  const leafletMapRef = useRef(null); // Ref for the Leaflet map instance

  useEffect(() => {
    fetchAlerts();

    // Initialize map
    if (!leafletMapRef.current) { // Only initialize once
      leafletMapRef.current = L.map(mapRef.current).setView([29.76, -95.37], 10); // Houston area
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '© OpenStreetMap contributors'
      }).addTo(leafletMapRef.current);

      // Add a sample coastal area overlay
      L.polygon([
        [29.85, -95.50], [29.70, -95.20], [29.50, -95.10], [29.40, -95.30], [29.60, -95.60]
      ], {
        color: '#0077B6',
        fillColor: '#00B4D8',
        fillOpacity: 0.2,
        weight: 2
      }).addTo(leafletMapRef.current).bindPopup('Protected Coastal Zone');

      // Add sample sensor markers (you'd get these from your backend)
      const sensors = [
        { id: 1, name: "Tide Gauge Alpha", lat: 29.75, lon: -95.35, status: "online" },
        { id: 2, name: "Weather Station Bravo", lat: 29.80, lon: -95.40, status: "online" },
        { id: 3, name: "Water Quality Sensor Charlie", lat: 29.70, lon: -95.30, status: "online" },
        { id: 4, name: "Tide Gauge Delta", lat: 29.65, lon: -95.45, status: "offline" },
        { id: 5, name: "Surveillance Camera Echo", lat: 29.78, lon: -95.25, status: "online" }
      ];

      sensors.forEach(sensor => {
        const marker = L.marker([sensor.lat, sensor.lon]).addTo(leafletMapRef.current);
        const statusIcon = sensor.status === "online" ? "🟢" : "🔴";
        marker.bindPopup(`
          <b>${sensor.name}</b><br>
          Status: ${statusIcon} ${sensor.status.toUpperCase()}<br>
          Location: ${sensor.lat.toFixed(4)}, ${sensor.lon.toFixed(4)}
        `);
      });
    }


    // Open websocket to backend or a websocket relay
    // VITE_WS_URL should point to your websocket service, e.g., ws://localhost:8001 or ws://<docker_service_name>:8001
    const wsUrl = (import.meta.env.VITE_WS_URL) || "ws://localhost:8001";
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    ws.onopen = () => console.log("WebSocket connected");
    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.type === "alert") {
          setAlerts(prev => [msg.payload, ...prev]);
          // Optionally, add alert markers to the map
          if (leafletMapRef.current && msg.payload.payload && msg.payload.payload.latitude && msg.payload.payload.longitude) {
            L.marker([msg.payload.payload.latitude, msg.payload.payload.longitude])
              .addTo(leafletMapRef.current)
              .bindPopup(`<b>${msg.payload.severity} Alert:</b> ${msg.payload.message}`)
              .openPopup();
          }
        } else if (msg.type === "reading") {
          // Assuming 'sea_level' is always present in reading.values
          if (msg.payload.values && typeof msg.payload.values.sea_level !== 'undefined') {
            setSeries(prev => [...prev, { t: new Date().toLocaleTimeString(), value: msg.payload.values.sea_level }].slice(-50));
          }
        }
      } catch (err) { console.error("WebSocket message error:", err); }
    };
    ws.onclose = () => console.log("WebSocket disconnected");
    ws.onerror = (err) => console.error("WebSocket error:", err);

    return () => {
      ws.close();
      if (leafletMapRef.current) {
        leafletMapRef.current.remove(); // Clean up map on unmount
        leafletMapRef.current = null;
      }
    };
  }, []); // Empty dependency array means this runs once on mount

  async function fetchAlerts() {
    try {
      const res = await getAlerts();
      setAlerts(res.data);
    } catch (error) {
      console.error("Error fetching alerts:", error);
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Coastal Threat Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Map Section */}
        <div className="bg-white rounded-lg shadow p-4 col-span-full lg:col-span-2">
          <h2 className="font-semibold mb-2">Coastal Monitoring Map</h2>
          <div ref={mapRef} style={{ height: "400px", width: "100%" }} className="rounded-lg overflow-hidden"></div>
        </div>

        {/* Sea Level Chart */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="font-semibold mb-2">Sea Level (recent)</h2>
          <LineChart width={400} height={250} data={series} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="t" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#8884d8" />
          </LineChart>
        </div>

        {/* Alerts List */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="font-semibold mb-2">Active Alerts</h2>
          <ul className="max-h-96 overflow-y-auto">
            {alerts.slice(0,10).map(a => (
              <li key={a.id} className="border p-2 mb-2 rounded-md">
                <div className="flex justify-between items-start">
                  <div>
                    <strong className={a.severity === 'high' ? 'text-red-600' : a.severity === 'medium' ? 'text-yellow-600' : 'text-green-600'}>
                      {a.severity.toUpperCase()}
                    </strong> — {a.message}
                  </div>
                  <div className="text-sm text-gray-500 ml-4">{new Date(a.created_at).toLocaleString()}</div>
                </div>
                {a.payload && (
                  <pre className="text-xs mt-2 bg-gray-50 p-2 rounded-sm overflow-x-auto">
                    {JSON.stringify(a.payload, null, 2)}
                  </pre>
                )}
              </li>
            ))}
            {alerts.length === 0 && <li className="text-gray-500">No active alerts.</li>}
          </ul>
        </div>
      </div>
    </div>
  );
}