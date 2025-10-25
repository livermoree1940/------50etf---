# -*- coding: utf-8 -*-
# 30%以下加仓 破60日线卖出
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
import mplcursors  # 添加交互式光标支持
import matplotlib.dates as mdates
from matplotlib.dates import num2date
import os
import sys
from datetime import datetime, timedelta
zhongzhzhishu="000688"
# 科创50 000688  沪深300  000300
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils_email import send_email_if_signal
def get_hs300_codes():
    """取沪深300最新成分股（含市场前缀 sh/sz）"""
    df = ak.index_stock_cons(symbol=zhongzhzhishu)          # 中证指数公司接口
    codes = []
    for _, row in df.iterrows():
        raw = row['品种代码'].zfill(6)
        pre = 'sh' if raw.startswith('6') else 'sz'
        codes.append(f"{pre}{raw}")
    print(f"已获取沪深300成分股 {len(codes)} 只")
    return codes
def check_ma60_signal(history_df):
    """检查60日线比例变化并触发邮件预警"""
    if len(history_df) < 2:
        print("数据不足，无法进行信号判断")
        return
    
    # 获取最新两天数据
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
    
    # 买入信号：前一天＜阈值，最新一天≥阈值
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
        
        # 生成图表文件路径
        image_path = f'{BLOCK_NAME}_板块分析_{datetime.now().strftime("%Y%m%d")}.png'
        
        print(f"🚨 买入信号触发！比例从 {prev_ratio:.1f}% 升至 {latest_ratio:.1f}%")
        send_email_if_signal(message, image_path)
    
    # 卖出信号：前一天＞阈值，最新一天≤阈值
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
        
        # 生成图表文件路径
        image_path = f'{BLOCK_NAME}_板块分析_{datetime.now().strftime("%Y%m%d")}.png'
        
        print(f"🚨 卖出信号触发！比例从 {prev_ratio:.1f}% 降至 {latest_ratio:.1f}%")
        send_email_if_signal(message, image_path)
    
    else:
        print("📊 无信号触发，继续观望")
        
        # 输出当前状态分析
        if latest_ratio < BUY_THRESHOLD:
            print(f"💚 当前处于低位区域 ({latest_ratio:.1f}% < {BUY_THRESHOLD}%)")
        elif latest_ratio > SELL_THRESHOLD:
            print(f"🔴 当前处于高位区域 ({latest_ratio:.1f}% > {SELL_THRESHOLD}%)")
        else:
            print(f"🟡 当前处于中性区域 ({BUY_THRESHOLD}% ≤ {latest_ratio:.1f}% ≤ {SELL_THRESHOLD}%)")

def enhanced_print_ma60_history(history_df):
    """增强版统计结果打印，包含信号检测"""
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
    
    # 添加信号检测
    check_ma60_signal(history_df)

# 忽略警告
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

XML_PATH = r"F:\Program Files\同花顺远航版\bin\users\mx_713570454\blockstockV3.xml"
BLOCK_NAME = "银行"
ANALYSIS_DAYS = 900
MAX_THREADS = 10
BUY_THRESHOLD = 30
SELL_THRESHOLD = 70
CACHE_DIR = r"D:\stock_cache"

# 创建缓存目录
os.makedirs(CACHE_DIR, exist_ok=True)

# def getcodebyxml(xml_path, block_name):
#     """解析XML文件获取股票代码"""
#     tree = ET.parse(xml_path)
#     root = tree.getroot()
#     for block in root.findall("Block"):
#         if block.get("name") == block_name:
#             stock_codes = []
#             for security in block.findall("security"):
#                 code = security.get("code")
#                 market = security.get("market")
#                 if market == "USHA":  # 沪市
#                     stock_codes.append(f"sh{code}")
#                 else:  # 深市
#                     stock_codes.append(f"sz{code}")
#             return stock_codes
#     return []
#     通过akshare 的 api 输入为申万银行指数

def getcodebyshengwan(symbol=801780):
    
    try:
        # 调用AKShare接口获取成分股数据
        index_component_sw_df = ak.index_component_sw(symbol=symbol)
        
        # 调试：打印数据前几行，确保获取成功
        print(f"成功获取申万指数 {symbol} 的成分股数据，共 {len(index_component_sw_df)} 只股票")
        print(index_component_sw_df.head())
        
        stock_codes = []
        for index, row in index_component_sw_df.iterrows():
            raw_code = row['证券代码']
            # 根据证券代码判断市场并格式化
            # 通常规则：6开头为沪市，0或3开头为深市
            if str(raw_code).startswith('6'):
                formatted_code = f"sh{raw_code}"
            else:
                formatted_code = f"sz{raw_code}"
            stock_codes.append(formatted_code)
        
        return stock_codes
        
    except Exception as e:
        print(f"获取申万指数 {symbol} 成分股时出错: {e}")
        return []
