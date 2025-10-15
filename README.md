# Vulnerability Scanner

A security assessment and penetration testing toolkit with a modern web UI and Docker-based backend.

## Features

- **Multiple Security Tools**:
  - OpenVAS - Network vulnerability scanning
  - Nuclei - Fast template-based scanning
  - Nmap - Port scanning and network discovery
  - OWASP ZAP - Web application and API security testing
  - SSLyze - TLS/SSL configuration analysis

- **Real-time Scanning**: Live scan status updates with automatic polling
- **Dashboard**: View scan history, findings, and statistics
- **Docker-based Backend**: Isolated security tools running in containers

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for frontend development)

## Setup Instructions

### 1. Start the Backend

Navigate to the project root and start all services:

```bash
docker-compose up -d
```

This will start:
- Scanner API (port 3001)
- Nmap container
- Nuclei container
- OWASP ZAP (port 8080)
- SSLyze container

Check if all containers are running:

```bash
docker-compose ps
```

### 2. Install Backend Dependencies

If this is your first time running, install the backend dependencies:

```bash
cd backend
npm install
cd ..
```

### 3. Start the Frontend

In a new terminal, start the frontend development server:

```bash
npm install
npm run dev
```

The UI will be available at `http://localhost:5173`

## Usage

1. **Check Backend Status**: Look for the "Backend Connected" indicator in the top right
2. **Select a Tool**: Click on any security tool from the left panel
3. **Enter Target**: Provide a target URL or IP address
4. **Start Scan**: Click "Start Scan" to begin the security assessment
5. **View Results**: Monitor scan progress in the dashboard on the right

## Docker Container Names

The Docker containers are named with the pattern `scanner-api-[service]-1`:

- `scanner-api-scanner-api-1` - Main API server
- `scanner-api-nmap-1` - Nmap scanning
- `scanner-api-nuclei-1` - Nuclei scanning
- `scanner-api-owasp-zap-1` - OWASP ZAP proxy
- `scanner-api-sslyze-1` - SSLyze SSL/TLS testing

## API Endpoints

- `POST /api/scan` - Start a new scan
- `GET /api/scan/:scanId` - Get scan details
- `GET /api/scans` - List all scans
- `GET /health` - Check backend health

## Troubleshooting

### Backend Not Connected

1. Check if Docker containers are running:
   ```bash
   docker-compose ps
   ```

2. Check backend logs:
   ```bash
   docker-compose logs scanner-api
   ```

3. Restart the backend:
   ```bash
   docker-compose restart scanner-api
   ```

### Scans Failing

1. Verify the target is reachable
2. Check individual tool logs:
   ```bash
   docker-compose logs nmap
   docker-compose logs nuclei
   ```

3. Ensure proper network connectivity from containers

### Port Conflicts

If ports 3001 or 8080 are already in use, modify `docker-compose.yml`:

```yaml
ports:
  - "3002:3001"  # Change external port
```

## Security Notes

- These tools should only be used on systems you own or have permission to test
- Never scan targets without proper authorization
- Some scans may be detected by intrusion detection systems
- Use responsibly and ethically

## Stopping the Services

To stop all containers:

```bash
docker-compose down
```

To stop and remove all data:

```bash
docker-compose down -v
```
