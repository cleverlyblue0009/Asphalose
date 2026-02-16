/**
 * ML Models page - View and manage ML models.
 */
import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Brain, TrendingUp, Clock, CheckCircle, AlertCircle } from 'lucide-react';

const Models = () => {
  const [status, setStatus] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [latestMetrics, setLatestMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statusRes, metricsRes, latestRes] = await Promise.all([
        apiService.getModelStatus(),
        apiService.getModelMetrics(10),
        apiService.getLatestMetrics(),
      ]);

      setStatus(statusRes.data);
      setMetrics(metricsRes.data);
      setLatestMetrics(latestRes.data);
    } catch (error) {
      console.error('Error fetching model data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTrainModels = async () => {
    if (!confirm('This will retrain all ML models. Continue?')) return;

    setTraining(true);
    try {
      await apiService.trainModels();
      alert('Model training started in background. This may take a few minutes.');
      setTimeout(fetchData, 5000); // Refresh after 5 seconds
    } catch (error) {
      console.error('Error training models:', error);
      alert('Error training models: ' + (error.response?.data?.detail || error.message));
    } finally {
      setTraining(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const bcMetrics = latestMetrics?.behavioral_classifier;
  const adMetrics = latestMetrics?.anomaly_detector;

  return (
    <div className="space-y-6">
      {/* Model Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Behavioral Classifier</h3>
            {status?.behavioral_classifier?.available ? (
              <CheckCircle className="w-6 h-6 text-green-500" />
            ) : (
              <AlertCircle className="w-6 h-6 text-red-500" />
            )}
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Status:</span>
              <span className={`font-medium ${status?.behavioral_classifier?.available ? 'text-green-600' : 'text-red-600'}`}>
                {status?.behavioral_classifier?.available ? 'Ready' : 'Not Available'}
              </span>
            </div>
            {bcMetrics && (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-600">Accuracy:</span>
                  <span className="font-medium text-gray-900">
                    {(bcMetrics.accuracy * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">F1 Score:</span>
                  <span className="font-medium text-gray-900">
                    {(bcMetrics.f1_score * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Training Samples:</span>
                  <span className="font-medium text-gray-900">
                    {bcMetrics.training_samples}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Last Trained:</span>
                  <span className="font-medium text-gray-900">
                    {new Date(bcMetrics.trained_at).toLocaleString()}
                  </span>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Anomaly Detector</h3>
            {status?.anomaly_detector?.available ? (
              <CheckCircle className="w-6 h-6 text-green-500" />
            ) : (
              <AlertCircle className="w-6 h-6 text-red-500" />
            )}
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Status:</span>
              <span className={`font-medium ${status?.anomaly_detector?.available ? 'text-green-600' : 'text-red-600'}`}>
                {status?.anomaly_detector?.available ? 'Ready' : 'Not Available'}
              </span>
            </div>
            {adMetrics && (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-600">Model Type:</span>
                  <span className="font-medium text-gray-900">
                    Isolation Forest
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Training Samples:</span>
                  <span className="font-medium text-gray-900">
                    {adMetrics.training_samples}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Last Trained:</span>
                  <span className="font-medium text-gray-900">
                    {new Date(adMetrics.trained_at).toLocaleString()}
                  </span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Actions</h3>
        <div className="flex items-center space-x-4">
          <button
            onClick={handleTrainModels}
            disabled={training}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium flex items-center"
          >
            <Brain className="w-5 h-5 mr-2" />
            {training ? 'Training...' : 'Train Models'}
          </button>
          <p className="text-sm text-gray-600">
            Retrain both ML models with synthetic data. This will take a few minutes.
          </p>
        </div>
      </div>

      {/* Training History */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Training History</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Model
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Accuracy
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  F1 Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Samples
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Trained At
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {metrics?.map((metric) => (
                <tr key={metric.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <Brain className="w-5 h-5 text-primary-500 mr-2" />
                      <span className="text-sm font-medium text-gray-900">
                        {metric.model_name.replace('_', ' ')}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.model_type}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.accuracy ? (metric.accuracy * 100).toFixed(2) + '%' : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.f1_score ? (metric.f1_score * 100).toFixed(2) + '%' : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.training_samples}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(metric.trained_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {(!metrics || metrics.length === 0) && (
            <div className="p-12 text-center text-gray-500">
              <Brain className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p>No training history</p>
              <p className="text-sm mt-2">Train models to see history</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Models;
