import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { analyzeStock, getTraces } from '../lib/api';

export type NodeStatus = 'Idle' | 'Running' | 'Completed' | 'Failed';

export interface TraceEvent {
    trace_id: string;
    event_type: 'STAGE_STARTED' | 'STAGE_COMPLETED' | 'STAGE_FAILED';
    timestamp: string;
    payload: any;
}

interface SSEContextType {
    traceId: string | null;
    events: TraceEvent[];
    nodeStatuses: Record<string, NodeStatus>;
    nodePayloads: Record<string, any>;
    isRunning: boolean;
    startAnalysis: (ticker: string) => Promise<void>;
    replayTrace: (traceId: string) => Promise<void>;
    resetState: () => void;
}

const SSEContext = createContext<SSEContextType | undefined>(undefined);

export const SSEProvider: React.FC<{children: ReactNode}> = ({ children }) => {
    const [traceId, setTraceId] = useState<string | null>(null);
    const [events, setEvents] = useState<TraceEvent[]>([]);
    const [nodeStatuses, setNodeStatuses] = useState<Record<string, NodeStatus>>({});
    const [nodePayloads, setNodePayloads] = useState<Record<string, any>>({});
    const [isRunning, setIsRunning] = useState(false);

    const resetState = useCallback(() => {
        setTraceId(null);
        setEvents([]);
        setNodeStatuses({});
        setNodePayloads({});
        setIsRunning(false);
    }, []);

    const processEvent = useCallback((event: TraceEvent) => {
        setEvents(prev => [...prev, event]);
        const stage = event.payload?.stage;
        if (!stage) return;

        if (event.event_type === 'STAGE_STARTED') {
            setNodeStatuses(prev => ({ ...prev, [stage]: 'Running' }));
        } else if (event.event_type === 'STAGE_COMPLETED') {
            setNodeStatuses(prev => ({ ...prev, [stage]: 'Completed' }));
            if (event.payload.result) {
                setNodePayloads(prev => ({ ...prev, [stage]: event.payload.result }));
            }
        } else if (event.event_type === 'STAGE_FAILED') {
            setNodeStatuses(prev => ({ ...prev, [stage]: 'Failed' }));
        }
    }, []);

    const startAnalysis = async (ticker: string) => {
        resetState();
        setIsRunning(true);
        const newTraceId = crypto.randomUUID();
        setTraceId(newTraceId);

        const eventSource = new EventSource(`http://localhost:8000/stream/events/${newTraceId}`);
        
        eventSource.addEventListener('STAGE_STARTED', (e) => {
            const data = JSON.parse(e.data);
            processEvent(data);
        });
        eventSource.addEventListener('STAGE_COMPLETED', (e) => {
            const data = JSON.parse(e.data);
            processEvent(data);
        });
        eventSource.addEventListener('STAGE_FAILED', (e) => {
            const data = JSON.parse(e.data);
            processEvent(data);
        });

        try {
            await analyzeStock(ticker, newTraceId);
        } catch (error) {
            console.error(error);
        } finally {
            setIsRunning(false);
            eventSource.close();
        }
    };

    const replayTrace = async (targetTraceId: string) => {
        resetState();
        setTraceId(targetTraceId);
        setIsRunning(true);
        try {
            const res = await getTraces();
            const traceObj = res.data.find((t: any) => t.trace_id === targetTraceId);
            if (traceObj && traceObj.events) {
                for (const ev of traceObj.events) {
                    processEvent(ev);
                    await new Promise(r => setTimeout(r, 600)); 
                }
            }
        } catch (error) {
            console.error(error);
        } finally {
            setIsRunning(false);
        }
    };

    return (
        <SSEContext.Provider value={{
            traceId, events, nodeStatuses, nodePayloads, isRunning, startAnalysis, replayTrace, resetState
        }}>
            {children}
        </SSEContext.Provider>
    );
};

export const useSSE = () => {
    const context = useContext(SSEContext);
    if (!context) throw new Error("useSSE must be used within SSEProvider");
    return context;
};
