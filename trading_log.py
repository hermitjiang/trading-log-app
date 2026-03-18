import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import os

# 页面配置
st.set_page_config(page_title="每日交易记录", page_icon="📈", layout="wide")

# ---------------------- 核心：文件存储 ----------------------
LOG_FILE = "trading_logs.json"

def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_logs(logs):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)

all_logs = load_logs()

# ---------------------- 日期切换逻辑 ----------------------
st.sidebar.title("📅 日志日期选择")

# 1. 日历组件
selected_date = st.sidebar.date_input("选择日期", value=date.today(), key="date_picker")
date_key = selected_date.strftime("%Y.%m.%d")

# 2. 历史日志下拉框
st.sidebar.divider()
st.sidebar.subheader("📜 历史日志")
history_dates = sorted(all_logs.keys(), reverse=True)

if history_dates:
    selected_history = st.sidebar.selectbox("快速选择", options=history_dates, key="history_select")

    if st.sidebar.button("🔍 切换到该日期"):
        date_key = selected_history
else:
    st.sidebar.info("暂无历史日志")

# 3. 删除按钮
if st.sidebar.button("🗑️ 删除当前日志", type="secondary"):
    if date_key in all_logs:
        del all_logs[date_key]
        save_logs(all_logs)
        st.sidebar.success(f"已删除 {date_key}")
        st.rerun()

# ---------------------- 初始化日志（空白默认值） ----------------------
# 关键修改：把所有默认文字改成空字符串
default_log = {
    "feel_word": "",
    "mood_score": 0,
    "opportunity_score": 0,
    "stop_loss": "",
    "max_limit": "",
    "target_profit_loss": "",
    "today_activity": "",
    "today_plan": "",
    "personal_affair": "",
    "empty_position_note": "",
    "price_data": [
        ["", 0.00, 0.00, 0.00, 0.00, 0.00],
        ["", 0.00, 0.00, 0.00, 0.00, 0.00],
        ["", 0.00, 0.00, 0.00, 0.00, 0.00]
    ]
}

if date_key not in all_logs:
    all_logs[date_key] = default_log

current_log = all_logs[date_key]

# ---------------------- 主界面 ----------------------
col_title, col_date = st.columns([3, 1])
with col_title:
    st.title("每日交易记录")
with col_date:
    st.title(f"📅 {date_key}")

st.divider()

# 感受/指数
col1, col2, col3 = st.columns([2, 1, 2])
with col1:
    current_log["feel_word"] = st.text_input("用一个词形容今天", value=current_log["feel_word"])
    current_log["mood_score"] = st.number_input("情绪指数（0-10）", min_value=0, max_value=10, value=int(current_log["mood_score"]))
    current_log["opportunity_score"] = st.number_input("机会质量（0-10）", min_value=0, max_value=10, value=int(current_log["opportunity_score"]))

with col3:
    current_log["stop_loss"] = st.text_input("今日止损", value=current_log["stop_loss"])
    current_log["target_profit_loss"] = st.text_input("目标盈亏", value=current_log["target_profit_loss"])
    current_log["max_limit"] = st.text_input("最高限额", value=current_log["max_limit"])

st.divider()

st.subheader("今天的活动")
current_log["today_activity"] = st.text_area("", value=current_log["today_activity"], height=60)

st.subheader("今天的计划")
current_log["today_plan"] = st.text_area("", value=current_log["today_plan"], height=100)

st.subheader("个人事务")
current_log["personal_affair"] = st.text_area("", value=current_log["personal_affair"], height=60)

st.divider()

st.subheader("关键价位")
price_df = pd.DataFrame(
    current_log["price_data"],
    columns=["标的", "支撑2", "支撑1", "最新价", "阻力1", "阻力2"]
)

edited_price_df = st.data_editor(
    price_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "支撑2": st.column_config.NumberColumn(format="%.2f"),
        "支撑1": st.column_config.NumberColumn(format="%.2f"),
        "最新价": st.column_config.NumberColumn(format="%.2f"),
        "阻力1": st.column_config.NumberColumn(format="%.2f"),
        "阻力2": st.column_config.NumberColumn(format="%.2f"),
    }
)
current_log["price_data"] = edited_price_df.values.tolist()

st.divider()

current_log["empty_position_note"] = st.text_input("空仓提示", value=current_log["empty_position_note"])
st.markdown(f"<h3 style='text-align:center;'>{current_log['empty_position_note']}</h3>", unsafe_allow_html=True)

# ---------------------- 保存 ----------------------
st.divider()
if st.button("💾 保存日志", type="primary"):
    all_logs[date_key] = current_log
    save_logs(all_logs)
    st.success(f"✅ 已保存 {date_key} 的日志")

# 导出
def make_csv():
    basic = pd.DataFrame({
        "日期": [date_key],
        "感受": [current_log["feel_word"]],
        "情绪": [current_log["mood_score"]],
        "机会质量": [current_log["opportunity_score"]],
        "止损": [current_log["stop_loss"]],
        "限额": [current_log["max_limit"]],
        "目标": [current_log["target_profit_loss"]],
        "活动": [current_log["today_activity"]],
        "计划": [current_log["today_plan"]],
        "事务": [current_log["personal_affair"]],
        "空仓": [current_log["empty_position_note"]]
    })
    csv_all = basic.to_csv(index=False, encoding="utf-8-sig") + "\n" + edited_price_df.to_csv(index=False, encoding="utf-8-sig")
    return csv_all

st.download_button(
    "📤 导出CSV",
    data=make_csv(),
    file_name=f"交易日志_{date_key}.csv",
    mime="text/csv"
)