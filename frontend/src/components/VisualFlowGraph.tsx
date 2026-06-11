import { useMemo, useEffect, useState } from 'react';
import { ReactFlow, Controls, Background, Position, Handle } from '@xyflow/react';
import type { Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useSSE } from '../context/SSEContext';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const cn = (...inputs: any[]) => twMerge(clsx(inputs));

const CustomNode = ({ data }: any) => {
    const { nodeStatuses } = useSSE();
    const status = nodeStatuses[data.label] || 'Idle';

    return (
        <div className={cn(
            "px-4 py-3 rounded-lg border bg-surface flex items-center justify-between min-w-[220px] transition-all duration-300 shadow-lg",
            status === 'Idle' && "border-border text-gray-400",
            status === 'Running' && "border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.5)] text-blue-400",
            status === 'Completed' && "border-primary shadow-[0_0_15px_rgba(16,185,129,0.3)] text-primary",
            status === 'Failed' && "border-danger shadow-[0_0_15px_rgba(239,68,68,0.5)] text-danger"
        )}>
            <Handle type="target" position={Position.Top} className="opacity-0" />
            <span className="font-semibold text-sm tracking-wide">{data.label}</span>
            <div className="flex items-center space-x-2">
                {status === 'Running' && (
                    <span className="relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
                    </span>
                )}
                {status === 'Completed' && (
                    <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
                )}
                {status === 'Failed' && (
                    <svg className="w-4 h-4 text-danger" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M6 18L18 6M6 6l12 12"></path></svg>
                )}
            </div>
            <Handle type="source" position={Position.Bottom} className="opacity-0" />
        </div>
    );
};

const nodeTypes = {
    custom: CustomNode,
};

const initialNodes: Node[] = [
    { id: '1', type: 'custom', position: { x: 50, y: 50 }, data: { label: 'Market Data Collection' } },
    { id: '2', type: 'custom', position: { x: 350, y: 50 }, data: { label: 'Macro Analysis' } },
    { id: '3', type: 'custom', position: { x: 350, y: 150 }, data: { label: 'Regime Detection' } },
    { id: '4', type: 'custom', position: { x: 200, y: 250 }, data: { label: 'Committee Analysis (LLM)' } },
    { id: '5', type: 'custom', position: { x: 200, y: 350 }, data: { label: 'Historical Memory Retrieval' } },
    { id: '6', type: 'custom', position: { x: 50, y: 450 }, data: { label: 'Audit Logging' } },
    { id: '7', type: 'custom', position: { x: 350, y: 450 }, data: { label: 'MongoDB Persistence' } },
];

const initialEdges: Edge[] = [
    { id: 'e1-4', source: '1', target: '4', animated: true },
    { id: 'e2-3', source: '2', target: '3', animated: true },
    { id: 'e3-4', source: '3', target: '4', animated: true },
    { id: 'e4-5', source: '4', target: '5', animated: true },
    { id: 'e5-6', source: '5', target: '6', animated: true },
    { id: 'e5-7', source: '5', target: '7', animated: true },
];

export const VisualFlowGraph = () => {
    const { isRunning, nodeStatuses } = useSSE();
    
    // Dynamically update edge animations based on state
    const edges = useMemo(() => {
        return initialEdges.map(edge => {
            const sourceStatus = nodeStatuses[initialNodes.find(n => n.id === edge.source)?.data.label as string];
            const targetStatus = nodeStatuses[initialNodes.find(n => n.id === edge.target)?.data.label as string];
            
            const isAnimating = (sourceStatus === 'Completed' && targetStatus !== 'Completed') || isRunning;
            
            return {
                ...edge,
                animated: isAnimating,
                style: { stroke: sourceStatus === 'Completed' ? '#10b981' : '#262626' }
            };
        });
    }, [nodeStatuses, isRunning]);

    return (
        <div className="h-full w-full bg-background rounded-xl border border-border overflow-hidden">
            <ReactFlow 
                nodes={initialNodes} 
                edges={edges} 
                nodeTypes={nodeTypes}
                fitView
                className="bg-background"
                proOptions={{ hideAttribution: true }}
            >
                <Background color="#262626" gap={16} />
                <Controls className="react-flow__controls" />
            </ReactFlow>
        </div>
    );
};
