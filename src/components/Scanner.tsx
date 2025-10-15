import { useState } from 'react';
import { Shield, Activity, AlertTriangle, Search } from 'lucide-react';

interface ScanResult {
  tool: string;
  target: string;
  output: string;
  status: string;
}

interface ScannerProps {
  tool: string;
  icon: React.ReactNode;
  title: string;
  description: string;
}

export default function Scanner({ tool, icon, title, description }: ScannerProps) {
  const [target, setTarget] = useState('');
  const [options, setOptions] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);

  const handleScan = async () => {
    if (!target) {
      alert('Please enter a target');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`http://localhost:8000/scan/${tool}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ target, tool, options }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        tool,
        target,
        output: `Error: ${error}`,
        status: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center mb-4">
        <div className="mr-3 text-blue-600">{icon}</div>
        <div>
          <h3 className="text-xl font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600">{description}</p>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target (IP/Domain)
          </label>
          <input
            type="text"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="example.com or 192.168.1.1"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Options (optional)
          </label>
          <input
            type="text"
            value={options}
            onChange={(e) => setOptions(e.target.value)}
            placeholder="Additional scan options"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
        </div>

        <button
          onClick={handleScan}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200 flex items-center justify-center"
        >
          {loading ? (
            <>
              <Activity className="animate-spin mr-2" size={20} />
              Scanning...
            </>
          ) : (
            <>
              <Search className="mr-2" size={20} />
              Start Scan
            </>
          )}
        </button>

        {result && (
          <div className="mt-4">
            <div className="flex items-center mb-2">
              <span className="text-sm font-medium text-gray-700 mr-2">Status:</span>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  result.status === 'completed'
                    ? 'bg-green-100 text-green-800'
                    : result.status === 'failed' || result.status === 'error'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}
              >
                {result.status}
              </span>
            </div>
            <div className="bg-gray-900 text-green-400 p-4 rounded-md overflow-auto max-h-96">
              <pre className="text-xs font-mono whitespace-pre-wrap break-words">
                {result.output}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
