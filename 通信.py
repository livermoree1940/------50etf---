# ==================  用户只用改这一小段  ==================
BLOCK_NAME      = "通信"           # 板块中文名（任意）
SOURCE_TYPE     = "sw"            # "xml" 或 "sw" 二选一
XML_PATH        = r"F:\Program Files\同花顺远航版\bin\users\mx_713570454\blockstockV3.xml"
XML_BLOCK_NAME  = "通信"           # xml 里 <Block name="xxx">
SW_INDEX_CODE   = 801770          # 申万行业指数代码
BUY_THRESHOLD   = 30
SELL_THRESHOLD  = 70
ANALYSIS_DAYS   = 900
MAX_THREADS     = 10
CACHE_DIR       = r"D:\stock_cache"
# ============================================================

# -------------------- 以下代码完全保留你原来的全部逻辑 --------------------
# 唯一改动：get_stock_data 内部换成“多接口备用”版本
import pandas as pd
import matplotlib.pyplot as plt
import akshare as ak
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import concurrent.futures
import numpy as np
import time
import os
import warnings
import traceback
import mplcursors
import matplotlib.dates as mdates
from matplotlib.dates import num2date
import sys

# 添加utils_email的导入
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils_email import send_email_if_signal

warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

os.makedirs(CACHE_DIR, exist_ok=True)

# ---------- ① 股票代码来源 ----------
def getcodebyshengwan(symbol=SW_INDEX_CODE):
    try:
        df = ak.index_component_sw(symbol=symbol)
        print(f"成功获取申万指数 {symbol} 的成分股数据，共 {len(df)} 只股票")
        return ["sh"+str(c) if str(c).startswith('6') else "sz"+str(c) for c in df['证券代码']]
    except Exception as e:
        print(f"获取申万指数 {symbol} 成分股时出错: {e}")
        return []

def getcodebyxml(xml_path, block_name):
    try:
        tree = ET.parse(xml_path)
        for b in tree.iter("Block"):
            if b.get("name") == block_name:
                codes = []
                for s in b.iter("security"):
                    m, c = s.get("market"), s.get("code")
                    codes.append(f"sh{c}" if m == "USHA" else f"sz{c}")
                return codes
    except Exception as e:
        print(f"xml 解析失败: {e}")
    return []

# ---------- ② 多接口备用 get_stock_data ----------
def get_stock_data(stock_code, days=ANALYSIS_DAYS):
    pure_code = stock_code[2:]
    cache_file = os.path.join(CACHE_DIR, f"{pure_code}.pkl")
    if os.path.exists(cache_file):
        try:
            df = pd.read_pickle(cache_file)
            if len(df) >= days + 60:
                return process_stock_data(df, days)
        except:
            pass

    end_date = datetime.now().strftime("%Y%m%d")
    start_date = "20240101"

    # 备用接口列表：腾讯→新浪→东财→通用
    api_list = [
        ("腾讯", lambda: ak.stock_zh_a_hist_tx(symbol=pure_code)),
        ("新浪", lambda: ak.stock_zh_a_hist_sina(symbol=pure_code)),
        ("东财", lambda: ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                        start_date=start_date, end_date=end_date, adjust="hfq")),
        ("通用", lambda: ak.index_zh_a_hist(symbol=pure_code, period="daily",
                                         start_date=start_date, end_date=end_date))
    ]

    df = None
    for src, api in api_list:
        try:
            print(f"[{src}] 尝试 {stock_code} ...")
            df = api()
            if df is not None and not df.empty:
                print(f"{src} 接口成功 → {stock_code}")
                break
        except Exception as e:
            print(f"  └─ {src} 失败: {str(e)[:60]}")
            time.sleep(np.random.uniform(0.1, 0.5))

    if df is None or df.empty or len(df) < 60:
        return None

    # 统一列名
    if '日期' in df.columns:
        df = df.rename(columns={'日期': 'date', '收盘': 'close'})
    elif 'trade_date' in df.columns:
        df = df.rename(columns={'trade_date': 'date', 'close': 'close'})
    elif 'date' not in df.columns:
        df = df.reset_index().rename(columns={'index': 'date'})
    if 'close' not in df.columns and '收盘' in df.columns:
        df = df.rename(columns={'收盘': 'close'})

    df = df[['date', 'close']].copy()
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df['ma60'] = df['close'].rolling(window=60, min_periods=1).mean()
    df['above'] = df['close'] > df['ma60']
    df.to_pickle(cache_file)
    return process_stock_data(df, days)

