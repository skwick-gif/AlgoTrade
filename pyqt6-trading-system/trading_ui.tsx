import React from 'react';
import { Activity, Wifi, WifiOff, Circle, TrendingUp, TrendingDown, BarChart3 } from 'lucide-react';

const TradingUI = () => {
  const [activeTab, setActiveTab] = React.useState(0);
  const [vixValue] = React.useState(18.5);
  const [marketRegime] = React.useState('Bull');
  const [ibkrStatus] = React.useState('connected');
  const [accountType] = React.useState('paper');

  const tabs = ['Dashboard', 'Scanning', 'Watchlist', 'Options Trading', 'Analytics', 'Settings'];
  
  const sidebarContent = {
    0: ['Overview', 'Markets', 'Positions', 'P&L', 'News', 'Alerts'],
    1: ['Stock Scanner', 'Options Scanner', 'Filters', 'Results', 'Saved Scans', 'Export'],
    2: ['Active List', 'Create List', 'Price Alerts', 'Volume Alerts', 'Technical Alerts', 'History'],
    3: ['Strategy Builder', 'Active Trades', 'Strategy 1-4', 'Backtest', 'Settings'],
    4: ['Performance', 'Reports', 'Trade History', 'Risk Analysis', 'Charts', 'Export'],
    5: ['Account', 'Data Sources', 'API Keys', 'Notifications', 'Import/Export', 'About']
  };

  const getVixColor = (vix) => {
    if (vix < 20) return '#22c55e';
    if (vix < 30) return '#f59e0b';
    return '#ef4444';
  };

  const getVixRotation = (vix) => {
    return Math.min((vix / 50) * 180, 180);
  };

  const getVixLabel = (vix) => {
    if (vix < 12) return 'LOW';
    if (vix < 20) return 'NORMAL';
    if (vix < 30) return 'HIGH';
    return 'EXTREME';
  };

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-xl font-semibold text-gray-800">AlgoTrade Pro</h1>
        </div>
        
        <div className="flex items-center space-x-8">
          {/* VIX Gauge */}
          <div className="flex flex-col items-center space-y-1">
            <span className="text-xs text-gray-500">VIX</span>
            <div className="relative w-16 h-8">
              {/* Gauge background */}
              <div className="absolute inset-0">
                <svg width="64" height="32" viewBox="0 0 64 32">
                  <path 
                    d="M 8 24 A 24 24 0 0 1 56 24" 
                    fill="none" 
                    stroke="#e5e7eb" 
                    strokeWidth="4"
                  />
                  <path 
                    d="M 8 24 A 24 24 0 0 1 24 8" 
                    fill="none" 
                    stroke="#22c55e" 
                    strokeWidth="4"
                  />
                  <path 
                    d="M 24 8 A 24 24 0 0 1 40 8" 
                    fill="none" 
                    stroke="#f59e0b" 
                    strokeWidth="4"
                  />
                  <path 
                    d="M 40 8 A 24 24 0 0 1 56 24" 
                    fill="none" 
                    stroke="#ef4444" 
                    strokeWidth="4"
                  />
                </svg>
                
                {/* Needle */}
                <div 
                  className="absolute bottom-0 left-1/2 w-0.5 h-6 bg-gray-800 origin-bottom transform -translate-x-1/2 transition-transform duration-500"
                  style={{
                    transform: `translateX(-50%) rotate(${getVixRotation(vixValue) - 90}deg)`
                  }}
                ></div>
                
                {/* Center dot */}
                <div className="absolute bottom-0 left-1/2 w-2 h-2 bg-gray-800 rounded-full transform -translate-x-1/2 translate-y-1"></div>
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs font-bold" style={{color: getVixColor(vixValue)}}>{vixValue}</div>
              <div className="text-xs text-gray-400">{getVixLabel(vixValue)}</div>
            </div>
          </div>

          {/* Market Regime */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Market</span>
            <div className="flex items-center space-x-1">
              {marketRegime === 'Bull' ? (
                <TrendingUp className="w-4 h-4 text-green-500" />
              ) : (
                <TrendingDown className="w-4 h-4 text-red-500" />
              )}
              <span className={`text-sm font-medium ${marketRegime === 'Bull' ? 'text-green-600' : 'text-red-600'}`}>
                {marketRegime}
              </span>
            </div>
          </div>

          {/* IBKR Connection */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">IBKR</span>
            <div className="flex items-center space-x-1">
              {ibkrStatus === 'connected' ? (
                <Wifi className="w-4 h-4 text-green-500" />
              ) : (
                <WifiOff className="w-4 h-4 text-red-500" />
              )}
              <div className="flex items-center space-x-1">
                <Circle 
                  className={`w-2 h-2 fill-current ${accountType === 'paper' ? 'text-blue-500' : 'text-orange-500'}`} 
                />
                <span className={`text-xs ${accountType === 'paper' ? 'text-blue-600' : 'text-orange-600'}`}>
                  {accountType === 'paper' ? 'PAPER' : 'LIVE'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="flex px-6">
          {tabs.map((tab, index) => (
            <button
              key={tab}
              onClick={() => setActiveTab(index)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === index
                  ? 'text-blue-600 border-blue-600'
                  : 'text-gray-500 border-transparent hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-48 bg-white border-r border-gray-200 py-4">
          <nav className="space-y-1 px-3">
            {sidebarContent[activeTab].map((button, index) => (
              <button
                key={button}
                className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              >
                {button}
              </button>
            ))}
          </nav>
        </div>

        {/* Content Area */}
        <div className="flex-1 bg-gray-50 p-6">
          <div className="bg-white rounded-lg shadow-sm h-full p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              {tabs[activeTab]} Content
            </h2>
            <div className="text-gray-500 text-center py-20">
              Content for {tabs[activeTab]} will be displayed here
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingUI;