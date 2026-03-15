
import React from 'react';

const Positions = ({ positions, marketData }) => {
    const formatPrice = (p) => p ? p.toFixed(2) : "0.00";
    
    return (
        <div className="positions-section" style={{ marginTop: '32px' }}>
            <h3 style={{ marginBottom: '16px' }}>Positions</h3>
            <table className="data-table">
                <thead>
                    <tr>
                        <th>INSTRUMENT</th>
                        <th>QTY</th>
                        <th>AVG. COST</th>
                        <th>LTP</th>
                        <th>P&L</th>
                        <th>CHG%</th>
                    </tr>
                </thead>
                <tbody>
                    {positions.length === 0 ? (
                        <tr><td colSpan="6" style={{ textAlign: 'center', padding: '24px' }} className="text-muted">No active positions</td></tr>
                    ) : (
                        positions.map(pos => {
                            const ltp = marketData[pos.symbol]?.ltp || 0;
                            const pnl = (ltp - pos.avg_price) * pos.quantity;
                            const pnlPct = pos.avg_price > 0 ? (pnl / (pos.avg_price * pos.quantity)) * 100 : 0;
                            const pnlClass = pnl >= 0 ? 'text-green' : 'text-red';
                            
                            if (pos.quantity === 0) return null;

                            return (
                                <tr key={pos.symbol}>
                                    <td>{pos.symbol}</td>
                                    <td>{pos.quantity}</td>
                                    <td>{formatPrice(pos.avg_price)}</td>
                                    <td>{formatPrice(ltp)}</td>
                                    <td className={pnlClass}>{formatPrice(pnl)}</td>
                                    <td className={pnlClass}>{pnlPct.toFixed(2)}%</td>
                                </tr>
                            );
                        })
                    )}
                </tbody>
            </table>
        </div>
    );
};

export default Positions;
