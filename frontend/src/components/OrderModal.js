
import React, { useState } from 'react';
import axios from 'axios';

const OrderModal = ({ symbol, side, ltp, onClose, onOrderSuccess }) => {
    const [quantity, setQuantity] = useState(1);
    const [price, setPrice] = useState(ltp || 0);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await axios.post('http://localhost:8000/trade/order', {
                symbol,
                side,
                quantity: parseFloat(quantity),
                price: parseFloat(price)
            });
            onOrderSuccess();
            onClose();
        } catch (err) {
            console.error("Order error:", err);
            alert("Failed to place order");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay" style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', 
            alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
            <div className="modal-content" style={{
                backgroundColor: '#1e2329', padding: '24px', borderRadius: '4px',
                width: '320px', border: '1px solid #2b3139'
            }}>
                <h3 style={{ margin: '0 0 16px', color: side === 'BUY' ? '#0ECB81' : '#F6465D' }}>
                    {side} {symbol}
                </h3>
                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '16px' }}>
                        <label style={{ display: 'block', marginBottom: '4px', fontSize: '11px', color: '#848E9C' }}>QUANTITY</label>
                        <input 
                            type="number" 
                            step="0.01"
                            value={quantity} 
                            onChange={(e) => setQuantity(e.target.value)}
                            style={{ width: '100%', padding: '8px', backgroundColor: '#0b0e11', border: '1px solid #2b3139', color: '#fff' }}
                        />
                    </div>
                    <div style={{ marginBottom: '24px' }}>
                        <label style={{ display: 'block', marginBottom: '4px', fontSize: '11px', color: '#848E9C' }}>PRICE (LTP: {ltp})</label>
                        <input 
                            type="number" 
                            step="0.01"
                            value={price} 
                            onChange={(e) => setPrice(e.target.value)}
                            style={{ width: '100%', padding: '8px', backgroundColor: '#0b0e11', border: '1px solid #2b3139', color: '#fff' }}
                        />
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <button 
                            type="button" 
                            onClick={onClose}
                            style={{ flex: 1, padding: '10px', backgroundColor: 'transparent', border: '1px solid #2b3139', color: '#fff', cursor: 'pointer' }}
                        >
                            Cancel
                        </button>
                        <button 
                            type="submit" 
                            disabled={loading}
                            style={{ 
                                flex: 1, padding: '10px', 
                                backgroundColor: side === 'BUY' ? '#0ECB81' : '#F6465D', 
                                border: 'none', color: '#fff', fontWeight: 'bold', cursor: 'pointer' 
                            }}
                        >
                            {loading ? '...' : side}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default OrderModal;