def process_stock_data(df, days):
    df = df.sort_index()
    return df.tail(days) if len(df) > days else df

# ---------- ③ 以下为你原来的全部代码，一字不动 ----------
def check_ma60_signal(history_df):
    """检查60日线比例变化并触发邮件预警"""
    if len(history_df) < 2:
        print("数据不足，无法进行信号判断")
        return
    latest_data = history_df.iloc[-1]
    prev_data = history_df.iloc[-2]
    latest_ratio = latest_data['above_ratio']
    prev_ratio = prev_data['above_ratio']
    latest_date = history_df.index[-1].strftime('%Y-%m-%d')
    prev_date = history_df.index[-2].strftime('%Y-%m-%d')
    print(f"\n信号检测结果:")
    print(f"前一日 ({prev_date}): {prev_ratio:.1f}%")
    print(f"最新日 ({latest_date}): {latest_ratio:.1f}%")
    print(f"买入阈值: {BUY_THRESHOLD}%, 卖出阈值: {SELL_THRESHOLD}%")
    if prev_ratio < BUY_THRESHOLD and latest_ratio >= BUY_THRESHOLD:
        subject = f"【买入信号】{BLOCK_NAME}板块60日线比例转强"
        message = f"""
        {BLOCK_NAME}板块出现60日线比例买入信号：
        统计日期：{latest_date}
        站上60日线比例：{latest_ratio:.1f}% （前一日：{prev_ratio:.1f}%）
        信号说明：比例由低于{BUY_THRESHOLD}%转为达到或超过{BUY_THRESHOLD}%
        当前状态：★★★ 买入机会 ★★★
        有效股票数量：{latest_data['above_count']}/{latest_data['valid_count']}
        策略建议：考虑分批建仓，控制仓位风险
        """
        image_path = f'{BLOCK_NAME}_板块分析_{datetime.now().strftime("%Y%m%d")}.png'
        print(f"🚨 买入信号触发！比例从 {prev_ratio:.1f}% 升至 {latest_ratio:.1f}%")
        send_email_if_signal(message, image_path)
    elif prev_ratio > SELL_THRESHOLD and latest_ratio <= SELL_THRESHOLD:
        subject = f"【卖出信号】{BLOCK_NAME}板块60日线比例转弱"
        message = f"""
        {BLOCK_NAME}板块出现60日线比例卖出信号：
        统计日期：{latest_date}
        站上60日线比例：{latest_ratio:.1f}% （前一日：{prev_ratio:.1f}%）
        信号说明：比例由高于{SELL_THRESHOLD}%转为达到或低于{SELL_THRESHOLD}%
        当前状态：★★★ 卖出信号 ★★★
        有效股票数量：{latest_data['above_count']}/{latest_data['valid_count']}
        策略建议：考虑减仓或止盈，控制回撤风险
        """
        image_path = f'{BLOCK_NAME}_板块分析_{datetime.now().strftime("%Y%m%d")}.png'
        print(f"🚨 卖出信号触发！比例从 {prev_ratio:.1f}% 降至 {latest_ratio:.1f}%")
        send_email_if_signal(message, image_path)
    else:
        print("📊 无信号触发，继续观望")
        if latest_ratio < BUY_THRESHOLD:
            print(f"💚 当前处于低位区域 ({latest_ratio:.1f}% < {BUY_THRESHOLD}%)")
        elif latest_ratio > SELL_THRESHOLD:
            print(f"🔴 当前处于高位区域 ({latest_ratio:.1f}% > {SELL_THRESHOLD}%)")
        else:
            print(f"🟡 当前处于中性区域 ({BUY_THRESHOLD}% ≤ {latest_ratio:.1f}% ≤ {SELL_THRESHOLD}%)")

