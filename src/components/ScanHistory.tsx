import { useState, useEffect } from 'react';
import { Clock, Shield } from 'lucide-react';

interface Scan {
  id: string;
  tool: string;
  target: string;
  status: string;
  created_at: string;
  result: string;
}

export default function ScanHistory() {
  const [scans, setScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedScan, setSelectedScan] = useState<Scan | null>(null);

  useEffect(() => {
    fetchScans();
  }, []);

  const fetchScans = async () => {
    try {
      const response = await fetch('http://localhost:8000/scans');
      const data = await response.json();
      setScans(data.scans || []);
    } catch (error) {
      console.error('Error fetching scans:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center mb-4">
        <Clock className="mr-3 text-blue-600" size={24} />
        <h3 className="text-xl font-semibold text-gray-900">Scan History</h3>
      </div>

      {scans.length === 0 ? (
        <p className="text-gray-600 text-center py-8">No scans yet</p>
      ) : (
        <div className="space-y-2">
          {scans.map((scan) => (
            <div
              key={scan.id}
              className="border border-gray-200 rounded-md p-4 hover:bg-gray-50 cursor-pointer transition-colors"
              onClick={() => setSelectedScan(scan)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Shield className="mr-2 text-blue-600" size={20} />
                  <div>
                    <p className="font-medium text-gray-900">
                      {scan.tool.toUpperCase()} - {scan.target}
                    </p>
                    <p className="text-sm text-gray-600">
                      {new Date(scan.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    scan.status === 'completed'
                      ? 'bg-green-100 text-green-800'
                      : scan.status === 'failed'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {scan.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedScan && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-xl font-semibold text-gray-900">
                  {selectedScan.tool.toUpperCase()} Scan Results
                </h4>
                <button
                  onClick={() => setSelectedScan(null)}
                  className="text-gray-600 hover:text-gray-900"
                >
                  ✕
                </button>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                Target: {selectedScan.target} | {new Date(selectedScan.created_at).toLocaleString()}
              </p>
              <div className="bg-gray-900 text-green-400 p-4 rounded-md overflow-auto">
                <pre className="text-xs font-mono whitespace-pre-wrap break-words">
                  {selectedScan.result}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
