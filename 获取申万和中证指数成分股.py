

import akshare as ak
import pandas as pd
index_component_sw_df = ak.index_component_sw(symbol="801780")
pd.option_context('display.max_rows',None)
print(index_component_sw_df["证券代码"])
import akshare as ak
# 获取沪深三百成分股
index_stock_cons_df = ak.index_stock_cons(symbol="000300")
print(index_stock_cons_df)
# 获取上证50成分股

index_stock_cons_df = ak.index_stock_cons(symbol="000016")
print(index_stock_cons_df)

# 获取中证500成分股
index_stock_cons_df = ak.index_stock_cons(symbol="000905")
print(index_stock_cons_df)
# 获取创业板指成分股
index_stock_cons_df = ak.index_stock_cons(symbol="399006")
print(index_stock_cons_df)
# 399303	国证2000
# 399305	基金指数
# # 399311	国证1000、
# 399403	防御100	2013/10/28
# 399404	大盘低波	2013/12/5
# 399405	大盘高贝	2013/12/5
# 399406	中盘低波	2013/12/5
# 399407	中盘高贝	2013/12/5
# 399408	小盘低波	2013/12/5
# 399409	小盘高贝	2013/12/5
# 399997	中证白酒指数399982	中证500等权重指数	2011/6/13
# 399983	沪深300地产等权重指数	2013/11/22
# 399984	沪深300等权重指数	2011/8/2
# 399985	中证全指指数	2011/8/2
# 399986	中证银行指数	2013/7/15
# 399987	中证酒指数	2014/12/10
# 399989	中证医疗指数	2014/10/31
# 399990	中证煤炭等权指数	2015/1/21
# 399991	中证一带一路主题指数	2015/2/16
# 399992	中证万得并购重组指数	2015/5/8
# 399993	中证万得生物科技指数	2015/5/8
# 399994	中证信息安全主题指数	2015/3/12
# 399995	中证基建工程指数	2015/3/12
# 399996	中证智能家居指数	2014/9/17
# 399997	中证白酒指数	2015/1/21
# 399998	中证煤炭指数	2015/2/13
