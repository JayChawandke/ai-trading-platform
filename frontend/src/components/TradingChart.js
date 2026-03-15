
import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, CandlestickSeries, CrosshairMode } from 'lightweight-charts';

const TradingChart = ({ data, symbol, latestPrice }) => {
    const chartContainerRef = useRef();
    const chartRef = useRef();
    const seriesRef = useRef();

    useEffect(() => {
        if (!data || data.length === 0) return;

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: 'transparent' },
                textColor: '#94a3b8',
                fontSize: 11,
            },
            grid: {
                vertLines: { color: 'rgba(51, 65, 85, 0.5)' },
                horzLines: { color: 'rgba(51, 65, 85, 0.5)' },
            },
            crosshair: {
                mode: CrosshairMode.Normal,
                vertLine: { labelBackgroundColor: '#1e293b' },
                horzLine: { labelBackgroundColor: '#1e293b' },
            },
            rightPriceScale: {
                borderColor: 'rgba(51, 65, 85, 0.5)',
                autoScale: true,
            },
            timeScale: {
                borderColor: 'rgba(51, 65, 85, 0.5)',
                timeVisible: true,
                secondsVisible: false,
            },
            handleScroll: true,
            handleScale: true,
        });

        const candlestickSeries = chart.addSeries(CandlestickSeries, {
            upColor: '#22c55e',
            downColor: '#f43f5e',
            borderVisible: false,
            wickUpColor: '#22c55e',
            wickDownColor: '#f43f5e',
        });

        candlestickSeries.setData(data);
        chart.timeScale().fitContent();
        
        chartRef.current = chart;
        seriesRef.current = candlestickSeries;

        const handleResize = () => {
            if (chartContainerRef.current && chartRef.current) {
                chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, [data]);

    // Update with real-time price if available
    useEffect(() => {
        if (latestPrice && seriesRef.current) {
            const lastPoint = data[data.length - 1];
            if (lastPoint) {
                seriesRef.current.update({
                    time: lastPoint.time,
                    open: lastPoint.open,
                    high: Math.max(lastPoint.high, latestPrice),
                    low: Math.min(lastPoint.low, latestPrice),
                    close: latestPrice,
                });
            }
        }
    }, [latestPrice]);

    return (
        <div style={{ position: 'relative', width: '100%', height: '400px', minHeight: '300px' }}>
            <div ref={chartContainerRef} style={{ width: '100%', height: '100%' }} />
        </div>
    );
};

export default TradingChart;
