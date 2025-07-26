import React, { useState } from 'react';

const History = ({ history, isLoading, onClearHistory, onRefreshHistory }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [filter, setFilter] = useState('all'); // all, basic, scientific, financial, programming

  const filteredHistory = history.filter(item => {
    if (filter === 'all') return true;
    return item.mode === filter;
  });

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      // Could add a toast notification here
    });
  };

  const getModeIcon = (mode) => {
    const icons = {
      basic: '🔢',
      scientific: '🧮',
      financial: '💰',
      programming: '⚙️'
    };
    return icons[mode] || '🔢';
  };

  const getNumberSystemBadge = (numberSystem) => {
    if (numberSystem === 'decimal') return null;
    
    const badges = {
      hexadecimal: { text: 'HEX', color: 'bg-purple-500' },
      octal: { text: 'OCT', color: 'bg-orange-500' },
      binary: { text: 'BIN', color: 'bg-green-500' }
    };
    
    const badge = badges[numberSystem];
    if (!badge) return null;
    
    return (
      <span className={`text-xs px-2 py-1 rounded ${badge.color} text-white`}>
        {badge.text}
      </span>
    );
  };

  return (
    <div className="bg-calc-primary rounded-xl p-6 shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white flex items-center">
          📊 History
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="ml-2 text-sm text-gray-400 hover:text-white"
          >
            {isExpanded ? '▼' : '▶'}
          </button>
        </h2>
        
        <div className="flex gap-2">
          <button
            onClick={onRefreshHistory}
            className="calc-button text-xs px-2 py-1"
            disabled={isLoading}
            title="Refresh History"
          >
            🔄
          </button>
          <button
            onClick={onClearHistory}
            className="calc-button calc-button-danger text-xs px-2 py-1"
            disabled={isLoading}
            title="Clear History"
          >
            🗑️
          </button>
        </div>
      </div>

      {isExpanded && (
        <>
          {/* Filter */}
          <div className="mb-4">
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="w-full bg-calc-secondary text-white rounded p-2 text-sm"
            >
              <option value="all">All Calculations</option>
              <option value="basic">Basic</option>
              <option value="scientific">Scientific</option>
              <option value="financial">Financial</option>
              <option value="programming">Programming</option>
            </select>
          </div>

          {/* History List */}
          <div className="custom-scrollbar max-h-96 overflow-y-auto space-y-2">
            {isLoading && (
              <div className="text-center text-gray-400 py-4">
                Loading history...
              </div>
            )}
            
            {!isLoading && filteredHistory.length === 0 && (
              <div className="text-center text-gray-400 py-8">
                <div className="text-4xl mb-2">📝</div>
                <p>No calculations yet</p>
                <p className="text-sm">Start calculating to see history</p>
              </div>
            )}
            
            {!isLoading && filteredHistory.map((item, index) => (
              <div
                key={item.calculation_id || index}
                className="history-item bg-calc-secondary rounded-lg p-3 cursor-pointer hover:bg-opacity-80"
                onClick={() => copyToClipboard(item.formatted_result)}
                title="Click to copy result"
              >
                <div className="flex items-start justify-between mb-2">
                  <span className="text-xs text-gray-400 flex items-center gap-2">
                    {getModeIcon(item.mode)} {item.mode}
                    {getNumberSystemBadge(item.number_system)}
                  </span>
                  <span className="text-xs text-gray-500">
                    {formatTimestamp(item.timestamp)}
                  </span>
                </div>
                
                <div className="text-white font-mono text-sm mb-1">
                  <div className="text-gray-300 truncate" title={item.expression}>
                    {item.expression}
                  </div>
                  <div className="text-calc-accent font-bold">
                    = {item.formatted_result}
                  </div>
                </div>
                
                {item.error && (
                  <div className="text-calc-error text-xs mt-1">
                    Error: {item.error}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* History Stats */}
          {!isLoading && history.length > 0 && (
            <div className="mt-4 text-xs text-gray-400 text-center">
              {filteredHistory.length} of {history.length} calculations
              {filter !== 'all' && ` (${filter} mode)`}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default History;