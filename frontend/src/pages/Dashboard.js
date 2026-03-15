import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import TradingChart from "../components/TradingChart";
import OrderModal from "../components/OrderModal";
import Positions from "../components/Positions";

const SCFG = {
  STRONG_BUY: { label: "STRONG BUY", color: "#00ff88", bg: "rgba(0,255,136,0.10)", bdr: "rgba(0,255,136,0.32)" },
  BUY:        { label: "BUY",         color: "#4ade80", bg: "rgba(74,222,128,0.09)", bdr: "rgba(74,222,128,0.28)" },
  HOLD:       { label: "HOLD",        color: "#fbbf24", bg: "rgba(251,191,36,0.09)", bdr: "rgba(251,191,36,0.28)" },
  WAIT:       { label: "WAIT",        color: "#94a3b8", bg: "rgba(148,163,184,0.07)", bdr: "rgba(148,163,184,0.18)" },
  SELL:       { label: "SELL",        color: "#f87171", bg: "rgba(248,113,113,0.10)", bdr: "rgba(248,113,113,0.32)" },
};

const APP_CONFIG = {
  BACKEND_URL: process.env.REACT_APP_BACKEND_URL || "http://localhost:8000",
  ML_SERVICE_URL: process.env.REACT_APP_ML_SERVICE_URL || "http://localhost:8001"
};

function timeAgo(iso) {
  if (!iso) return "---";
  const d = Math.floor((Date.now() - new Date(iso)) / 60000);
  if (d < 1) return "just now";
  if (d < 60) return `${d}m ago`;
  return `${Math.floor(d/60)}h ago`;
}

const getCurrency = (sym) => {
  const s = (sym || "").toUpperCase();
  const usSymbols = ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "AMD", "NFLX", "BA", "DIS", "PYPL", "INTC", "SPY", "QQQ"];
  if (s.startsWith("^") || usSymbols.includes(s)) return "$";
  return "₹";
};

const getPriceData = (m) => ({
  price: m?.ltp || 0,
  change: m?.chg_pct || 0,
  cur: getCurrency(m?.symbol)
});