def enhanced_print_ma60_history(history_df):
    if history_df.empty:
        print("无有效数据")
        return
    print(f"\n{BLOCK_NAME}板块60日均线位置历史变化:")
    print("日期\t\t站上比例\t站上数量/有效数量")
    print("-" * 50)
    for date, row in history_df.tail(20).iterrows():
        print(f"{date.strftime('%Y-%m-%d')}\t{row['above_ratio']:.1f}%\t{row['above_count']}/{row['valid_count']}")
    avg_ratio = history_df['above_ratio'].mean()
    latest_ratio = history_df.iloc[-1]['above_ratio']
    current_date = datetime.now().strftime("%m%d")
    print(f"\n统计周期: {history_df.index[0].strftime('%Y-%m-%d')} 至 {history_df.index[-1].strftime('%Y-%m-%d')}")
    print(f"平均站上60日线比例: {avg_ratio:.1f}%")
    print(f"{current_date} 涨跌比 {int(latest_ratio)}:{int(100-latest_ratio)}")
    print(f"最高比例: {history_df['above_ratio'].max():.1f}%, 最低比例: {history_df['above_ratio'].min():.1f}%")
    if latest_ratio < BUY_THRESHOLD:
        print(f"\n当前状态: ★★★ 买入机会 (低于{BUY_THRESHOLD}%) ★★★")
    elif latest_ratio > SELL_THRESHOLD:
        print(f"\n当前状态: ★★★ 卖出信号 (高于{SELL_THRESHOLD}%) ★★★")
    else:
        print("\n当前状态: 持有观望")
    check_ma60_signal(history_df)

