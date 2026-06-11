import React, { useState } from 'react';
import { VisualFlowGraph } from './VisualFlowGraph';
import { ExecutionTimeline } from './ExecutionTimeline';
import { CommitteeRoomView } from './CommitteeRoomView';
import { ReplayManager } from './ReplayManager';
import { useSSE } from '../context/SSEContext';

export const DashboardLayout = () => {
    const { startAnalysis, isRunning } = useSSE();
    const [ticker, setTicker] = useState('RELIANCE.NS');

    const handleRun = () => {
        if (!ticker || isRunning) return;
        startAnalysis(ticker);
    };

    return (
        <div className="h-screen w-screen flex bg-background text-gray-200 overflow-hidden">
            {/* Left Sidebar: Replays */}
            <div className="w-64 flex-shrink-0 z-10 shadow-2xl relative">
                <ReplayManager />
            </div>

            {/* Main Center Area: Flow Graph & Timeline */}
            <div className="flex-1 flex flex-col min-w-0 bg-[#0c0c0c]">
                {/* Header */}
                <header className="h-14 border-b border-border bg-surface flex items-center px-6 justify-between flex-shrink-0 shadow-sm relative z-10">
                    <div className="flex items-center space-x-3">
                        <div className="w-3 h-3 bg-primary shadow-[0_0_8px_rgba(16,185,129,0.8)]"></div>
                        <h1 className="font-bold text-sm tracking-widest text-gray-300">COMMITTEE INTELLIGENCE</h1>
                    </div>
                    
                    <div className="flex items-center space-x-4 font-mono">
                        <input 
                            type="text" 
                            value={ticker}
                            onChange={(e) => setTicker(e.target.value.toUpperCase())}
                            className="bg-background border border-border rounded px-3 py-1 text-sm focus:outline-none focus:border-primary transition-colors text-center w-32 uppercase"
                            placeholder="TICKER"
                        />
                        <button 
                            onClick={handleRun}
                            disabled={isRunning}
                            className={`px-4 py-1.5 rounded text-xs font-bold tracking-widest transition-all ${
                                isRunning ? 'bg-border text-gray-500 cursor-not-allowed' : 'bg-primary text-background hover:bg-emerald-400 hover:shadow-[0_0_15px_rgba(16,185,129,0.4)]'
                            }`}
                        >
                            {isRunning ? 'EXECUTING...' : 'RUN ANALYSIS'}
                        </button>
                    </div>
                </header>

                {/* Graph Area */}
                <div className="flex-1 p-6 overflow-hidden">
                    <VisualFlowGraph />
                </div>

                {/* Timeline Area */}
                <div className="h-[30%] p-6 pt-0">
                    <ExecutionTimeline />
                </div>
            </div>

            {/* Right Sidebar: Committee View */}
            <div className="w-[450px] flex-shrink-0 shadow-2xl relative z-10">
                <CommitteeRoomView />
            </div>
        </div>
    );
};
