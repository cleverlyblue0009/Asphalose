/**
 * File Scanner page - Upload and scan files for threats.
 */
import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Upload, FileSearch, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

const FileScanner = () => {
  const [scanResults, setScanResults] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [resultsRes, statsRes] = await Promise.all([
        apiService.getScanResults({ limit: 20 }),
        apiService.getScanStats(),
      ]);

      setScanResults(resultsRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching scan data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file) return;

    setUploading(true);
    try {
      const result = await apiService.scanFile(file);
      alert(`Scan complete!\nResult: ${result.data.scan.scan_result}\nConfidence: ${(result.data.scan.confidence_score * 100).toFixed(1)}%`);
      fetchData(); // Refresh results
    } catch (error) {
      console.error('Error scanning file:', error);
      alert('Error scanning file: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const getResultIcon = (result) => {
    if (result === 'safe') return <CheckCircle className="w-6 h-6 text-green-500" />;
    if (result === 'suspicious') return <AlertTriangle className="w-6 h-6 text-yellow-500" />;
    return <XCircle className="w-6 h-6 text-red-500" />;
  };

  const getResultColor = (result) => {
    const colors = {
      safe: 'bg-green-100 text-green-800',
      suspicious: 'bg-yellow-100 text-yellow-800',
      malicious: 'bg-red-100 text-red-800',
    };
    return colors[result] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600">Total Scans</div>
          <div className="text-3xl font-bold text-gray-900 mt-2">{stats?.total_scans || 0}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600">Safe</div>
          <div className="text-3xl font-bold text-green-600 mt-2">{stats?.safe || 0}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600">Suspicious</div>
          <div className="text-3xl font-bold text-yellow-600 mt-2">{stats?.suspicious || 0}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600">Malicious</div>
          <div className="text-3xl font-bold text-red-600 mt-2">{stats?.malicious || 0}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600">Quarantined</div>
          <div className="text-3xl font-bold text-purple-600 mt-2">{stats?.quarantined || 0}</div>
        </div>
      </div>

      {/* Upload Area */}
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Scan a File</h2>
        <form
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className="space-y-4"
        >
          <div
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
              dragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <Upload className={`w-16 h-16 mx-auto mb-4 ${dragActive ? 'text-primary-500' : 'text-gray-400'}`} />
            <p className="text-lg font-medium text-gray-900 mb-2">
              {dragActive ? 'Drop file here' : 'Drag and drop a file here'}
            </p>
            <p className="text-sm text-gray-600 mb-4">or</p>
            <label className="cursor-pointer">
              <span className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors inline-block font-medium">
                {uploading ? 'Scanning...' : 'Choose File'}
              </span>
              <input
                type="file"
                className="hidden"
                onChange={handleChange}
                disabled={uploading}
              />
            </label>
            <p className="text-xs text-gray-500 mt-4">Maximum file size: 10MB</p>
          </div>
        </form>
      </div>

      {/* Scan Results */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Recent Scans</h2>
        </div>
        {loading ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    File
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Size
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Result
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {scanResults.map((scan) => (
                  <tr key={scan.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        {getResultIcon(scan.scan_result)}
                        <div className="ml-3">
                          <div className="text-sm font-medium text-gray-900">{scan.filename}</div>
                          <div className="text-xs text-gray-500">Hash: {scan.file_hash.substring(0, 16)}...</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {(scan.file_size / 1024).toFixed(2)} KB
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${getResultColor(scan.scan_result)}`}>
                        {scan.scan_result}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {scan.confidence_score ? (scan.confidence_score * 100).toFixed(1) + '%' : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {scan.is_quarantined ? (
                        <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded">
                          Quarantined
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded">
                          Normal
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(scan.scan_timestamp).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {scanResults.length === 0 && (
              <div className="p-12 text-center text-gray-500">
                <FileSearch className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p>No scan results yet</p>
                <p className="text-sm mt-2">Upload a file to get started</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default FileScanner;
