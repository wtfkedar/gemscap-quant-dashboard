import asyncio
import json
import websockets
from datetime import datetime
from storage import insert_tick
from config import WEBSOCKET_TIMEOUT, WEBSOCKET_PING_INTERVAL, MAX_RETRIES

_running = False
_tasks = []

async def _listen_symbol(symbol):
    url = f"wss://fstream.binance.com/ws/{symbol}@trade"
    retry_count = 0
    max_retries = MAX_RETRIES
    ws = None
    
    print(f"[{symbol}] Starting WebSocket connection...")
    
    try:
        while _running and retry_count < max_retries:
            try:
                async with websockets.connect(url, ping_interval=WEBSOCKET_PING_INTERVAL, ping_timeout=10) as ws:
                    print(f"[{symbol}] ✅ Connected successfully!")
                    retry_count = 0
                    tick_count = 0
                    
                    while _running:
                        try:
                            msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                            data = json.loads(msg)
                            ts = datetime.utcfromtimestamp(data["T"] / 1000).isoformat()
                            insert_tick(ts, symbol, float(data["p"]), float(data["q"]))
                            tick_count += 1
                            
                            if tick_count % 10 == 0:
                                print(f"[{symbol}] Received {tick_count} ticks")
                                
                        except asyncio.TimeoutError:
                            # Check if still running, if not break
                            if not _running:
                                print(f"[{symbol}] Stop signal received")
                                break
                            continue
                        except asyncio.CancelledError:
                            print(f"[{symbol}] Task cancelled")
                            break
                        except Exception as e:
                            print(f"[{symbol}] ❌ Error receiving data: {e}")
                            break
                    
                    # Break out of retry loop if stopped
                    if not _running:
                        break
                            
            except asyncio.CancelledError:
                print(f"[{symbol}] Connection cancelled")
                break
            except Exception as e:
                retry_count += 1
                print(f"[{symbol}] ❌ Connection error (attempt {retry_count}/{max_retries}): {e}")
                if _running and retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    print(f"[{symbol}] Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
    except asyncio.CancelledError:
        print(f"[{symbol}] Task cancelled during execution")
    finally:
        print(f"[{symbol}] Stream ended")

async def start_stream(symbols):
    global _running, _tasks
    _running = True
    print(f"🚀 Starting stream for symbols: {symbols}")
    try:
        _tasks = [asyncio.create_task(_listen_symbol(s)) for s in symbols]
        await asyncio.gather(*_tasks, return_exceptions=True)
    except Exception as e:
        print(f"❌ Stream error: {e}")
    finally:
        print("Stream tasks completed")
        _tasks = []

def stop_stream():
    global _running, _tasks
    print("🛑 Stopping stream...")
    _running = False
    
    # Cancel all running tasks
    for task in _tasks:
        if not task.done():
            task.cancel()
    
    print("✅ All tasks cancelled")
