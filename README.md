# Vulnerability Scanner Dashboard

A comprehensive security scanning application with support for Nmap, Nikto, and Nuclei vulnerability scanners.

## Features

- **Nmap Scanner**: Network mapping and port scanning
- **Nikto Scanner**: Web server vulnerability scanning
- **Nuclei Scanner**: Fast vulnerability scanner with templates
- **Scan History**: View and manage all previous scans with results stored in Supabase
- **Real-time Results**: View scan output in real-time
- **Docker Support**: Easy deployment with Docker Compose

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Supabase account (database credentials in .env file)

## Quick Start

1. **Clone and setup**:
   ```bash
   # Ensure .env file has Supabase credentials
   cat .env
   ```

2. **Start with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Architecture

- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **Security Tools**: Nmap, Nikto, Nuclei (installed in backend container)

## API Endpoints

- `POST /scan/nmap` - Run Nmap scan
- `POST /scan/nikto` - Run Nikto scan
- `POST /scan/nuclei` - Run Nuclei scan
- `GET /scans` - Get all scan history
- `GET /scans/{scan_id}` - Get specific scan details
- `GET /health` - Health check

## Usage

1. Select a scanner tool from the dashboard
2. Enter target IP address or domain
3. Add optional scan parameters
4. Click "Start Scan"
5. View results in real-time
6. Access scan history at the bottom of the dashboard

## Security Note

This tool is designed for authorized security testing only. Always ensure you have permission to scan target systems.

## Development

**Frontend development**:
```bash
npm install
npm run dev
```

**Backend development**:
```bash
cd backend
pip install -r requirements.txt
python main.py
```

## Environment Variables

Required in `.env`:
- `VITE_SUPABASE_URL` - Your Supabase project URL
- `VITE_SUPABASE_ANON_KEY` - Your Supabase anonymous key
