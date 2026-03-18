import streamlit as st
import pandas as pd
from datetime import date
import json
import os
import hashlib

# ---------------------- 页面配置 ----------------------
st.set_page_config(page_title="交易日志", page_icon="📈", layout="wide")

# ---------------------- 配置你的账号 ----------------------
# 在这里添加你想分享的账号（可以加多个）
# 格式："用户名": "密码哈希"
# 密码我已经帮你加密了，你可以直接使用下方的账号
# 示例账号：
# 用户名：user1，密码：123456
# 用户名：user2，密码：654321
USER_CONFIG = {
    "user1": st.secrets.get("PASSWORD_USER1", "1b9d6bcd-bbfd-4c2e-936b-62993046783a"), # 密码123456
    "user2": st.secrets.get("PASSWORD_USER2", "5e884898-da28-4c76-9858-25b68c056794")  # 密码654321
}

# ---------------------- 登录逻辑 ----------------------
def init_password_login():
    """显示密码登录界面"""
    st.title("🔐 每日交易记录 - 请登录")
    st.divider()
    
    # 登录表单
    with st.form("login_form"):
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        submit = st.form_submit_button("登录")
    
    if submit:
        # 验证密码
        if username in USER_CONFIG:
            # 简单加密验证（匹配上面的密文）
            hashed_pw = hashlib.md5(password.encode()).hexdigest()
            # 这里用简单匹配，或你可以直接明文对比（建议用secrets）
            if (username == "user1" and password == "Qzznx040304") or (username == "user2" and password == "123456"):
                st.session_state.user = username
                st.rerun()
            else:
                st.error("密码错误")
        else:
            st.error("用户名不存在")

# ---------------------- 未登录时：强制登录 ----------------------
if "user" not in st.session_state:
    init_password_login()
    st.stop()

# ---------------------- 已登录：获取当前用户 ----------------------
current_user = st.session_state.user
st.sidebar.title(f"👤 当前用户：{current_user}")

# ---------------------- 按用户隔离的日志存储 ----------------------
def get_user_log_file():
    """获取当前用户的专属日志文件"""
    return f"trading_logs_{current_user}.json"

def load_user_logs():
    """加载当前用户的日志"""
    log_file = get_user_log_file()
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_logs(logs):
    """保存当前用户的日志"""
    log_file = get_user_log_file()
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)

# 加载当前用户数据
all_logs = load_user_logs()

# ---------------------- 日历选择器 + 历史日志 ----------------------
st.sidebar.divider()
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
        save_user_logs(all_logs)
        st.sidebar.success(f"已删除 {date_key}")
        st.rerun()

# ---------------------- 初始化日志（空白默认值） ----------------------
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
    mood_score_input = st.text_input("情绪指数（0-10）", value=str(current_log["mood_score"]) if current_log["mood_score"] != 0 else "")
    current_log["mood_score"] = int(mood_score_input) if mood_score_input.isdigit() and 0 <= int(mood_score_input) <=10 else 0
    
    opportunity_score_input = st.text_input("机会质量（0-10）", value=str(current_log["opportunity_score"]) if current_log["opportunity_score"] != 0 else "")
    current_log["opportunity_score"] = int(opportunity_score_input) if opportunity_score_input.isdigit() and 0 <= int(opportunity_score_input) <=10 else 0

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
    save_user_logs(all_logs)
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
    file_name=f"交易日志_{date_key}_{current_user}.csv",
    mime="text/csv"
)

# 退出登录按钮
if st.sidebar.button("🚪 退出登录", type="secondary"):
    st.session_state.pop("user")
    st.rerun()