const Bar = ({ label, score, verdict }) => (
  <div style={{ marginBottom: '15px' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px', fontSize: '0.85rem' }}>
      <span style={{ color: '#94a3b8' }}>{label}</span>
      <span style={{ color: verdict === 'Bullish' || verdict === 'Oversold' || verdict === 'Strong Buy' ? '#22c55e' : verdict === 'Neutral' ? '#fbbf24' : '#f43f5e', fontWeight: '600' }}>
        {verdict}
      </span>
    </div>
    <div style={{ height: '6px', background: '#334155', borderRadius: '3px', overflow: 'hidden' }}>
      <div style={{ 
        width: `${Math.min(Math.abs(score) * 100, 100)}%`, 
        height: '100%', 
        background: verdict === 'Bullish' || verdict === 'Oversold' || score > 0 ? '#22c55e' : '#f43f5e',
        transition: 'width 0.5s ease'
      }} />
    </div>
  </div>
);

function SCard({ s, mData, onSel, isSel, aiSignal }) {
  const pData = getPriceData(mData);
  const isUp = aiSignal?.prediction === "BUY";
  const isHold = aiSignal?.prediction === "HOLD";
  const headline = aiSignal?.headline || (isHold ? "WAITING" :  aiSignal?.prediction || "---");
  const priceColor = pData.change >= 0 ? '#22c55e' : '#ef4444';

  return (
    <div onClick={() => onSel(s)} className={`signal-card ${isSel ? 'selected' : ''}`} style={{
      padding: '16px',
      background: isSel ? '#1e293b' : 'rgba(30, 41, 59, 0.4)',
      borderBottom: '1px solid #334155',
      cursor: 'pointer',
      transition: 'all 0.2s',
      borderRadius: '8px',
      marginBottom: '8px',
      borderLeft: isSel ? `4px solid ${isHold ? '#94a3b8' : isUp ? '#22c55e' : '#ef4444'}` : '4px solid transparent'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
        <span style={{ fontWeight: '700', fontSize: '1.1rem', color: '#f1f5f9' }}>{s.symbol}</span>
        <span style={{ fontWeight: '600', color: priceColor }}>
          {pData.cur}{pData.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}
        </span>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ 
            width: '8px', height: '8px', borderRadius: '50%',
            background: isHold ? '#94a3b8' : isUp ? '#22c55e' : '#ef4444'
          }} />
          <span style={{ 
            fontSize: '0.8rem', fontWeight: '700', 
            color: isHold ? '#94a3b8' : isUp ? '#22c55e' : '#ef4444',
            textTransform: 'uppercase', letterSpacing: '0.5px'
          }}>
            {headline}
          </span>
        </div>
        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
          {aiSignal?.confidence ? `AI ${aiSignal.confidence}%` : '---'}
        </span>
      </div>
    </div>
  );
}

function Detail({ aiSignal, mData, chartData, onTrade, symbol, selectedRange, onRangeChange }) {
  const s = aiSignal || {};
  const isUp = s.prediction === "BUY";
  const isHold = s.prediction === "HOLD";
  const themeColor = isHold ? '#94a3b8' : isUp ? '#22c55e' : '#f43f5e';
  const pData = getPriceData(mData);

  return (
    <div className="detail-container" style={{ padding: '24px', height: '100%', overflowY: 'auto', background: '#0f172a' }}>
      <div className="detail-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '2.4rem', margin: 0, color: '#f1f5f9', display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            {symbol}
            <span style={{ 
              fontSize: '1rem', padding: '6px 16px', borderRadius: '20px', 
              background: `${themeColor}20`, color: themeColor, border: `1px solid ${themeColor}40`
            }}>
              {s.headline || "ANALYZING..."}
            </span>
          </h2>
          <p style={{ color: '#64748b', marginTop: '4px', fontSize: '1rem' }}>AI Neural Predictor · {s.horizon || '---'}</p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '2.4rem', fontWeight: '800', color: '#f1f5f9' }}>
            {pData.cur}{pData.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </div>
          <div style={{ color: pData.change >= 0 ? '#22c55e' : '#f43f5e', fontWeight: '600', fontSize: '1.1rem' }}>
            {pData.change >= 0 ? '▲' : '▼'} {Math.abs(pData.change).toFixed(2)}%
          </div>
        </div>
      </div>

      <div className="chart-wrapper" style={{ marginBottom: '32px', background: '#1e293b', borderRadius: '16px', padding: '16px', border: '1px solid #334155' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <span style={{ textTransform: 'uppercase', fontSize: '0.8rem', color: '#94a3b8', letterSpacing: '1px' }}>Market Chart</span>
          <div style={{ display: 'flex', gap: '8px' }}>
            {['1D', '5D', '1M', '1Y', '5Y'].map(r => (
               <button 
                 key={r} 
                 onClick={() => onRangeChange(r)}
                 style={{ 
                   background: selectedRange === r ? themeColor : '#334155', 
                   border: 'none', 
                   color: selectedRange === r ? '#000' : '#94a3b8', 
                   fontSize: '0.7rem', 
                   padding: '4px 10px', 
                   borderRadius: '4px', 
                   cursor: 'pointer',
                   fontWeight: selectedRange === r ? '700' : '500',
                   transition: 'all 0.2s'
                 }}
               >
                 {r}
               </button>
            ))}
          </div>
        </div>
        <TradingChart data={chartData} symbol={symbol} latestPrice={pData.price} />
      </div>

      <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '28px', marginBottom: '32px' }}>
        <div style={{ background: '#1e293b', padding: '24px', borderRadius: '16px', border: '1px solid #334155' }}>
          <h3 style={{ textTransform: 'uppercase', fontSize: '0.85rem', color: '#94a3b8', letterSpacing: '1.5px', marginBottom: '20px' }}>
            Why this {s.prediction || 'Hold'}?
          </h3>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {(s.why || ["Initializing analysis..."]).map((w, i) => (
              <li key={i} style={{ 
                color: '#cbd5e1', marginBottom: '14px', display: 'flex', gap: '12px', fontSize: '1.1rem',
                lineHeight: '1.5'
              }}>
                <span style={{ color: themeColor, fontWeight: '900' }}>•</span> {w}
              </li>
            ))}
          </ul>
          
          <div style={{ marginTop: '28px', paddingTop: '24px', borderTop: '1px solid #334155', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
             <div>
                <span style={{ color: '#64748b', fontSize: '0.8rem', display: 'block', fontWeight: '600' }}>RISK LEVEL</span>
                <span style={{ color: s.risk === 'High' ? '#f43f5e' : '#22c55e', fontWeight: '700', fontSize: '1.2rem' }}>{s.risk || '---'}</span>
             </div>
             <div>
                <span style={{ color: '#64748b', fontSize: '0.8rem', display: 'block', fontWeight: '600' }}>HORIZON</span>
                <span style={{ color: '#f1f5f9', fontWeight: '700', fontSize: '1.2rem' }}>{s.horizon || '---'}</span>
             </div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ background: `${themeColor}10`, padding: '24px', borderRadius: '16px', border: `1px solid ${themeColor}30` }}>
            <span style={{ color: themeColor, fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px' }}>Entry Zone</span>
            <div style={{ fontSize: '1.8rem', fontWeight: '800', color: '#f1f5f9', marginTop: '6px' }}>
              {pData.cur}{s.price_levels?.entry || '---'}
            </div>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div style={{ background: '#1e293b', padding: '20px', borderRadius: '16px', border: '1px solid #334155' }}>
              <span style={{ color: '#22c55e', fontSize: '0.8rem', fontWeight: '700' }}>TARGET</span>
              <div style={{ fontSize: '1.4rem', fontWeight: '800', color: '#f1f5f9', marginTop: '4px' }}>
                {pData.cur}{s.price_levels?.target || '---'}
              </div>
            </div>
            <div style={{ background: '#1e293b', padding: '20px', borderRadius: '16px', border: '1px solid #334155' }}>
              <span style={{ color: '#f43f5e', fontSize: '0.8rem', fontWeight: '700' }}>STOP LOSS</span>
              <div style={{ fontSize: '1.4rem', fontWeight: '800', color: '#f1f5f9', marginTop: '4px' }}>
                {pData.cur}{s.price_levels?.stop || '---'}
              </div>
            </div>
          </div>

          <button onClick={() => onTrade(symbol, s.prediction === "SELL" ? "SELL" : "BUY")} style={{
            width: '100%', padding: '20px', borderRadius: '16px', border: 'none',
            background: themeColor, color: '#000', fontWeight: '900', fontSize: '1.2rem',
            cursor: 'pointer', transition: 'all 0.2s', marginTop: '12px',
            boxShadow: `0 8px 16px ${themeColor}33`
          }}>
            EXECUTE {s.prediction === "SELL" ? "PUT" : "CALL"}
          </button>
        </div>
      </div>

      <div style={{ marginTop: '40px' }}>
        <h3 style={{ textTransform: 'uppercase', fontSize: '0.85rem', color: '#94a3b8', letterSpacing: '1.5px', marginBottom: '24px' }}>
          Signal Breakdown
        </h3>
        <div className="components-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '28px' }}>
          <Bar label="Trend Momentum" score={s.components?.lstm?.score || 0} verdict={s.components?.lstm?.verdict || 'Neutral'} />
          <Bar label="Value Zone" score={s.components?.rsi?.score || 0} verdict={s.components?.rsi?.verdict || 'Neutral'} />
          <Bar label="Volume Strength" score={s.components?.volume?.score || 0} verdict={s.components?.volume?.verdict || 'Neutral'} />
        </div>
      </div>
    </div>
  );
}

function LiveClock() {
  const [t,setT]=useState(new Date());
  useEffect(()=>{const id=setInterval(()=>setT(new Date()),1000);return()=>clearInterval(id);},[]);
  return <span style={{fontFamily:"monospace",fontSize:11,color:"#00ff88"}}>{t.toLocaleTimeString("en-IN",{timeZone:"Asia/Kolkata",hour:"2-digit",minute:"2-digit",second:"2-digit"})} IST</span>;
}

function TickerBar({items, mData}) {
  const [x,setX]=useState(0);
  const IW=185;
  useEffect(()=>{const id=setInterval(()=>setX(p=>p>=items.length*IW?0:p+0.55),18);return()=>clearInterval(id);},[items.length]);
  
  return (
    <div style={{overflow:"hidden",background:"rgba(15,23,42,0.95)",borderBottom:"1px solid rgba(255,255,255,0.05)",padding:"8px 0"}}>
      <div style={{display:"flex",transform:`translateX(-${x}px)`,transition:"transform 0.02s linear",whiteSpace:"nowrap"}}>
        {[...items,...items].map((m,i)=>(
          <div key={i} style={{display:"inline-flex",alignItems:"center",gap:8,padding:"0 20px",borderRight:"1px solid rgba(255,255,255,0.04)",minWidth:IW}}>
            <span style={{fontSize:10,fontWeight:700,color:"#94a3b8"}}>{m.symbol}</span>
            <span style={{fontSize:10,fontWeight:700,color:(mData[m.symbol]?.chg_pct || 0)>=0?"#22c55e":"#f43f5e"}}>
              {(mData[m.symbol]?.chg_pct || 0)>=0?"▲":"▼"} {Math.abs(mData[m.symbol]?.chg_pct || 0).toFixed(2)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [watchlist, setWatchlist] = useState([]);
  const [marketData, setMarketData] = useState({});
  const [mlSignals, setMlSignals] = useState({});
  const [selectedSymbol, setSelectedSymbol] = useState(null);
  const [selectedRange, setSelectedRange] = useState("1Y");
  const [chartData, setChartData] = useState([]);
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("signals");
  const [pulse, setPulse] = useState(false);
  const [orderModal, setOrderModal] = useState({ show: false, symbol: '', side: '', ltp: 0 });
  const [drawerOpen, setDrawerOpen] = useState(false);
  const wsRef = useRef(null);

  const rangeMap = {
    "1D": { p: "1d", i: "5m" },
    "5D": { p: "5d", i: "15m" },
    "1M": { p: "1mo", i: "1h" },
    "1Y": { p: "1y", i: "1d" },
    "5Y": { p: "5y", i: "1wk" }
  };

  const fetchPositions = async () => {
    try {
      const res = await axios.get(`${APP_CONFIG.BACKEND_URL}/trade/positions`);
      setPositions(res.data);
    } catch (err) { console.error(err); }
  };

  useEffect(() => {
    const fetchInitial = async () => {
      try {
        const [wRes, pRes] = await Promise.all([
          axios.get(`${APP_CONFIG.BACKEND_URL}/watchlist/`),
          axios.get(`${APP_CONFIG.BACKEND_URL}/trade/positions`)
        ]);
        setWatchlist(wRes.data);
        setPositions(pRes.data);
        if (wRes.data.length > 0) setSelectedSymbol(wRes.data[0].symbol);

        const sigMap = {};
        for(let item of wRes.data) {
            try {
                const sRes = await axios.get(`${APP_CONFIG.ML_SERVICE_URL}/predict/${item.symbol}`);
                sigMap[item.symbol] = sRes.data;
            } catch(e) {}
        }
        setMlSignals(sigMap);
      } catch (err) { console.error(err); } finally { setLoading(false); }
    };
    fetchInitial();
  }, []);

  useEffect(() => {
    if (!selectedSymbol) return;
    const fetchHistory = async () => {
        try {
            const { p, i } = rangeMap[selectedRange];
            const res = await axios.get(`${APP_CONFIG.BACKEND_URL}/market/history/${selectedSymbol}?period=${p}&interval=${i}`);
            setChartData(res.data);
        } catch(e) { console.error(e); }
    };
    fetchHistory();
  }, [selectedSymbol, selectedRange]);

  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket(`${APP_CONFIG.BACKEND_URL.replace("http", "ws")}/ws`);
      wsRef.current = ws;
      ws.onopen = () => console.log("WS Connected");
      ws.onmessage = (e) => {
          try {
              const data = JSON.parse(e.data);
              setMarketData(data);
              setPulse(true);
              setTimeout(()=>setPulse(false), 500);
          } catch(err) {}
      };
      ws.onclose = () => setTimeout(connect, 3000);
    };
    connect();
    return () => wsRef.current?.close();
  }, []);

  const handleTrade = (symbol, side) => {
    const ltp = marketData[symbol]?.ltp || 0;
    setOrderModal({ show: true, symbol, side, ltp });
  };

  useEffect(() => {
    if (!selectedSymbol) return;
    const fetchPrediction = async () => {
        try {
            setMlSignals(p => ({ ...p, [selectedSymbol]: { ...p[selectedSymbol], loading: true } }));
            const res = await axios.get(`${APP_CONFIG.ML_SERVICE_URL}/predict/${selectedSymbol}`);
            setMlSignals(p => ({ ...p, [selectedSymbol]: res.data }));
        } catch(e) {}
    };
    fetchPrediction();
  }, [selectedSymbol]);

  const sigState = mlSignals[selectedSymbol];
  const enrichedSignal = sigState && !sigState.loading ? sigState : { 
    prediction: "HOLD", 
    confidence: 0.50, 
    reason: `Syncing neural data for ${selectedSymbol}...` 
  };

  return (
    <div style={{minHeight:"100vh",background:"#050c1a",fontFamily:"'Inter',sans-serif",color:"#cbd5e1"}}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        *{box-sizing:border-box}
        
        .watchlist-drawer {
          position: fixed; top: 0; left: 0; bottom: 0; width: 320px;
          background: #0f172a; border-right: 1px solid #334155;
          z-index: 1000; transition: transform 0.3s ease;
          transform: translateX(-100%); padding: 20px;
        }
        .watchlist-drawer.open { transform: translateX(0); }
        .drawer-overlay {
          position: fixed; inset: 0; background: rgba(0,0,0,0.5);
          backdrop-filter: blur(4px); z-index: 999; display: none;
        }
        .drawer-overlay.open { display: block; }
        
        @media (min-width: 1025px) {
          .dashboard-grid { display: grid; grid-template-columns: 320px 1fr !important; gap: 20px; }
          .watchlist-drawer { position: static !important; transform: none !important; width: 100% !important; background: transparent !important; border: none !important; padding: 0 !important; }
          .drawer-overlay { display: none !important; }
          .menu-toggle { display: none !important; }
        }
        
        @media (max-width: 1024px) {
          .dashboard-grid { grid-template-columns: 1fr !important; }
          .detail-header { flex-direction: column; gap: 16px; }
          .detail-header > div:last-child { text-align: left !important; }
          .stats-grid { grid-template-columns: 1fr !important; }
          .components-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
      
      <TickerBar items={watchlist} mData={marketData}/>

      <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",padding:"14px 22px",background:"rgba(15,23,42,0.8)",backdropFilter:"blur(20px)",position:"sticky",top:0,zIndex:100,borderBottom:"1px solid rgba(255,255,255,0.05)"}}>
        <div style={{display:"flex",alignItems:"center",gap:16}}>
          <button className="menu-toggle" onClick={() => setDrawerOpen(true)} style={{ background: 'transparent', border: 'none', color: '#f1f5f9', fontSize: '1.5rem', cursor: 'pointer' }}>☰</button>
          <div style={{display:"flex",alignItems:"center",gap:10}}>
            <div style={{width:30,height:30,borderRadius:8,background:"linear-gradient(135deg,#0ea5e9,#00ff88)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:14,fontWeight:900,color:"#050c1a"}}>AI</div>
            <span style={{fontSize:16,fontWeight:800,color:"#f1f5f9"}}>Jay Intel</span>
          </div>
        </div>
        <div style={{display:"flex",alignItems:"center",gap:20}}>
            <div style={{display:"flex",gap:4,background:"rgba(255,255,255,0.03)",padding:4,borderRadius:8}}>
              {["signals","portfolio"].map(t=>(
                <button key={t} onClick={()=>setTab(t)} style={{background:tab===t?"#1e293b":"transparent",border:"none",color:tab===t?"#38bdf8":"#64748b",fontSize:13,fontWeight:600,padding:"6px 16px",borderRadius:6,cursor:"pointer",textTransform:"capitalize"}}>{t}</button>
              ))}
            </div>
            <div style={{display:"flex",alignItems:"center",gap:6}}>
              <div style={{width:8,height:8,borderRadius:"50%",background:pulse?"#00ff88":"#166534",transition:"all 0.4s"}}/>
              <LiveClock/>
            </div>
        </div>
      </div>

      <div className={`drawer-overlay ${drawerOpen ? 'open' : ''}`} onClick={() => setDrawerOpen(false)} />
      
      <div style={{padding:"20px",maxWidth:1600,margin:"0 auto"}}>
        {tab === "signals" && (
            <div className="dashboard-grid">
                <div className={`watchlist-drawer ${drawerOpen ? 'open' : ''}`}>
                    <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'20px'}} className="menu-toggle">
                        <span style={{fontWeight:800, color:'#f1f5f9'}}>WATCHLIST</span>
                        <button onClick={() => setDrawerOpen(false)} style={{background:'transparent', border:'none', color:'#64748b', fontSize:'1.2rem'}}>✕</button>
                    </div>
                    <div style={{display:"flex",flexDirection:"column",gap:12}}>
                        {watchlist.map(s => (
                            <SCard key={s.symbol} s={s} aiSignal={mlSignals[s.symbol]} mData={marketData[s.symbol]} onSel={(item)=>{setSelectedSymbol(item.symbol); setDrawerOpen(false);}} isSel={selectedSymbol === s.symbol} />
                        ))}
                    </div>
                </div>
                <div>
                   {selectedSymbol && (
                       <Detail 
                         aiSignal={enrichedSignal} 
                         mData={marketData[selectedSymbol]} 
                         chartData={chartData} 
                         onTrade={(side) => handleTrade(selectedSymbol, side)} 
                         symbol={selectedSymbol}
                         selectedRange={selectedRange}
                         onRangeChange={setSelectedRange}
                       />
                   )}
                </div>
            </div>
        )}

        {tab === "portfolio" && <Positions positions={positions} marketData={marketData} />}

        {orderModal.show && (
            <OrderModal symbol={orderModal.symbol} side={orderModal.side} ltp={orderModal.ltp} onClose={() => setOrderModal({ ...orderModal, show: false })} onOrderSuccess={fetchPositions} />
        )}
      </div>
    </div>
  );
}
