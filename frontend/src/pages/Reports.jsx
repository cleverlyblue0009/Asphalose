/**
 * Reports page - Analytics and reporting.
 */
import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Activity, AlertTriangle, FileSearch } from 'lucide-react';

const Reports = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const summaryRes = await apiService.getSummary();
      setSummary(summaryRes.data);
    } catch (error) {
      console.error('Error fetching reports:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const overview = summary?.overview || {};
  const timeline = summary?.timeline || [];
  const activityByType = summary?.activity_by_type || {};
  const alertsBySeverity = summary?.alerts_by_severity || {};

  // Convert activity by type to chart data
  const activityTypeData = Object.entries(activityByType).map(([key, value]) => ({
    name: key.replace('_', ' '),
    value: value,
  }));

  // Convert alerts by severity to chart data
  const severityData = Object.entries(alertsBySeverity).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    value: value,
  }));

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];
  const SEVERITY_COLORS = {
    Critical: '#ef4444',
    High: '#f97316',
    Medium: '#eab308',
    Low: '#3b82f6',
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600">Total Activities</h3>
            <Activity className="w-8 h-8 text-blue-500" />
          </div>
          <div className="text-3xl font-bold text-gray-900">{overview.total_activities || 0}</div>
          <p className="text-sm text-gray-600 mt-2">
            {overview.suspicious_activities || 0} suspicious
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600">Active Alerts</h3>
            <AlertTriangle className="w-8 h-8 text-red-500" />
          </div>
          <div className="text-3xl font-bold text-gray-900">{overview.active_alerts || 0}</div>
          <p className="text-sm text-gray-600 mt-2">
            {overview.critical_alerts || 0} critical
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600">File Scans</h3>
            <FileSearch className="w-8 h-8 text-yellow-500" />
          </div>
          <div className="text-3xl font-bold text-gray-900">{overview.total_scans || 0}</div>
          <p className="text-sm text-gray-600 mt-2">
            {overview.malicious_files || 0} threats detected
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600">Threat Rate</h3>
            <TrendingUp className="w-8 h-8 text-purple-500" />
          </div>
          <div className="text-3xl font-bold text-gray-900">
            {overview.total_activities > 0
              ? ((overview.suspicious_activities / overview.total_activities) * 100).toFixed(1)
              : 0}%
          </div>
          <p className="text-sm text-gray-600 mt-2">Detection rate</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity Timeline */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity Timeline (7 Days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timeline}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="activities" stroke="#3b82f6" name="Total" strokeWidth={2} />
              <Line type="monotone" dataKey="suspicious" stroke="#ef4444" name="Suspicious" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Activity by Type */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity by Type</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={activityTypeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Alerts by Severity */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Alerts by Severity</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={severityData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.name}: ${entry.value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {severityData.map((entry) => (
                  <Cell key={`cell-${entry.name}`} fill={SEVERITY_COLORS[entry.name] || '#3b82f6'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Activity Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={activityTypeData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => entry.name}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {activityTypeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Stats */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Detailed Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-2">Activity Types</h4>
            <div className="space-y-2">
              {Object.entries(activityByType).map(([type, count]) => (
                <div key={type} className="flex justify-between text-sm">
                  <span className="text-gray-700">{type.replace('_', ' ')}:</span>
                  <span className="font-medium text-gray-900">{count}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-2">Alert Severity</h4>
            <div className="space-y-2">
              {Object.entries(alertsBySeverity).map(([severity, count]) => (
                <div key={severity} className="flex justify-between text-sm">
                  <span className="text-gray-700">{severity}:</span>
                  <span className="font-medium text-gray-900">{count}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-2">Recent Activity (24h)</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-700">Total:</span>
                <span className="font-medium text-gray-900">{summary?.recent?.activities_24h || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-700">Suspicious:</span>
                <span className="font-medium text-red-600">{summary?.recent?.suspicious_24h || 0}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reports;
