import React, { useEffect, useState } from 'react';
import { useSSE } from '../context/SSEContext';
import { getTraces } from '../lib/api';

export const ReplayManager = () => {
    const { replayTrace, isRunning } = useSSE();
    const [traces, setTraces] = useState<any[]>([]);

    useEffect(() => {
        const fetchTraces = async () => {
            try {
                const res = await getTraces();
                setTraces(res.data);
            } catch (err) {
                console.error(err);
            }
        };
        fetchTraces();
    }, []);

    return (
        <div className="flex flex-col h-full bg-background border-r border-border font-mono">
            <div className="p-4 border-b border-border">
                <h2 className="text-sm font-bold text-gray-200 uppercase tracking-widest">Replay Manager</h2>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-2">
                {traces.length === 0 ? (
                    <div className="text-xs text-gray-500 italic">No traces found.</div>
                ) : (
                    traces.map((trace) => {
                        // Attempt to extract ticker from Market Data Collection event
                        const marketEvent = trace.events?.find((e: any) => e.event_type === 'STAGE_STARTED' && e.payload?.stage === 'Market Data Collection');
                        // Since we didn't store ticker directly, we can infer it or just use timestamp
                        // Actually, MarketAgent.gather_data output has company_name. Let's look for COMPLETED.
                        const marketComplete = trace.events?.find((e: any) => e.event_type === 'STAGE_COMPLETED' && e.payload?.stage === 'Market Data Collection');
                        const company = marketComplete?.payload?.result?.company_name || 'Analysis';
                        
                        // Fallback to timestamp if no valid company parsed
                        const time = trace.events?.[0]?.timestamp ? new Date(trace.events[0].timestamp).toLocaleString() : 'Unknown Time';

                        return (
                            <div 
                                key={trace.trace_id} 
                                onClick={() => !isRunning && replayTrace(trace.trace_id)}
                                className={`p-3 rounded border text-xs cursor-pointer transition-colors ${
                                    isRunning ? 'opacity-50 border-border cursor-not-allowed' : 'border-border bg-surface hover:border-primary hover:bg-[#1a1a1a]'
                                }`}
                            >
                                <div className="font-bold text-gray-300">{company}</div>
                                <div className="text-gray-500 mt-1">{time}</div>
                                <div className="text-[10px] text-gray-600 mt-2 truncate">ID: {trace.trace_id}</div>
                            </div>
                        )
                    })
                )}
            </div>
        </div>
    );
};
