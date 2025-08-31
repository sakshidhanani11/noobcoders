# Coastal Threat Alert System

A comprehensive early warning and alerting platform for coastal areas that collects data from physical sensors, satellite feeds, and historical records. Using AI/ML, it analyzes trends and detects anomalies indicating threats like storm surges, coastal erosion, pollution, and illegal activities.

## Features

- Real-time sensor data ingestion
- AI/ML threat prediction using TensorFlow
- WebSocket-based real-time updates
- Interactive dashboard with maps and charts
- SMS alerts via Twilio integration
- Docker containerization

## Quick Start

1. **Install Docker Desktop** from https://www.docker.com/products/docker-desktop

2. **Clone or download this project** to your local machine

3. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Add your Twilio credentials:
     ```
     TWILIO_SID=your_twilio_account_sid
     TWILIO_TOKEN=your_twilio_auth_token
     TWILIO_FROM=+1234567890
     SMS_RECIPIENT=+19876543210
     ```

4. **Build and run the application**:
   ```bash
   docker-compose up --build