def get_stock_data(stock_code, days=ANALYSIS_DAYS):
    """获取股票数据并计算60日均线，优先级：腾讯 > 新浪 > 东财"""
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
    
    try:
        time.sleep(np.random.uniform(0.1, 0.5))
        
        df = None
        
        # 第一优先级：腾讯接口
        try:
            print(f"尝试腾讯接口获取 {stock_code} 数据...")
            df = ak.stock_zh_a_hist_tx(symbol=pure_code)
            if df is not None and not df.empty:
                print(f"腾讯接口成功获取 {stock_code} 数据")
        except Exception as e:
            print(f"腾讯接口获取 {stock_code} 数据失败: {str(e)}")
        
        # 第二优先级：新浪接口
        if df is None or df.empty:
            try:
                print(f"尝试新浪接口获取 {stock_code} 数据...")
                df = ak.stock_zh_a_hist_sina(symbol=pure_code)
                if df is not None and not df.empty:
                    print(f"新浪接口成功获取 {stock_code} 数据")
            except Exception as e:
                print(f"新浪接口获取 {stock_code} 数据失败: {str(e)}")
        
        # 第三优先级：东财接口（原接口）
        if df is None or df.empty:
            try:
                print(f"尝试东财接口获取 {stock_code} 数据...")
                df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                                        start_date=start_date, end_date=end_date, 
                                        adjust="hfq")
                if df is not None and not df.empty:
                    print(f"东财接口成功获取 {stock_code} 数据")
            except Exception as e:
                print(f"东财接口获取 {stock_code} 数据失败: {str(e)}")
        
        # 最后的备选方案
        if df is None or df.empty:
            try:
                df = ak.stock_zh_a_hist(symbol=pure_code, period="daily", 
                                        start_date=start_date, end_date=end_date, 
                                        adjust="hfq")
            except:
                try:
                    df = ak.stock_zh_a_daily(symbol=stock_code, adjust="qfq")
                    if df is not None and len(df) > days + 100:
                        df = df.iloc[-(days+100):]
                except:
                    return None
        
        if df is None or df.empty or len(df) < 60:
            return None
        
        # 统一列名格式
        if '日期' in df.columns:
            df = df.rename(columns={'日期': 'date', '收盘': 'close'})
        elif 'trade_date' in df.columns:
            df = df.rename(columns={'trade_date': 'date', 'close': 'close'})
        elif 'date' not in df.columns:
            df = df.reset_index().rename(columns={'index': 'date'})
        
        # 确保有close列
        if 'close' not in df.columns:
            if '收盘' in df.columns:
                df = df.rename(columns={'收盘': 'close'})
            elif 'close' in df.columns:
                pass
            else:
                return None
        
        df = df[['date', 'close']].copy()
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        df['ma60'] = df['close'].rolling(window=60, min_periods=1).mean()
        df['above'] = df['close'] > df['ma60']
        
        df.to_pickle(cache_file)
        
        return process_stock_data(df, days)
    except Exception as e:
        print(f"获取 {stock_code} 数据失败: {str(e)}")
        traceback.print_exc()
        return None

def process_stock_data(df, days):
    """处理股票数据并返回所需天数"""
    df = df.sort_index()
    if len(df) > days:
        return df.iloc[-days:]
    return df

def process_stock(stock_code, days):
    """处理单只股票数据"""
    df = get_stock_data(stock_code, days)
    return stock_code, df

