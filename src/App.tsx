import { Shield, Activity, Search, Zap } from 'lucide-react';
import Scanner from './components/Scanner';
import ScanHistory from './components/ScanHistory';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center">
            <Shield className="text-blue-600 mr-3" size={32} />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Vulnerability Scanner Dashboard
              </h1>
              <p className="text-gray-600 mt-1">
                Nmap, Nuclei, Nikto, SSLyze, and OWASP ZAP
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Scanner
            tool="nmap"
            icon={<Search size={24} />}
            title="Nmap Scanner"
            description="Network mapping and port scanning"
          />
          <Scanner
            tool="nikto"
            icon={<Activity size={24} />}
            title="Nikto Scanner"
            description="Web server vulnerability scanning"
          />
          <Scanner
            tool="nuclei"
            icon={<Zap size={24} />}
            title="Nuclei Scanner"
            description="Fast vulnerability scanner with templates"
          />
          <Scanner
            tool="sslyze"
            icon={<Shield size={24} />}
            title="SSLyze (TLS/SSL)"
            description="Analyze TLS/SSL configuration"
          />
          <Scanner
            tool="zap-baseline"
            icon={<Zap size={24} />}
            title="OWASP ZAP Baseline"
            description="Passive baseline scan for web apps"
          />
          <Scanner
            tool="zap-api"
            icon={<Zap size={24} />}
            title="OWASP ZAP API Scan"
            description="Scan OpenAPI/Swagger endpoints"
          />
          <Scanner
            tool="openvas-start"
            icon={<Shield size={24} />}
            title="OpenVAS (Start Service)"
            description="Launch OpenVAS container; open UI on :9392"
            requireTarget={false}
          />
        </div>

        <ScanHistory />
      </main>
    </div>
  );
}

export default App;