def calculate_ma60_history(stock_codes, days=ANALYSIS_DAYS):
    print(f"开始处理 {len(stock_codes)} 只股票...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(lambda c: (c, get_stock_data(c, days)), code) for code in stock_codes]
        stock_data = {}
        for f in concurrent.futures.as_completed(futures):
            code, df = f.result()
            if df is not None and not df.empty:
                stock_data[code] = df
                print(f"成功处理: {code}")
            else:
                print(f"处理失败: {code}")
    if not stock_data:
        return pd.DataFrame(), {}
    all_dates = sorted({d for df in stock_data.values() for d in df.index})
    rec = []
    for d in all_dates:
        abv = val = 0
        for df in stock_data.values():
            if d in df.index:
                val += 1
                abv += df.loc[d, 'above']
        if val:
            rec.append({'date': d, 'above_ratio': abv/val*100, 'above_count': abv, 'valid_count': val})
    hist = pd.DataFrame(rec).set_index('date')
    hist.index = pd.to_datetime(hist.index)
    print(f"历史数据范围: {hist.index[0].date()} 至 {hist.index[-1].date()}")
    return hist, stock_data

def build_equal_weight_index(stock_data):
    if not stock_data:
        return None
    all_dates = sorted({d for df in stock_data.values() for d in df.index})
    vals = []
    for d in all_dates:
        closes = [df.loc[d, 'close'] for df in stock_data.values() if d in df.index]
        if closes:
            vals.append(np.mean(closes))
        else:
            vals.append(np.nan)
    idx = pd.DataFrame({'index_value': vals}, index=pd.to_datetime(all_dates))
    idx['index_ma60'] = idx['index_value'].rolling(60).mean()
    return idx

def plot_index_and_ratio(history_df, index_data):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), sharex=True)
    merged = pd.merge(history_df, index_data, left_index=True, right_index=True, how='inner')
    if merged.empty:
        print(" merged 为空，跳过绘图")
        return
    # 图1：指数
    l1, = ax1.plot(merged.index, merged['index_value'], label='指数值', color='blue', linewidth=1.5)
    l2, = ax1.plot(merged.index, merged['index_ma60'], label='指数60日均线', color='red', linestyle='--', linewidth=1.5)
    ax1.set_ylabel('指数值'); ax1.set_title(f'{BLOCK_NAME}板块指数走势'); ax1.grid(True, linestyle='--', alpha=0.7); ax1.legend()
    y_min, y_max = ax1.get_ylim()
    ax1.fill_between(merged.index, y_min, y_max, where=(merged['above_ratio'] < BUY_THRESHOLD), color='green', alpha=0.1)
    ax1.fill_between(merged.index, y_min, y_max, where=((merged['above_ratio'] >= BUY_THRESHOLD) & (merged['above_ratio'] <= SELL_THRESHOLD)), color='yellow', alpha=0.1)
    ax1.fill_between(merged.index, y_min, y_max, where=(merged['above_ratio'] > SELL_THRESHOLD), color='red', alpha=0.1)
    ax1.set_ylim(y_min, y_max)
    # 图2：比例
    l3, = ax2.plot(merged.index, merged['above_ratio'], marker='o', linestyle='-', color='purple', linewidth=1.5, markersize=3, label='60日线上比例')
    ax2.fill_between(merged.index, 0, BUY_THRESHOLD, where=(merged['above_ratio'] < BUY_THRESHOLD), color='green', alpha=0.2)
    ax2.fill_between(merged.index, BUY_THRESHOLD, SELL_THRESHOLD, where=((merged['above_ratio'] >= BUY_THRESHOLD) & (merged['above_ratio'] <= SELL_THRESHOLD)), color='yellow', alpha=0.2)
    ax2.fill_between(merged.index, SELL_THRESHOLD, 100, where=(merged['above_ratio'] > SELL_THRESHOLD), color='red', alpha=0.2)
    ax2.axhline(BUY_THRESHOLD, color='green', linestyle='--', alpha=0.7); ax2.axhline(SELL_THRESHOLD, color='red', linestyle='--', alpha=0.7)
    ax2.set_xlabel('日期'); ax2.set_ylabel('比例 (%)'); ax2.set_title('60日线以上比例'); ax2.set_ylim(0, 100); ax2.grid(True, linestyle='--', alpha=0.7); ax2.legend(loc='upper right')
    date_format = mdates.DateFormatter('%Y-%m-%d'); ax2.xaxis.set_major_formatter(date_format)
    num_days = len(merged)
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, num_days // 15)) if num_days > 180 else mdates.DayLocator(interval=1))
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right'); plt.tight_layout()
    # 交互光标
    cursor1 = mplcursors.cursor(l1, hover=True); cursor2 = mplcursors.cursor(l2, hover=True); cursor3 = mplcursors.cursor(l3, hover=True)
    @cursor1.connect("add")
    def on_add1(sel): sel.annotation.set(text=f"日期: {num2date(sel.target[0]).strftime('%Y-%m-%d')}\n指数值: {sel.target[1]:.2f}")
    @cursor2.connect("add")
    def on_add2(sel): sel.annotation.set(text=f"日期: {num2date(sel.target[0]).strftime('%Y-%m-%d')}\n60日均线: {sel.target[1]:.2f}")
    @cursor3.connect("add")
    def on_add3(sel):
        date_obj = num2date(sel.target[0]); date_str = date_obj.strftime('%Y-%m-%d')
        if date_str in merged.index.strftime('%Y-%m-%d').values:
            row = merged.loc[merged.index.strftime('%Y-%m-%d') == date_str].iloc[0]
            sel.annotation.set(text=f"日期: {date_str}\n比例: {sel.target[1]:.1f}%\n站上数量: {row['above_count']}/{row['valid_count']}")
        else:
            sel.annotation.set(text=f"日期: {date_str}\n比例: {sel.target[1]:.1f}%")
    # 保存
    filename = f'{BLOCK_NAME}_板块分析_{datetime.now().strftime("%Y%m%d")}.png'
    plt.savefig(filename, dpi=300); print(f"图表已保存至: {filename}"); plt.show()

# -------------------- 主入口 --------------------
if __name__ == "__main__":
    # 1. 选代码来源
    if SOURCE_TYPE == "xml":
        stock_codes = getcodebyxml(XML_PATH, XML_BLOCK_NAME)
    else:
        stock_codes = getcodebyshengwan(SW_INDEX_CODE)

    if not stock_codes:
        print(f"未找到板块 '{BLOCK_NAME}'")
        exit()
    print(f"板块 '{BLOCK_NAME}' 共 {len(stock_codes)} 只股票")

    # 2. 以下完全是你原来的流程
    history_df, stock_data = calculate_ma60_history(stock_codes, ANALYSIS_DAYS)
    if not history_df.empty:
        enhanced_print_ma60_history(history_df)
        index_data = build_equal_weight_index(stock_data)
        if index_data is not None:
            plot_index_and_ratio(history_df, index_data)
    else:
        print("未能生成有效数据，请检查股票代码和数据源")