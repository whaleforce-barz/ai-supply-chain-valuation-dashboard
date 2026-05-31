# AI Data Center 供應鏈估值風險初篩

- 產出日期：2026-05-31
- Frozen universe：157 檔，來源為 `ai_supply_chain_stock_pool.md`，未因價格表現新增或移除標的。
- 市場資料來源：[Yahoo Finance](https://finance.yahoo.com/) via [yfinance](https://pypi.org/project/yfinance/)；不同交易所 ticker 可能有延遲、幣別差異或缺漏。
- 判讀性質：估值過熱/合理性初篩，不是買賣建議；缺少 forward estimate、mid-cycle EPS、backlog 或 capex 後 FCF 的標的保留為資料不足或需覆核。

## 標籤分布

| 估值標籤 | 檔數 |
| --- | ---: |
| 未充分反映 | 5 |
| 合理反映 | 59 |
| 偏熱 | 32 |
| 過熱 | 35 |
| 極度過熱 / priced for perfection | 7 |
| 資料不足 | 19 |

## 分類覆蓋

| 類型 | 檔數 |
| --- | ---: |
| 8. L4 Data Center 電力 / 散熱 / 配電 | 20 |
| 4. L3 半導體設備 / EDA / 測試 | 18 |
| 12. L5 原材料 / 工業氣體 / 電纜 | 17 |
| 1. L1 需求端 / AI 雲端 / Data Center | 15 |
| 5. L3 先進封裝 / ABF / PCB / CCL | 15 |
| 11. L5 電力供應 / 公用事業 / 核能 | 12 |
| 2. L2 AI 晶片 / ASIC / CPU / 電源 IC | 12 |
| 6. L2/L3 AI Server / ODM / Rack | 12 |
| 3. L3 半導體製造 / 記憶體 | 11 |
| 7. L2/L3 Networking / 光通訊 | 10 |
| 9. L4 EPC / 建設 / 機電工程 | 8 |
| 10. L5 備援電力 / 微電網 / 燃料電池 | 7 |

## 高風險 / 已反映較多

| Ticker | 公司 | 類型 | 價格 | 市值 | PE/Fwd PE | EV/EBITDA | PS | 營收成長 | 標籤 | 判讀 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 8035.T | Tokyo Electron | 4. L3 半導體設備 / EDA / 測試 | 52420.00 JPY | 23.9T | 40.9 | 33.0 | 9.8 | 8.6% | 偏熱 | PE > 30x 已反映明顯 AI / 製程升級期待 |
| LRCX | Lam Research | 4. L3 半導體設備 / EDA / 測試 | 318.18 USD | 397.9B | 40.1 | 50.6 | 18.4 | 23.8% | 偏熱 | PE > 30x 已反映明顯 AI / 製程升級期待 |
| CDNS | Cadence | 4. L3 半導體設備 / EDA / 測試 | 374.93 USD | 103.4B | 39.9 | 52.1 | 18.7 | 18.7% | 偏熱 | PE > 30x 已反映明顯 AI / 製程升級期待 |
| TER | Teradyne | 4. L3 半導體設備 / EDA / 測試 | 374.31 USD | 58.6B | 39.3 | 50.3 | 15.5 | 87.0% | 偏熱 | PE > 30x 已反映明顯 AI / 製程升級期待 |
| KLAC | KLA | 4. L3 半導體設備 / EDA / 測試 | 1921.71 USD | 251.0B | 38.5 | 43.1 | 19.2 | 11.5% | 偏熱 | PE > 30x 已反映明顯 AI / 製程升級期待 |
| VIAV | Viavi | 7. L2/L3 Networking / 光通訊 | 48.56 USD | 12.0B | 37.9 | 54.9 | 8.8 | 42.8% | 偏熱 | 虧損但營收倍數已不低，需要毛利與現金流改善 |
| FN | Fabrinet | 7. L2/L3 Networking / 光通訊 | 654.16 USD | 23.4B | 37.9 | 46.9 | 5.5 | 39.3% | 偏熱 | 估值已反映 AI data center 需求擴張 |
| VRT | Vertiv | 8. L4 Data Center 電力 / 散熱 / 配電 | 315.71 USD | 121.3B | 35.7 | 51.2 | 11.2 | 30.1% | 偏熱 | 估值已反映 AI data center 需求擴張 |
| ASML | ASML | 4. L3 半導體設備 / EDA / 測試 | 1612.76 USD | 621.6B | 33.8 | 48.5 | 18.4 | 13.2% | 偏熱 | PE > 30x 已反映明顯 AI / 製程升級期待 |
| MRVL | Marvell | 2. L2 AI 晶片 / ASIC / CPU / 電源 IC | 205.00 USD | 179.3B | 33.7 | 66.7 | 20.6 | 27.6% | 偏熱 | PE > 30x 已反映明顯 AI / 製程升級期待 |
| ASM.AS | ASM International | 4. L3 半導體設備 / EDA / 測試 | 898.40 EUR | 43.9B | 33.3 | 39.4 | 13.7 | 2.8% | 偏熱 | PE > 30x 已反映明顯 AI / 製程升級期待 |
| TXN | Texas Instruments | 2. L2 AI 晶片 / ASIC / CPU / 電源 IC | 305.68 USD | 278.2B | 32.5 | 33.1 | 15.1 | 18.6% | 偏熱 | PE > 30x 已反映明顯 AI / 製程升級期待 |
| ABBN.SW | ABB | 8. L4 Data Center 電力 / 散熱 / 配電 | 83.62 CHF | 151.8B | 31.4 | 22.2 | 4.4 | 18.3% | 偏熱 | 估值已反映 AI data center 需求擴張 |
| ROK | Rockwell Automation | 8. L4 Data Center 電力 / 散熱 / 配電 | 451.06 USD | 50.2B | 31.1 | 27.4 | 5.7 | 11.9% | 偏熱 | 估值已反映 AI data center 需求擴張 |
| NOK | Nokia | 7. L2/L3 Networking / 光通訊 | 14.84 USD | 82.8B | 30.4 | 31.8 | 4.1 | 2.4% | 偏熱 | 估值已反映 AI data center 需求擴張 |
| ENTG | Entegris | 4. L3 半導體設備 / EDA / 測試 | 138.79 USD | 21.1B | 30.0 | 27.8 | 6.5 | 5.0% | 偏熱 | PE > 30x 已反映明顯 AI / 製程升級期待 |
| CAT | Caterpillar | 10. L5 備援電力 / 微電網 / 燃料電池 | 875.87 USD | 403.4B | 29.4 | 30.4 | 5.7 | 22.2% | 偏熱 | 估值已反映 AI data center 需求擴張 |
| SCCO | Southern Copper | 12. L5 原材料 / 工業氣體 / 電纜 | 191.30 USD | 159.6B | 29.1 | 18.3 | 11.0 | 36.2% | 偏熱 | 材料股 EV/EBITDA 偏高，需要 commodity spread 支持 |
| PRY.MI | Prysmian | 12. L5 原材料 / 工業氣體 / 電纜 | 148.00 EUR | 43.3B | 25.9 | 18.5 | 2.1 | 10.1% | 偏熱 | 材料股 EV/EBITDA 偏高，需要 commodity spread 支持 |
| NKT.CO | NKT | 12. L5 原材料 / 工業氣體 / 電纜 | 1025.00 DKK | 54.8B | 25.6 | 77.9 | 15.3 | 3.2% | 偏熱 | 材料股 EV/EBITDA 偏高，需要 commodity spread 支持 |
| LIN | Linde | 12. L5 原材料 / 工業氣體 / 電纜 | 497.69 USD | 230.1B | 25.3 | 18.7 | 6.6 | 8.2% | 偏熱 | 材料股 EV/EBITDA 偏高，需要 commodity spread 支持 |
| AI.PA | Air Liquide | 12. L5 原材料 / 工業氣體 / 電纜 | 178.08 EUR | 102.8B | 22.9 | 15.1 | 3.8 | -3.4% | 偏熱 | 材料股 EV/EBITDA 偏高，需要 commodity spread 支持 |
| DELL | Dell | 6. L2/L3 AI Server / ODM / Rack | 420.91 USD | 273.4B | 21.2 | 21.0 | 2.0 | 87.5% | 偏熱 | EV/EBITDA 偏高，需要訂單與現金轉換支持 |
| APD | Air Products | 12. L5 原材料 / 工業氣體 / 電纜 | 278.62 USD | 62.0B | 19.6 | 21.2 | 5.0 | 8.8% | 偏熱 | 材料股 EV/EBITDA 偏高，需要 commodity spread 支持 |
| FCX | Freeport-McMoRan | 12. L5 原材料 / 工業氣體 / 電纜 | 65.71 USD | 94.5B | 17.6 | 11.6 | 3.6 | 8.8% | 偏熱 | P/B 偏高，需要高 ROIC 或供給緊缺支持 |
| 6723.T | Renesas | 3. L3 半導體製造 / 記憶體 | 4500.00 JPY | 8.2T | 17.5 | 24.5 | 5.9 | 23.2% | 偏熱 | 虧損但營收倍數已不低，需要毛利與現金流改善 |
| BHP | BHP | 12. L5 原材料 / 工業氣體 / 電纜 | 88.91 USD | 225.9B | 16.7 | 18.0 | 4.2 | 10.8% | 偏熱 | 材料股 EV/EBITDA 偏高，需要 commodity spread 支持 |
| STLD | Steel Dynamics | 12. L5 原材料 / 工業氣體 / 電纜 | 260.15 USD | 37.5B | 15.3 | 17.8 | 2.0 | 19.1% | 偏熱 | 材料股 EV/EBITDA 偏高，需要 commodity spread 支持 |
| SMCI | Super Micro | 6. L2/L3 AI Server / ODM / Rack | 46.09 USD | 27.7B | 14.3 | 22.5 | 0.8 | 122.7% | 偏熱 | EV/EBITDA 偏高，需要訂單與現金轉換支持 |
| FCEL | FuelCell Energy | 10. L5 備援電力 / 微電網 / 燃料電池 | 21.66 USD | 1.1B | -11.9 | -14.0 | 6.8 | 60.7% | 偏熱 | 虧損但營收倍數已不低，需要毛利與現金流改善 |
| PLUG | Plug Power | 10. L5 備援電力 / 微電網 / 燃料電池 | 3.95 USD | 5.5B | -24.0 | -10.3 | 7.4 | 22.3% | 偏熱 | 虧損但營收倍數已不低，需要毛利與現金流改善 |
| CRWV | CoreWeave | 1. L1 需求端 / AI 雲端 / Data Center | 109.53 USD | 59.8B | -174.7 | 30.6 | 9.6 | 111.6% | 偏熱 | 虧損但營收倍數已不低，需要毛利與現金流改善 |
| NBIS | Nebius | 1. L1 需求端 / AI 雲端 / Data Center | 231.09 USD | 58.7B | 639.7 | -1538.9 | 66.8 | 683.9% | 過熱 | 平台型公司 PE > 55x，需要 AI monetization 明確加速 |
| ARM | Arm | 2. L2 AI 晶片 / ASIC / CPU / 電源 IC | 353.29 USD | 377.3B | 115.6 | 351.5 | 76.7 | 20.1% | 過熱 | EV/EBITDA > 80x，估值需多年高成長與高 margin 同時支撐 |
| CORZ | Core Scientific | 1. L1 需求端 / AI 雲端 / Data Center | 26.85 USD | 8.5B | 85.2 | -100.1 | 24.1 | 44.9% | 過熱 | 平台型公司 PE > 55x，需要 AI monetization 明確加速 |
| ALAB | Astera Labs | 2. L2 AI 晶片 / ASIC / CPU / 電源 IC | 342.85 USD | 58.8B | 81.5 | 246.9 | 58.7 | 93.4% | 過熱 | EV/EBITDA > 80x，估值需多年高成長與高 margin 同時支撐 |
| INTC | Intel | 2. L2 AI 晶片 / ASIC / CPU / 電源 IC | 114.68 USD | 576.4B | 74.5 | 42.5 | 10.7 | 7.2% | 過熱 | 虧損且 PS > 10x，估值仰賴明確轉盈路徑 |
| 4062.T | Ibiden | 5. L3 先進封裝 / ABF / PCB / CCL | 23000.00 JPY | 6.4T | 74.4 | 50.9 | 15.4 | 18.6% | 過熱 | 資本密集模式 EV/EBITDA > 25x，需要高利用率多年維持 |
| CIEN | Ciena | 7. L2/L3 Networking / 光通訊 | 580.23 USD | 82.0B | 66.4 | 144.3 | 16.0 | 33.1% | 過熱 | EV/EBITDA > 80x，需訂單、毛利與現金流快速追上估值 |
| DLR | Digital Realty | 1. L1 需求端 / AI 雲端 / Data Center | 190.00 USD | 68.0B | 66.3 | 29.9 | 10.8 | 16.7% | 過熱 | 平台型公司 PE > 55x，需要 AI monetization 明確加速 |
| BE | Bloom Energy | 10. L5 備援電力 / 微電網 / 燃料電池 | 285.00 USD | 81.1B | 65.5 | 352.1 | 33.1 | 130.4% | 過熱 | EV/EBITDA > 80x，需訂單、毛利與現金流快速追上估值 |
| 0981.HK | SMIC | 3. L3 半導體製造 / 記憶體 | 81.60 HKD | 653.9B | 59.4 | 106.1 | 68.2 | 11.5% | 過熱 | 資本密集模式 EV/EBITDA > 25x，需要高利用率多年維持 |
| EQIX | Equinix | 1. L1 需求端 / AI 雲端 / Data Center | 1068.04 USD | 105.3B | 55.6 | 29.7 | 11.1 | 12.1% | 過熱 | 平台型公司 PE > 55x，需要 AI monetization 明確加速 |
| MTSI | MACOM | 7. L2/L3 Networking / 光通訊 | 364.64 USD | 27.8B | 53.3 | 117.3 | 25.9 | 22.5% | 過熱 | EV/EBITDA > 80x，需訂單、毛利與現金流快速追上估值 |
| MPWR | Monolithic Power | 2. L2 AI 晶片 / ASIC / CPU / 電源 IC | 1566.21 USD | 76.9B | 51.9 | 88.2 | 26.0 | 26.1% | 過熱 | EV/EBITDA > 80x，估值需多年高成長與高 margin 同時支撐 |
| 6146.T | Disco | 4. L3 半導體設備 / EDA / 測試 | 65090.00 JPY | 7.1T | 47.8 | 34.1 | 16.2 |  | 過熱 | PE > 45x，需 backlog、ASP、毛利率持續兌現 |
| LITE | Lumentum | 7. L2/L3 Networking / 光通訊 | 854.96 USD | 66.5B | 47.2 | 120.8 | 26.7 | 90.1% | 過熱 | EV/EBITDA > 80x，需訂單、毛利與現金流快速追上估值 |
| COHR | Coherent | 7. L2/L3 Networking / 光通訊 | 361.47 USD | 70.7B | 44.6 | 54.9 | 10.7 | 20.5% | 過熱 | PE > 38x，若訂單或 margin 放緩容易壓縮 |
| PWR | Quanta Services | 9. L4 EPC / 建設 / 機電工程 | 711.73 USD | 106.8B | 43.3 | 42.4 | 3.5 | 26.3% | 過熱 | PE > 60x，需要高成長兌現 |
| AAON | AAON | 8. L4 Data Center 電力 / 散熱 / 配電 | 140.20 USD | 11.5B | 42.6 | 47.5 | 7.1 | 54.3% | 過熱 | PE > 38x，若訂單或 margin 放緩容易壓縮 |
| AMD | AMD | 2. L2 AI 晶片 / ASIC / CPU / 電源 IC | 516.10 USD | 841.6B | 39.8 | 112.1 | 22.5 | 37.8% | 過熱 | EV/EBITDA > 80x，估值需多年高成長與高 margin 同時支撐 |
| GEV | GE Vernova | 8. L4 Data Center 電力 / 散熱 / 配電 | 968.32 USD | 260.2B | 39.5 | 74.8 | 6.6 | 16.3% | 過熱 | PE > 38x，若訂單或 margin 放緩容易壓縮 |
| ANET | Arista | 7. L2/L3 Networking / 光通訊 | 159.47 USD | 200.8B | 35.8 | 44.5 | 20.7 | 35.1% | 過熱 | PS > 20x，元件/光通訊估值已高度反映 AI 需求 |
| 3037.TW | 欣興 | 5. L3 先進封裝 / ABF / PCB / CCL | 1055.00 TWD | 1.7T | 35.8 | 63.0 | 12.0 | 24.5% | 過熱 | 資本密集模式 EV/EBITDA > 25x，需要高利用率多年維持 |
| 3189.TW | 景碩 | 5. L3 先進封裝 / ABF / PCB / CCL | 729.00 TWD | 384.1B | 35.5 | 38.4 | 9.2 | 28.8% | 過熱 | 資本密集模式 EV/EBITDA > 25x，需要高利用率多年維持 |
| STX | Seagate | 3. L3 半導體製造 / 記憶體 | 879.80 USD | 199.1B | 33.3 | 57.0 | 18.1 | 44.1% | 過熱 | 資本密集模式 EV/EBITDA > 25x，需要高利用率多年維持 |
| 2383.TW | 台光電 | 5. L3 先進封裝 / ABF / PCB / CCL | 5120.00 TWD | 1.8T | 32.9 | 78.0 | 17.4 | 52.5% | 過熱 | 資本密集模式 EV/EBITDA > 25x，需要高利用率多年維持 |
| MTZ | MasTec | 9. L4 EPC / 建設 / 機電工程 | 378.37 USD | 29.9B | 32.3 | 26.9 | 2.0 | 34.5% | 過熱 | PE > 60x，需要高成長兌現 |
| TTMI | TTM Technologies | 5. L3 先進封裝 / ABF / PCB / CCL | 173.72 USD | 18.0B | 32.2 | 42.6 | 5.8 | 30.4% | 過熱 | 資本密集模式 EV/EBITDA > 25x，需要高利用率多年維持 |
| 8046.TW | 南電 | 5. L3 先進封裝 / ABF / PCB / CCL | 848.00 TWD | 547.9B | 30.3 | 53.7 | 12.8 | 32.1% | 過熱 | 資本密集模式 EV/EBITDA > 25x，需要高利用率多年維持 |

## 合理或可能未充分反映

| Ticker | 公司 | 類型 | 價格 | 市值 | PE/Fwd PE | EV/EBITDA | PS | 營收成長 | 標籤 | 判讀 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| EXC | Exelon | 11. L5 電力供應 / 公用事業 / 核能 | 45.64 USD | 46.7B | 15.0 | 11.8 | 1.9 | 7.9% | 未充分反映 | 公用事業估值偏低，若負載成長兌現有重評空間 |
| NRG | NRG Energy | 11. L5 電力供應 / 公用事業 / 核能 | 134.08 USD | 28.3B | 11.5 | 23.1 | 0.9 | 19.5% | 未充分反映 | 公用事業估值偏低，若負載成長兌現有重評空間 |
| VST | Vistra | 11. L5 電力供應 / 公用事業 / 核能 | 160.23 USD | 54.0B | 14.6 | 11.2 | 2.8 | 43.4% | 未充分反映 | 公用事業估值偏低，若負載成長兌現有重評空間 |
| 7735.T | SCREEN | 4. L3 半導體設備 / EDA / 測試 | 11120.00 JPY | 2.1T | 12.7 | 13.7 | 3.5 | 9.1% | 未充分反映 | 估值低於高品質設備股常態且仍有成長 |
| RRX | Regal Rexnord | 8. L4 Data Center 電力 / 散熱 / 配電 | 201.76 USD | 13.4B | 14.9 | 14.9 | 2.2 | 4.3% | 未充分反映 | 估值低且成長仍正，可能未完全反映 AI 需求 |
| AMZN | Amazon | 1. L1 需求端 / AI 雲端 / Data Center | 270.64 USD | 2.9T | 27.4 | 19.3 | 3.9 | 16.6% | 合理反映 | 大型平台估值未單靠 AI 題材脫離基本面 |
| GOOGL | Alphabet | 1. L1 需求端 / AI 雲端 / Data Center | 380.34 USD | 4.6T | 26.2 | 28.4 | 10.9 | 21.8% | 合理反映 | 大型平台估值未單靠 AI 題材脫離基本面 |
| IBM | IBM | 1. L1 需求端 / AI 雲端 / Data Center | 297.80 USD | 279.9B | 22.1 | 20.3 | 4.1 | 9.5% | 合理反映 | 大型平台估值未單靠 AI 題材脫離基本面 |
| META | Meta | 1. L1 需求端 / AI 雲端 / Data Center | 632.51 USD | 1.6T | 17.5 | 14.7 | 7.5 | 33.1% | 合理反映 | 大型平台估值未單靠 AI 題材脫離基本面 |
| MSFT | Microsoft | 1. L1 需求端 / AI 雲端 / Data Center | 450.24 USD | 3.3T | 23.3 | 18.4 | 10.5 | 18.3% | 合理反映 | 大型平台估值未單靠 AI 題材脫離基本面 |
| ORCL | Oracle | 1. L1 需求端 / AI 雲端 / Data Center | 225.78 USD | 649.4B | 28.1 | 28.3 | 10.1 | 21.7% | 合理反映 | 大型平台估值未單靠 AI 題材脫離基本面 |
| CMI | Cummins | 10. L5 備援電力 / 微電網 / 燃料電池 | 646.63 USD | 89.2B | 19.4 | 19.0 | 2.6 | 2.7% | 合理反映 | 估值與工業/元件成長股區間大致相符 |
| GNRC | Generac | 10. L5 備援電力 / 微電網 / 燃料電池 | 277.91 USD | 16.4B | 25.1 | 33.2 | 3.8 | 12.4% | 合理反映 | 估值與工業/元件成長股區間大致相符 |
| AEP | American Electric Power | 11. L5 電力供應 / 公用事業 / 核能 | 126.67 USD | 68.9B | 18.5 | 13.3 | 3.1 | 10.2% | 合理反映 | 估值接近成熟公用事業合理區間 |
| CEG | Constellation Energy | 11. L5 電力供應 / 公用事業 / 核能 | 287.75 USD | 103.9B | 21.1 | 15.8 | 3.5 | 63.8% | 合理反映 | 估值接近成熟公用事業合理區間 |
| DUK | Duke Energy | 11. L5 電力供應 / 公用事業 / 核能 | 122.73 USD | 95.7B | 17.1 | 11.4 | 2.9 | 11.3% | 合理反映 | 估值接近成熟公用事業合理區間 |
| NEE | NextEra Energy | 11. L5 電力供應 / 公用事業 / 核能 | 87.01 USD | 181.5B | 19.8 | 20.9 | 6.5 | 7.3% | 合理反映 | 估值接近成熟公用事業合理區間 |
| PEG | PSEG | 11. L5 電力供應 / 公用事業 / 核能 | 78.65 USD | 39.2B | 16.7 | 13.2 | 3.1 | 19.4% | 合理反映 | 估值接近成熟公用事業合理區間 |
| SO | Southern Company | 11. L5 電力供應 / 公用事業 / 核能 | 92.05 USD | 103.8B | 18.7 | 13.0 | 3.4 | 8.0% | 合理反映 | 估值接近成熟公用事業合理區間 |
| SRE | Sempra | 11. L5 電力供應 / 公用事業 / 核能 | 89.13 USD | 58.3B | 16.1 | 18.6 | 4.3 | -3.9% | 合理反映 | 估值接近成熟公用事業合理區間 |
| TECK | Teck Resources | 12. L5 原材料 / 工業氣體 / 電纜 | 66.16 USD | 32.4B | 22.1 | 7.4 | 2.6 | 72.2% | 合理反映 | 材料股估值未明顯過熱，但需看週期位置 |
| ADI | Analog Devices | 2. L2 AI 晶片 / ASIC / CPU / 電源 IC | 413.85 USD | 201.6B | 28.0 | 33.6 | 15.8 | 37.2% | 合理反映 | 估值與高毛利設備/晶片股大致相符 |
| AVGO | Broadcom | 2. L2 AI 晶片 / ASIC / CPU / 電源 IC | 446.77 USD | 2.1T | 24.2 | 58.2 | 31.0 | 29.5% | 合理反映 | 估值與高毛利設備/晶片股大致相符 |
| MCHP | Microchip | 2. L2 AI 晶片 / ASIC / CPU / 電源 IC | 94.65 USD | 51.3B | 23.1 | 46.5 | 10.9 | 35.1% | 合理反映 | 估值與高毛利設備/晶片股大致相符 |
| NVDA | NVIDIA | 2. L2 AI 晶片 / ASIC / CPU / 電源 IC | 211.14 USD | 5.1T | 16.7 | 30.6 | 20.2 | 85.2% | 合理反映 | 估值與高毛利設備/晶片股大致相符 |
| QCOM | Qualcomm | 2. L2 AI 晶片 / ASIC / CPU / 電源 IC | 251.02 USD | 264.6B | 23.6 | 20.8 | 5.9 | -3.5% | 合理反映 | 估值與高毛利設備/晶片股大致相符 |
| 000660.KS | SK hynix | 3. L3 半導體製造 / 記憶體 | 2.33M KRW | 1656.1T | 6.1 | 17.7 | 12.5 | 198.1% | 合理反映 | EV/EBITDA 落在可解釋區間，需追蹤利用率與 capex |
| 005930.KS | Samsung Electronics | 3. L3 半導體製造 / 記憶體 | 317000.00 KRW | 2081.6T | 5.9 | 14.1 | 5.4 | 69.2% | 合理反映 | EV/EBITDA 落在可解釋區間，需追蹤利用率與 capex |
| 2303.TW | 聯電 | 3. L3 半導體製造 / 記憶體 | 144.50 TWD | 1.8T | 27.1 | 16.9 | 7.5 | 5.5% | 合理反映 | EV/EBITDA 落在可解釋區間，需追蹤利用率與 capex |
| AEIS | Advanced Energy | 4. L3 半導體設備 / EDA / 測試 | 302.18 USD | 12.1B | 25.7 | 38.9 | 6.3 | 26.3% | 合理反映 | 估值與高毛利設備/晶片股大致相符 |
| AMAT | Applied Materials | 4. L3 半導體設備 / EDA / 測試 | 450.06 USD | 357.3B | 27.8 | 38.4 | 12.3 | 11.4% | 合理反映 | 估值與高毛利設備/晶片股大致相符 |
| KEYS | Keysight | 4. L3 半導體設備 / EDA / 測試 | 338.33 USD | 57.8B | 28.5 | 38.2 | 9.5 | 31.5% | 合理反映 | 估值與高毛利設備/晶片股大致相符 |
| MKSI | MKS | 4. L3 半導體設備 / EDA / 測試 | 324.26 USD | 21.9B | 21.7 | 27.2 | 5.4 | 15.2% | 合理反映 | 估值與高毛利設備/晶片股大致相符 |
| SNPS | Synopsys | 4. L3 半導體設備 / EDA / 測試 | 475.62 USD | 91.1B | 27.6 | 58.6 | 10.5 | 41.9% | 合理反映 | 估值與高毛利設備/晶片股大致相符 |
| 3044.TW | 健鼎 | 5. L3 先進封裝 / ABF / PCB / CCL | 521.00 TWD | 273.8B | 15.0 | 13.7 | 3.5 | 22.4% | 合理反映 | EV/EBITDA 落在可解釋區間，需追蹤利用率與 capex |
| AMKR | Amkor | 5. L3 先進封裝 / ABF / PCB / CCL | 69.56 USD | 17.2B | 28.4 | 14.3 | 2.4 | 27.5% | 合理反映 | EV/EBITDA 落在可解釋區間，需追蹤利用率與 capex |
| 2317.TW | 鴻海 | 6. L2/L3 AI Server / ODM / Rack | 289.00 TWD | 4.0T | 13.5 | 10.7 | 0.5 | 28.9% | 合理反映 | 低毛利模式估值尚未明顯脫離 earnings / EBITDA 基礎 |
| 2356.TW | 英業達 | 6. L2/L3 AI Server / ODM / Rack | 70.20 TWD | 251.8B | 20.3 | 17.6 | 0.3 | 27.6% | 合理反映 | 低毛利模式估值尚未明顯脫離 earnings / EBITDA 基礎 |
| 2357.TW | 華碩 | 6. L2/L3 AI Server / ODM / Rack | 761.00 TWD | 565.2B | 13.4 | 13.9 | 0.7 | 41.1% | 合理反映 | 低毛利模式估值尚未明顯脫離 earnings / EBITDA 基礎 |
| 2376.TW | 技嘉 | 6. L2/L3 AI Server / ODM / Rack | 370.00 TWD | 247.9B | 12.0 | 13.2 | 0.7 | 59.8% | 合理反映 | 低毛利模式估值尚未明顯脫離 earnings / EBITDA 基礎 |
| 2382.TW | 廣達 | 6. L2/L3 AI Server / ODM / Rack | 339.00 TWD | 1.3T | 12.0 | 16.0 | 0.5 | 66.6% | 合理反映 | 低毛利模式估值尚未明顯脫離 earnings / EBITDA 基礎 |
| 3231.TW | 緯創 | 6. L2/L3 AI Server / ODM / Rack | 158.50 TWD | 504.1B | 9.1 | 9.1 | 0.2 | 144.3% | 合理反映 | 低毛利模式估值尚未明顯脫離 earnings / EBITDA 基礎 |
| 6669.TW | 緯穎 | 6. L2/L3 AI Server / ODM / Rack | 5445.00 TWD | 1.0T | 11.9 | 14.7 | 1.0 | 62.0% | 合理反映 | 低毛利模式估值尚未明顯脫離 earnings / EBITDA 基礎 |
| 6702.T | Fujitsu | 6. L2/L3 AI Server / ODM / Rack | 3368.00 JPY | 5.8T | 22.2 | 11.3 | 1.7 |  | 合理反映 | 低毛利模式估值尚未明顯脫離 earnings / EBITDA 基礎 |
| CSCO | Cisco | 7. L2/L3 Networking / 光通訊 | 120.42 USD | 474.6B | 25.2 | 28.9 | 7.8 | 12.0% | 合理反映 | 估值與工業/元件成長股區間大致相符 |
| CARR | Carrier | 8. L4 Data Center 電力 / 散熱 / 配電 | 63.87 USD | 53.0B | 20.0 | 20.6 | 2.4 | 2.4% | 合理反映 | 估值與工業/元件成長股區間大致相符 |
| EMR | Emerson | 8. L4 Data Center 電力 / 散熱 / 配電 | 143.82 USD | 80.6B | 20.1 | 15.8 | 4.4 | 2.9% | 合理反映 | 估值與工業/元件成長股區間大致相符 |
| ETN | Eaton | 8. L4 Data Center 電力 / 散熱 / 配電 | 400.60 USD | 155.6B | 25.5 | 27.9 | 5.5 | 16.8% | 合理反映 | 估值與工業/元件成長股區間大致相符 |
| HON | Honeywell | 8. L4 Data Center 電力 / 散熱 / 配電 | 237.86 USD | 150.7B | 20.8 | 20.8 | 4.0 | 2.4% | 合理反映 | 估值與工業/元件成長股區間大致相符 |
| HUBB | Hubbell | 8. L4 Data Center 電力 / 散熱 / 配電 | 473.61 USD | 25.0B | 21.8 | 18.6 | 4.2 | 11.1% | 合理反映 | 估值與工業/元件成長股區間大致相符 |
| JCI | Johnson Controls | 8. L4 Data Center 電力 / 散熱 / 配電 | 134.06 USD | 81.8B | 23.5 | 21.0 | 3.3 | 8.2% | 合理反映 | 估值與工業/元件成長股區間大致相符 |
| LR.PA | Legrand | 8. L4 Data Center 電力 / 散熱 / 配電 | 147.65 EUR | 38.6B | 22.9 | 20.1 | 4.0 | 11.4% | 合理反映 | 估值與工業/元件成長股區間大致相符 |
| MOD | Modine | 8. L4 Data Center 電力 / 散熱 / 配電 | 278.91 USD | 14.7B | 24.4 | 34.0 | 4.6 | 47.5% | 合理反映 | 估值與工業/元件成長股區間大致相符 |
| PH | Parker-Hannifin | 8. L4 Data Center 電力 / 散熱 / 配電 | 844.63 USD | 106.5B | 24.8 | 21.1 | 5.1 | 10.6% | 合理反映 | 估值與工業/元件成長股區間大致相符 |
| SIE.DE | Siemens | 8. L4 Data Center 電力 / 散熱 / 配電 | 269.80 EUR | 205.8B | 21.2 | 22.1 | 2.6 | -0.0% | 合理反映 | 估值與工業/元件成長股區間大致相符 |
| SU.PA | Schneider Electric | 8. L4 Data Center 電力 / 散熱 / 配電 | 269.95 EUR | 151.9B | 23.6 | 21.1 | 3.8 | 4.2% | 合理反映 | 估值與工業/元件成長股區間大致相符 |
| TT | Trane Technologies | 8. L4 Data Center 電力 / 散熱 / 配電 | 451.30 USD | 99.8B | 26.5 | 24.4 | 4.6 | 6.0% | 合理反映 | 估值與工業/元件成長股區間大致相符 |
| WCC | WESCO | 8. L4 Data Center 電力 / 散熱 / 配電 | 361.17 USD | 17.6B | 19.2 | 15.5 | 0.7 | 13.8% | 合理反映 | 估值與工業/元件成長股區間大致相符 |
| ACM | AECOM | 9. L4 EPC / 建設 / 機電工程 | 69.37 USD | 8.9B | 10.3 | 8.9 | 0.6 | 0.8% | 合理反映 | 以可得倍數未見明顯過熱，但需補 forward estimates |
| DY | Dycom | 9. L4 EPC / 建設 / 機電工程 | 510.00 USD | 15.3B | 26.0 | 21.5 | 2.4 | 56.1% | 合理反映 | 以可得倍數未見明顯過熱，但需補 forward estimates |
| FIX | Comfort Systems USA | 9. L4 EPC / 建設 / 機電工程 | 1828.21 USD | 64.3B | 34.4 | 38.5 | 6.3 | 1.0% | 合理反映 | 以可得倍數未見明顯過熱，但需補 forward estimates |
| FLR | Fluor | 9. L4 EPC / 建設 / 機電工程 | 45.76 USD | 6.4B | 13.9 | -11.0 | 0.4 | -8.0% | 合理反映 | 以可得倍數未見明顯過熱，但需補 forward estimates |
| GVA | Granite Construction | 9. L4 EPC / 建設 / 機電工程 | 136.84 USD | 6.0B | 18.1 | 15.4 | 1.3 | 30.4% | 合理反映 | 以可得倍數未見明顯過熱，但需補 forward estimates |
| J | Jacobs | 9. L4 EPC / 建設 / 機電工程 | 119.86 USD | 14.2B | 14.5 | 16.9 | 1.1 | 27.0% | 合理反映 | 以可得倍數未見明顯過熱，但需補 forward estimates |

## 資料不足 / 需覆核

| Ticker | 公司 | 類型 | 價格 | 市值 | PE/Fwd PE | EV/EBITDA | PS | 營收成長 | 標籤 | 判讀 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| TSM | TSMC | 3. L3 半導體製造 / 記憶體 | 418.45 USD | 2.2T | 21.4 | 3.0 | 0.5 | 35.1% | 資料不足 | 需要利用率、折舊與 capex 後 FCF 支持 |
| GFS | GlobalFoundries | 3. L3 半導體製造 / 記憶體 | 79.97 USD | 43.9B | 31.8 | 21.0 | 6.4 | 3.1% | 資料不足 | 需要利用率、折舊與 capex 後 FCF 支持 |
| UMC | UMC | 3. L3 半導體製造 / 記憶體 | 22.18 USD | 55.7B | 27.6 | 2.1 | 0.2 | 5.5% | 資料不足 | 需要利用率、折舊與 capex 後 FCF 支持 |
| ANSS | Ansys | 4. L3 半導體設備 / EDA / 測試 |  |  |  |  |  |  | 資料不足 | 缺少可用的 PE / EV/EBITDA / PS / PB 基礎 |
| ICHR | Ichor | 4. L3 半導體設備 / EDA / 測試 | 71.52 USD | 2.5B | 27.4 | 94.3 | 2.6 | 4.7% | 資料不足 | 虧損公司需要 breakeven revenue / cash burn 資料 |
| 3711.TW | 日月光投控 | 5. L3 先進封裝 / ABF / PCB / CCL | 611.00 TWD | 2.7T | 26.2 | 22.7 | 4.0 | 17.2% | 資料不足 | 需要利用率、折舊與 capex 後 FCF 支持 |
| 6967.T | Shinko | 5. L3 先進封裝 / ABF / PCB / CCL |  |  |  |  |  |  | 資料不足 | 缺少可用的 PE / EV/EBITDA / PS / PB 基礎 |
| 2316.TW | 楠梓電 | 5. L3 先進封裝 / ABF / PCB / CCL | 168.50 TWD | 30.6B | 12.6 | -617.7 | 7.9 | 17.4% | 資料不足 | 需要利用率、折舊與 capex 後 FCF 支持 |
| ROG | Rogers | 5. L3 先進封裝 / ABF / PCB / CCL | 141.52 USD | 2.5B | 32.4 | 20.0 | 3.1 | 5.2% | 資料不足 | 虧損公司需要 breakeven revenue / cash burn 資料 |
| HPE | HPE | 6. L2/L3 AI Server / ODM / Rack | 43.04 USD | 57.1B | 15.8 | 15.1 | 1.6 | 18.4% | 資料不足 | 虧損公司需要 breakeven revenue / cash burn 資料 |
| ATKR | Atkore | 8. L4 Data Center 電力 / 散熱 / 配電 | 82.81 USD | 2.8B | 13.5 | 11.4 | 1.0 | 4.2% | 資料不足 | 虧損公司需要 breakeven revenue / cash burn 資料 |
| OKLO | Oklo | 11. L5 電力供應 / 公用事業 / 核能 | 66.88 USD | 11.6B | -79.7 | -54.8 |  |  | 資料不足 | 虧損公司需要 breakeven revenue / cash burn 資料 |
| RIO | Rio Tinto | 12. L5 原材料 / 工業氣體 / 電纜 | 106.39 USD | 173.0B | 12.0 | 9.5 | 3.0 | 14.6% | 資料不足 | 材料股需要 mid-cycle EBITDA / ROIC 才能定性 |
| NUE | Nucor | 12. L5 原材料 / 工業氣體 / 電纜 | 250.00 USD | 56.9B | 15.8 | 12.7 | 1.7 | 21.3% | 資料不足 | 材料股需要 mid-cycle EBITDA / ROIC 才能定性 |
| AA | Alcoa | 12. L5 原材料 / 工業氣體 / 電纜 | 77.64 USD | 20.5B | 11.5 | 12.8 | 1.6 | -5.2% | 資料不足 | 材料股需要 mid-cycle EBITDA / ROIC 才能定性 |
| NEX.PA | Nexans | 12. L5 原材料 / 工業氣體 / 電纜 | 158.40 EUR | 6.9B | 17.4 | 11.1 | 0.9 |  | 資料不足 | 材料股需要 mid-cycle EBITDA / ROIC 才能定性 |
| 4063.T | Shin-Etsu | 12. L5 原材料 / 工業氣體 / 電纜 | 7758.00 JPY | 14.4T | 23.5 | 15.0 | 5.6 | 1.3% | 資料不足 | 材料股需要 mid-cycle EBITDA / ROIC 才能定性 |
| 3436.T | SUMCO | 12. L5 原材料 / 工業氣體 / 電纜 | 3994.00 JPY | 1.4T | 81.1 | 16.0 | 3.4 | -1.0% | 資料不足 | 虧損公司需要 breakeven revenue / cash burn 資料 |
| 4091.T | Nippon Sanso | 12. L5 原材料 / 工業氣體 / 電纜 | 6184.00 JPY | 2.7T | 22.3 | 10.7 | 2.0 | 7.5% | 資料不足 | 材料股需要 mid-cycle EBITDA / ROIC 才能定性 |

## 分類結論

- GPU / ASIC：龍頭與高純度標的多半已反映高成長，需要檢查 FY2026-2028 EPS/FCF CAGR 是否足以支撐目前倍數。
- HBM / CoWoS / ABF：不能只看 PE；記憶體要用 mid-cycle P/B / EBITDA，封裝與代工要看 capex 後 ROIC 與利用率。
- ODM / EMS：AI server 營收成長很快，但低毛利與 working capital 會稀釋估值，PS 偏高者要特別保守。
- 電力 / 散熱：Vertiv、Eaton、Schneider、GE Vernova 這類已被市場重評，合理性取決於 backlog、margin 與交期瓶頸能否維持。
- 公用事業 / 發電：AI load growth 有長期支撐，但估值不能脫離監管回報、PPA 價格與 capex funding。
- 原材料：AI 是需求增量之一，不是唯一因子；必須用 mid-cycle spread / ROIC，不能用單一年景氣高點判斷便宜。

## 後續必補資料

1. Forward EPS / EBITDA consensus 與 3-5 年 CAGR。
2. AI revenue purity、backlog、book-to-bill、客戶集中度。
3. Capex 後 FCF、ROIC vs WACC，尤其是代工、封裝、電力與公用事業。
4. 記憶體與材料的 mid-cycle earnings，避免用高峰 EPS 誤判便宜。
5. 國際 ticker 的幣別、ADR 對應與 Yahoo Finance 缺值覆核。

## 資料來源

- [Yahoo Finance](https://finance.yahoo.com/) quote/fundamental fields via [yfinance](https://pypi.org/project/yfinance/), accessed on generation date.
- 供應鏈分類來源：`ai_supply_chain_stock_pool.md`。
