import akshare as ak
import pandas as pd
# index_component_sw_df = ak.index_component_sw(symbol="801780")
# pd.option_context('display.max_rows',None)
# print(index_component_sw_df["证券代码"])

# index_component_sw_df = ak.index_component_sw(symbol="801770")
# # 通信
# sorted_df=index_component_sw_df.sort_values("最新权重",ascending=False)
# with pd.option_context('display.max_rows',None):
#     print(sorted_df)
# index_component_sw_df = ak.index_component_sw(symbol="801040")
# # 钢铁
# sorted_df=index_component_sw_df.sort_values("最新权重",ascending=False)
# with pd.option_context('display.max_rows',None):
#     print(sorted_df)

index_component_sw_df = ak.index_component_sw(symbol="801150")
pd.option_context('display.max_rows',None)
print(index_component_sw_df)