def calculate_ma60_history(stock_codes, days=ANALYSIS_DAYS):
    """计算60日均线比例历史"""
    print(f"开始处理 {len(stock_codes)} 只股票...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(process_stock, code, days) for code in stock_codes]
        stock_data = {}
        for future in concurrent.futures.as_completed(futures):
            try:
                code, df = future.result()
                if df is not None and not df.empty:
                    stock_data[code] = df
                    start_date = df.index[0].strftime('%Y-%m-%d')
                    end_date = df.index[-1].strftime('%Y-%m-%d')
                    print(f"成功处理: {code} ({start_date} 至 {end_date})")
                else:
                    print(f"处理失败: {code} (无有效数据)")
            except Exception as e:
                print(f"处理 {code} 时发生错误: {str(e)}")
    
    print(f"处理完成: 成功 {len(stock_data)}, 失败 {len(stock_codes) - len(stock_data)}")
    
    if not stock_data:
        return pd.DataFrame(), {}
    
    all_dates = set()
    for df in stock_data.values():
        all_dates |= set(df.index)
    all_dates = sorted(all_dates)
    
    data = []
    for date in all_dates:
        above_count = 0
        valid_count = 0
        for df in stock_data.values():
            if date in df.index:
                valid_count += 1
                if df.loc[date, 'above']:
                    above_count += 1
        
        if valid_count > 0:
            data.append({
                'date': date,
                'above_ratio': above_count / valid_count * 100,
                'above_count': above_count,
                'valid_count': valid_count
            })
    
    history_df = pd.DataFrame(data)
    history_df['date'] = pd.to_datetime(history_df['date'])
    history_df.set_index('date', inplace=True)
    
    if not history_df.empty:
        start_date = history_df.index[0].strftime('%Y-%m-%d')
        end_date = history_df.index[-1].strftime('%Y-%m-%d')
        print(f"历史数据范围: {start_date} 至 {end_date}")
    
    return history_df, stock_data

def build_equal_weight_index(stock_data):
    """构建等权重指数并计算60日均线"""
    if not stock_data:
        return None
    
    all_dates = set()
    for df in stock_data.values():
        all_dates |= set(df.index)
    common_dates = sorted(all_dates)
    
    index_df = pd.DataFrame(index=common_dates)
    
    daily_values = []
    for date in common_dates:
        closes = [df.loc[date, 'close'] for df in stock_data.values() if date in df.index]
        
        if closes:
            daily_value = np.mean(closes)
            daily_values.append(daily_value)
        else:
            daily_values.append(np.nan)
    
    index_df['index_value'] = daily_values
    index_df['index_ma60'] = index_df['index_value'].rolling(window=60, min_periods=1).mean()
    
    return index_df

def plot_index_and_ratio(history_df, index_data):
    """绘制指数走势和60日线比例图，添加鼠标悬停提示"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), sharex=True)
    
    merged_df = pd.merge(history_df, index_data, left_index=True, right_index=True, how='inner')
    
    if not merged_df.empty:
        start_date = merged_df.index[0].strftime('%Y-%m-%d')
        end_date = merged_df.index[-1].strftime('%Y-%m-%d')
        print(f"图表数据范围: {start_date} 至 {end_date}")
    
    # 绘制指数走势和60日均线
    line1, = ax1.plot(merged_df.index, merged_df['index_value'], label='指数值', color='blue', linewidth=1.5)
    line2, = ax1.plot(merged_df.index, merged_df['index_ma60'], label='指数60日均线', color='red', linestyle='--', linewidth=1.5)
    ax1.set_ylabel('指数值')
    ax1.set_title(f'{BLOCK_NAME}板块指数走势')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend()
    
    # 在指数走势图上添加颜色区域背景
    y_min, y_max = ax1.get_ylim()
    
    # 添加填充区域到指数图
    ax1.fill_between(merged_df.index, y_min, y_max, 
                    where=(merged_df['above_ratio'] < BUY_THRESHOLD), 
                    color='green', alpha=0.1, label=f'低于{BUY_THRESHOLD}%')
    ax1.fill_between(merged_df.index, y_min, y_max, 
                    where=((merged_df['above_ratio'] >= BUY_THRESHOLD) & 
                           (merged_df['above_ratio'] <= SELL_THRESHOLD)), 
                    color='yellow', alpha=0.1, label=f'{BUY_THRESHOLD}%-{SELL_THRESHOLD}%')
    ax1.fill_between(merged_df.index, y_min, y_max, 
                    where=(merged_df['above_ratio'] > SELL_THRESHOLD), 
                    color='red', alpha=0.1, label=f'高于{SELL_THRESHOLD}%')
    
    # 恢复原来的y轴范围
    ax1.set_ylim(y_min, y_max)
    
    # 绘制60日线以上比例
    line3, = ax2.plot(merged_df.index, merged_df['above_ratio'], marker='o', linestyle='-', color='purple', 
             linewidth=1.5, markersize=3, label='60日线上比例')
    
    # 添加填充区域到比例图
    ax2.fill_between(merged_df.index, 0, BUY_THRESHOLD, 
                    where=(merged_df['above_ratio'] < BUY_THRESHOLD), 
                    color='green', alpha=0.2, label=f'低于{BUY_THRESHOLD}%')
    ax2.fill_between(merged_df.index, BUY_THRESHOLD, SELL_THRESHOLD, 
                    where=((merged_df['above_ratio'] >= BUY_THRESHOLD) & 
                           (merged_df['above_ratio'] <= SELL_THRESHOLD)), 
                    color='yellow', alpha=0.2, label=f'{BUY_THRESHOLD}%-{SELL_THRESHOLD}%')
    ax2.fill_between(merged_df.index, SELL_THRESHOLD, 100, 
                    where=(merged_df['above_ratio'] > SELL_THRESHOLD), 
                    color='red', alpha=0.2, label=f'高于{SELL_THRESHOLD}%')
    
    ax2.axhline(BUY_THRESHOLD, color='green', linestyle='--', alpha=0.7)
    ax2.axhline(SELL_THRESHOLD, color='red', linestyle='--', alpha=0.7)
    
    ax2.set_xlabel('日期')
    ax2.set_ylabel('比例 (%)')
    ax2.set_title('60日线以上比例')
    ax2.set_ylim(0, 100)
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend(loc='upper right')
    
    # 设置x轴日期格式为年月日
    date_format = mdates.DateFormatter('%Y-%m-%d')
    ax2.xaxis.set_major_formatter(date_format)
    
    # 根据数据量自动调整x轴刻度密度
    num_days = len(merged_df)
    if num_days > 180:  # 超过半年数据
        # 每30天显示一个刻度
        locator = mdates.DayLocator(interval=max(1, num_days // 15))
    elif num_days > 90:  # 超过3个月数据
        # 每15天显示一个刻度
        locator = mdates.DayLocator(interval=max(1, num_days // 10))
    else:
        # 显示所有日期
        locator = mdates.DayLocator(interval=1)
    
    ax2.xaxis.set_major_locator(locator)
    
    # 旋转日期标签避免重叠
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    # 添加鼠标悬停提示功能
    cursor1 = mplcursors.cursor(line1, hover=True)
    cursor2 = mplcursors.cursor(line2, hover=True)
    cursor3 = mplcursors.cursor(line3, hover=True)
    
    # 设置提示内容
    @cursor1.connect("add")
    def on_add1(sel):
        # 将浮点数日期转换为 datetime 对象
        date_obj = num2date(sel.target[0])
        value = sel.target[1]
        sel.annotation.set(text=f"日期: {date_obj.strftime('%Y-%m-%d')}\n指数值: {value:.2f}")
        sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)
    
    @cursor2.connect("add")
    def on_add2(sel):
        date_obj = num2date(sel.target[0])
        value = sel.target[1]
        sel.annotation.set(text=f"日期: {date_obj.strftime('%Y-%m-%d')}\n 60日均线: {value:.2f}")
        sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)
    
    @cursor3.connect("add")
    def on_add3(sel):
        date_obj = num2date(sel.target[0])
        value = sel.target[1]
        # 获取该日期的详细数据
        date_str = date_obj.strftime('%Y-%m-%d')
        if date_str in merged_df.index.strftime('%Y-%m-%d').values:
            # 使用日期字符串找到对应的行
            row = merged_df.loc[merged_df.index.strftime('%Y-%m-%d') == date_str].iloc[0]
            text = (f"日期: {date_str}\n"
                    f"比例: {value:.1f}%\n"
                    f"站上数量: {row['above_count']}/{row['valid_count']}")
            sel.annotation.set(text=text)
            sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)
        else:
            # 如果没有找到，只显示基本数据
            text = (f"日期: {date_str}\n比例: {value:.1f}%")
            sel.annotation.set(text=text)
            sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)
    
    # 保存图片
    filename = f'{BLOCK_NAME}_板块分析_{datetime.now().strftime("%Y%m%d")}.png'
    plt.savefig(filename, dpi=300)
    print(f"图表已保存至: {filename}")
    
    plt.show()

def print_ma60_history(history_df):
    """打印统计结果"""
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

if __name__ == "__main__":
    # 1. 换成沪深300
    stock_codes = get_hs300_codes()

    if not stock_codes:
        print("沪深300成分股获取失败")
        exit()

    test_code = stock_codes
    print(f"\n测试获取股票数据: {test_code}")
    test_df = get_stock_data(test_code, ANALYSIS_DAYS)
    if test_df is not None:
        start_date = test_df.index[0].strftime('%Y-%m-%d')
        end_date = test_df.index[-1].strftime('%Y-%m-%d')
        print(f"测试成功! 获取到 {len(test_df)} 条数据 ({start_date} 至 {end_date})")
    else:
        print(f"测试失败! 无法获取 {test_code} 数据")
    
    history_df, stock_data = calculate_ma60_history(stock_codes, ANALYSIS_DAYS)
    
    if not history_df.empty:
        # 使用增强版打印函数（包含信号检测）
        enhanced_print_ma60_history(history_df)
        index_data = build_equal_weight_index(stock_data)
        if index_data is not None:
            plot_index_and_ratio(history_df, index_data)
    else:
        print("未能生成有效数据，请检查股票代码和数据源")
