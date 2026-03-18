'use client';

import { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Send, RefreshCw, AlertCircle, TrendingUp } from 'lucide-react';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316'];

export default function Dashboard() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8080';
  const [query, setQuery] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [history, setHistory] = useState([]);
  const [columns, setColumns] = useState([]);

  // Fetch available columns on mount
  useEffect(() => {
    const fetchColumns = async () => {
      try {
        const response = await fetch(`${API_URL}/columns`);
        const result = await response.json();
        setColumns(result.columns || []);
      } catch (err) {
        console.error('Failed to fetch columns:', err);
      }
    };
    fetchColumns();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_query: query }),
      });

      const result = await response.json();

      if (result.error) {
        setError(result.error);
        setData(null);
      } else {
        setData(result);
        setHistory([{ query, timestamp: new Date() }, ...history.slice(0, 4)]);
        setError('');
      }
    } catch (err) {
      setError(`Connection error: ${err.message}`);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickQuery = (q) => {
    setQuery(q);
  };

  const renderChart = () => {
    if (!data?.data || data.data.length === 0) return null;

    const chart_data = data.data;
    const xAxis = data.meta?.x || 'x';
    const yAxis = data.meta?.y || 'y';
    const chartType = data.meta?.chart_type || 'bar';

    try {
      return (
        <div className="w-full h-96 mt-6">
          <ResponsiveContainer width="100%" height="100%">
            {chartType === 'pie' ? (
              <PieChart>
                <Pie
                  data={chart_data}
                  dataKey={yAxis}
                  nameKey={xAxis}
                  cx="50%"
                  cy="50%"
                  outerRadius={120}
                  label
                >
                  {chart_data.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            ) : chartType === 'line' ? (
              <LineChart data={chart_data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={xAxis} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey={yAxis} stroke="#3b82f6" />
              </LineChart>
            ) : (
              <BarChart data={chart_data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={xAxis} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey={yAxis} fill="#3b82f6" />
              </BarChart>
            )}
          </ResponsiveContainer>
        </div>
      );
    } catch (err) {
      return <div className="text-red-500">Chart rendering failed</div>;
    }
  };

  const quickQueries = [
    'What is the average price by model?',
    'Show me total tax grouped by transmission',
    'How many cars by year?',
    'Maximum mileage by fueltype',
    'Average engine size by fuel type',
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-8 h-8 text-blue-500" />
            <h1 className="text-4xl font-bold text-white">Conversational Dashboard</h1>
          </div>
          <p className="text-slate-400">Ask questions about your data in natural language</p>
        </div>

        {/* Query Input */}
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-6 mb-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question... e.g., 'What is the average price by model?'"
                className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 transition"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-500 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition"
              >
                <Send className="w-4 h-4" />
                {loading ? 'Analyzing...' : 'Query'}
              </button>
            </div>

            {/* Quick Query Buttons */}
            <div className="flex flex-wrap gap-2">
              <span className="text-sm text-slate-400 w-full">Quick queries:</span>
              {quickQueries.map((q, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => handleQuickQuery(q)}
                  className="text-xs bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1.5 rounded transition"
                >
                  {q.substring(0, 30)}...
                </button>
              ))}
            </div>
          </form>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-950 border border-red-700 rounded-lg p-4 mb-8 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {/* Results */}
        {data && !error && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            {/* Main Content */}
            <div className="lg:col-span-2 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-6">
              {/* Query Info */}
              <div className="mb-6 p-4 bg-slate-700/30 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-white font-semibold">Query Analysis</h3>
                  <span className="text-xs bg-blue-600 text-white px-3 py-1 rounded-full">
                    {data.meta?.aggregation?.toUpperCase() || 'ANALYSIS'}
                  </span>
                </div>
                <p className="text-slate-300 text-sm mb-3">{data.meta?.query_parsed}</p>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div className="bg-slate-700/50 p-3 rounded">
                    <p className="text-slate-400">X-Axis</p>
                    <p className="text-white font-mono">{data.meta?.x}</p>
                  </div>
                  <div className="bg-slate-700/50 p-3 rounded">
                    <p className="text-slate-400">Y-Axis</p>
                    <p className="text-white font-mono">{data.meta?.y}</p>
                  </div>
                  <div className="bg-slate-700/50 p-3 rounded">
                    <p className="text-slate-400">Records</p>
                    <p className="text-white font-mono">{data.meta?.record_count || data.data.length}</p>
                  </div>
                </div>
              </div>

              {/* Chart */}
              {data.data && data.data.length > 0 && (
                <div className="border-t border-slate-700 pt-6">
                  <h3 className="text-white font-semibold mb-4">Visualization</h3>
                  {renderChart()}
                </div>
              )}
            </div>

            {/* Data Table */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-6">
              <h3 className="text-white font-semibold mb-4">Data</h3>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {data.data && data.data.length > 0 ? (
                  data.data.slice(0, 10).map((item, i) => (
                    <div key={i} className="bg-slate-700/30 p-3 rounded-lg border border-slate-600 hover:border-blue-500 transition">
                      {Object.entries(item).map(([key, value]) => (
                        <div key={key} className="text-sm">
                          <span className="text-slate-400">{key}:</span>
                          <span className="text-white ml-2 font-mono">{value}</span>
                        </div>
                      ))}
                    </div>
                  ))
                ) : (
                  <p className="text-slate-400 text-sm">No data available</p>
                )}
                {data.data && data.data.length > 10 && (
                  <p className="text-slate-400 text-sm mt-2">+{data.data.length - 10} more records</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Query History */}
        {history.length > 0 && (
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-6">
            <h3 className="text-white font-semibold mb-4">Recent Queries</h3>
            <div className="space-y-2">
              {history.map((item, i) => (
                <button
                  key={i}
                  onClick={() => handleQuickQuery(item.query)}
                  className="w-full text-left bg-slate-700/30 hover:bg-slate-700/50 p-3 rounded-lg border border-slate-600 hover:border-blue-500 transition"
                >
                  <p className="text-white text-sm">{item.query}</p>
                  <p className="text-slate-400 text-xs mt-1">{item.timestamp.toLocaleTimeString()}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!data && !error && (
          <div className="text-center py-12">
            <TrendingUp className="w-12 h-12 text-slate-600 mx-auto mb-4 opacity-50" />
            <p className="text-slate-400">Enter a query to get started</p>
          </div>
        )}
      </div>
    </div>
  );
}
