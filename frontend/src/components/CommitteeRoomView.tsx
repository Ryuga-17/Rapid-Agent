import React from 'react';
import { useSSE } from '../context/SSEContext';

const SectionHeader = ({ title }: { title: string }) => (
    <h3 className="text-xs uppercase tracking-widest text-gray-500 font-bold mb-3 border-b border-border pb-2">{title}</h3>
);

export const CommitteeRoomView = () => {
    const { nodePayloads } = useSSE();

    const market = nodePayloads['Market Data Collection'];
    const macro = nodePayloads['Macro Analysis'];
    const regime = nodePayloads['Regime Detection'];
    const committee = nodePayloads['Committee Analysis (LLM)'];
    const history = nodePayloads['Historical Memory Retrieval'];

    return (
        <div className="h-full bg-surface border-l border-border flex flex-col font-mono overflow-y-auto">
            <div className="bg-border px-6 py-4 border-b border-border">
                <h2 className="text-lg font-bold text-gray-200 tracking-wide">COMMITTEE ROOM</h2>
                <p className="text-xs text-gray-500">Live Execution Payload Introspection</p>
            </div>

            <div className="p-6 space-y-8 flex-1">
                {/* 1. Market Agent */}
                <section>
                    <SectionHeader title="Market Agent" />
                    {market ? (
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div><span className="text-gray-500">Company:</span> <span className="text-gray-200">{market.company_name}</span></div>
                            <div><span className="text-gray-500">Price:</span> <span className="text-gray-200">${market.market_data?.price}</span></div>
                            <div><span className="text-gray-500">PE Ratio:</span> <span className="text-gray-200">{market.market_data?.pe_ratio}</span></div>
                            <div><span className="text-gray-500">Volatility:</span> <span className="text-gray-200">{market.market_data?.volatility}%</span></div>
                        </div>
                    ) : <div className="text-sm text-gray-600 italic">Waiting for data...</div>}
                </section>

                {/* 2. Macro Agent */}
                <section>
                    <SectionHeader title="Macro Agent" />
                    {macro ? (
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div><span className="text-gray-500">Inflation:</span> <span className="text-gray-200">{macro.inflation}%</span></div>
                            <div><span className="text-gray-500">Interest Rate:</span> <span className="text-gray-200">{macro.interest_rate}%</span></div>
                            <div><span className="text-gray-500">GDP Growth:</span> <span className="text-gray-200">{macro.gdp_growth}%</span></div>
                        </div>
                    ) : <div className="text-sm text-gray-600 italic">Waiting for data...</div>}
                </section>

                {/* 3. Regime Service */}
                <section>
                    <SectionHeader title="Regime Service" />
                    {regime ? (
                        <div className="text-sm space-y-2">
                            <div><span className="text-gray-500">Current Regime:</span> <span className="text-blue-400 font-bold">{regime.regime}</span></div>
                            <div><span className="text-gray-500">Confidence:</span> <span className="text-gray-200">{regime.confidence * 100}%</span></div>
                            <div>
                                <span className="text-gray-500">Triggering Factors:</span>
                                <ul className="list-disc list-inside text-gray-300 mt-1">
                                    {regime.triggering_factors?.map((f: string, i: number) => <li key={i}>{f}</li>)}
                                </ul>
                            </div>
                        </div>
                    ) : <div className="text-sm text-gray-600 italic">Waiting for data...</div>}
                </section>

                {/* 4. Historical Memory */}
                <section>
                    <SectionHeader title="Historical Memory Panel" />
                    {history ? (
                        <div className="text-sm space-y-3 bg-background p-4 rounded border border-border">
                            {history.previous_rating ? (
                                <>
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-500">Recommendation Shift:</span>
                                        <div className="flex items-center space-x-2 font-bold">
                                            <span className="text-gray-400">{history.previous_rating}</span>
                                            <span className="text-gray-500">→</span>
                                            <span className={history.current_rating === 'Buy' ? 'text-primary' : history.current_rating === 'Sell' ? 'text-danger' : 'text-yellow-500'}>
                                                {history.current_rating}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-500">Confidence Change:</span>
                                        <span className={history.confidence_change >= 0 ? 'text-primary' : 'text-danger'}>
                                            {history.confidence_change > 0 ? '+' : ''}{history.confidence_change}%
                                        </span>
                                    </div>
                                    {history.new_risks?.length > 0 && (
                                        <div className="mt-2">
                                            <span className="text-danger">New Risks Identified:</span>
                                            <ul className="list-disc list-inside text-gray-300 mt-1">
                                                {history.new_risks.map((r: string, i: number) => <li key={i}>{r}</li>)}
                                            </ul>
                                        </div>
                                    )}
                                </>
                            ) : (
                                <div className="text-gray-500 italic">No previous history for this asset. Baseline established.</div>
                            )}
                        </div>
                    ) : <div className="text-sm text-gray-600 italic">Waiting for data...</div>}
                </section>

                {/* 5. Final Recommendation */}
                <section>
                    <SectionHeader title="Recommendation Explainer" />
                    {committee ? (
                        <div className="space-y-4">
                            <div className="flex items-center space-x-4">
                                <div className={`px-4 py-2 rounded font-bold text-lg border ${
                                    committee.rating === 'Buy' ? 'bg-primary/10 border-primary text-primary' : 
                                    committee.rating === 'Sell' ? 'bg-danger/10 border-danger text-danger' : 
                                    'bg-yellow-500/10 border-yellow-500 text-yellow-500'
                                }`}>
                                    {committee.rating}
                                </div>
                                <div className="text-sm">
                                    <div className="text-gray-500">Confidence</div>
                                    <div className="text-lg font-bold">{committee.confidence}%</div>
                                </div>
                            </div>
                            <div className="text-sm space-y-2">
                                <div><span className="text-primary font-bold">Bull Case:</span> <span className="text-gray-300">{committee.bull_case}</span></div>
                                <div><span className="text-danger font-bold">Bear Case:</span> <span className="text-gray-300">{committee.bear_case}</span></div>
                                <div>
                                    <span className="text-gray-500 font-bold">Key Risks:</span>
                                    <ul className="list-disc list-inside text-gray-300 mt-1">
                                        {committee.key_risks?.map((r: string, i: number) => <li key={i}>{r}</li>)}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    ) : <div className="text-sm text-gray-600 italic">Waiting for data...</div>}
                </section>
            </div>
        </div>
    );
};
