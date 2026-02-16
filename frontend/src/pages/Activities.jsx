/**
 * Activities page - View system activities and logs.
 */
import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Activity as ActivityIcon, Filter, AlertCircle } from 'lucide-react';

const Activities = () => {
  const [activities, setActivities] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [suspiciousOnly, setSuspiciousOnly] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [suspiciousOnly]);

  const fetchData = async () => {
    try {
      const [activitiesRes, statsRes] = await Promise.all([
        apiService.getActivities({ suspicious_only: suspiciousOnly }),
        apiService.getActivityStats(),
      ]);

      setActivities(activitiesRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching activities:', error);
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (type) => {
    return <ActivityIcon className="w-5 h-5" />;
  };

  const getActivityColor = (type) => {
    const colors = {
      process: 'bg-blue-100 text-blue-800',
      file_access: 'bg-green-100 text-green-800',
      login: 'bg-purple-100 text-purple-800',
      network: 'bg-orange-100 text-orange-800',
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600">Total Activities</div>
          <div className="text-3xl font-bold text-gray-900 mt-2">{stats?.total_activities || 0}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600">Suspicious</div>
          <div className="text-3xl font-bold text-red-600 mt-2">{stats?.suspicious_count || 0}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600">Safe</div>
          <div className="text-3xl font-bold text-green-600 mt-2">{stats?.safe_count || 0}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-4">
          <Filter className="w-5 h-5 text-gray-500" />
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={suspiciousOnly}
              onChange={(e) => setSuspiciousOnly(e.target.checked)}
              className="mr-2 rounded text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm font-medium text-gray-700">Show suspicious only</span>
          </label>
        </div>
      </div>

      {/* Activities List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Source
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
              {activities.map((activity) => (
                <tr key={activity.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getActivityColor(activity.activity_type)}`}>
                      {activity.activity_type}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{activity.description}</div>
                    {activity.process_name && (
                      <div className="text-xs text-gray-500">Process: {activity.process_name}</div>
                    )}
                    {activity.file_path && (
                      <div className="text-xs text-gray-500">File: {activity.file_path}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{activity.source_ip || 'N/A'}</div>
                    {activity.user_id && (
                      <div className="text-xs text-gray-500">{activity.user_id}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {activity.is_suspicious ? (
                      <div className="flex items-center">
                        <AlertCircle className="w-4 h-4 text-red-500 mr-1" />
                        <span className="text-sm font-medium text-red-700">Suspicious</span>
                        {activity.confidence_score && (
                          <span className="ml-2 text-xs text-gray-500">
                            ({(activity.confidence_score * 100).toFixed(0)}%)
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-green-700">Safe</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(activity.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {activities.length === 0 && (
            <div className="p-12 text-center text-gray-500">
              <ActivityIcon className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p>No activities found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Activities;
