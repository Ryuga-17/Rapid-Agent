import React, { useRef, useEffect } from 'react';
import { useSSE } from '../context/SSEContext';

export const ExecutionTimeline = () => {
    const { events } = useSSE();
    const endOfMessagesRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [events]);

    return (
        <div className="h-full flex flex-col bg-surface border border-border rounded-xl overflow-hidden font-mono text-sm">
            <div className="bg-border px-4 py-2 text-gray-300 font-semibold border-b border-border flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-primary animate-pulse"></div>
                <span>LIVE DECISION TIMELINE</span>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {events.length === 0 && (
                    <div className="text-gray-500 italic">Waiting for execution to start...</div>
                )}
                {events.map((ev, idx) => {
                    const time = new Date(ev.timestamp).toLocaleTimeString([], { hour12: false });
                    const isStart = ev.event_type === 'STAGE_STARTED';
                    const isFail = ev.event_type === 'STAGE_FAILED';
                    
                    return (
                        <div key={idx} className="flex flex-col space-y-1">
                            <div className="flex items-start space-x-3">
                                <span className="text-gray-500 w-20 flex-shrink-0">{time}</span>
                                <div className={`flex-1 ${isStart ? 'text-gray-300' : isFail ? 'text-danger' : 'text-primary'}`}>
                                    {isStart ? `Initiated: ${ev.payload.stage}` : 
                                     isFail ? `Failed: ${ev.payload.stage} (${ev.payload.error})` : 
                                     `Completed: ${ev.payload.stage} [${ev.payload.duration_sec}s]`}
                                </div>
                            </div>
                        </div>
                    );
                })}
                <div ref={endOfMessagesRef} />
            </div>
        </div>
    );
};
