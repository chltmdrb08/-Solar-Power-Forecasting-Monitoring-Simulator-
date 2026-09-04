import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="태양광 발전 시뮬레이터", page_icon="☀️", layout="wide"
)

st.title("☀️ 태양광 발전량 예측 및 모니터링 시뮬레이터")
st.caption(
    "전기전자공학부 - 신재생에너지 전력 변환 시뮬레이션 프로젝트"
)

# 사이드바: 입력 매개변수 설정
st.sidebar.header("⚙️ 시스템 매개변수 설정")
panel_area = st.sidebar.number_input(
    "패널 면적 (m²)", min_value=1.0, max_value=500.0, value=20.0, step=1.0
)
base_efficiency = (
    st.sidebar.slider(
        "기본 패널 효율 (%)",
        min_value=5.0,
        max_value=30.0,
        value=20.0,
        step=0.5,
    )
    / 100
)
max_irradiance = st.sidebar.slider(
    "최대 일조량 (W/m²)",
    min_value=200,
    max_value=1200,
    value=800,
    step=50,
)
peak_temp = st.sidebar.slider(
    "최고 기온 (°C)", min_value=0, max_value=45, value=30, step=1
)

# 시간 데이터 (0시 ~ 23시)
hours = np.arange(24)

# 일조량 및 기온 시간대별 프로필 생성 (가상의 햇빛 곡선)
irradiance = np.maximum(
    0, max_irradiance * np.sin(np.pi * (hours - 6) / 12)
)  # 6시~18시 일출/일몰
temperature = 15 + (peak_temp - 15) * np.sin(np.pi * (hours - 8) / 12)
temperature = np.maximum(10, temperature)

# 온도가 25도를 초과할 때 효율 감소 (태양광 패널 온도 계수: -0.4%/°C)
temp_loss = np.maximum(0, (temperature - 25) * 0.004)
adjusted_efficiency = base_efficiency * (1 - temp_loss)

# 시간당 발전량 산출 (kW) = 일조량(W/m²) * 면적(m²) * 조정 효율 / 1000
power_kw = (irradiance * panel_area * adjusted_efficiency) / 1000
total_energy_kwh = np.sum(power_kw)

# 데이터프레임 구성
df = pd.DataFrame(
    {
        "시간 (시)": hours,
        "일조량 (W/m²)": np.round(irradiance, 1),
        "기온 (°C)": np.round(temperature, 1),
        "발전량 (kW)": np.round(power_kw, 2),
    }
)

# 대시보드 상단 메트릭
col1, col2, col3 = st.columns(3)
col1.metric("하루 총 누적 발전량", f"{total_energy_kwh:.2f} kWh")
col2.metric("최대 피크 출력", f"{np.max(power_kw):.2f} kW")
col3.metric("평균 온도 손실율", f"{np.mean(temp_loss)*100:.2f} %")

st.markdown("---")

# 시각화 그래프
st.subheader("📈 시간대별 일조량 및 발전량 추이")
fig = px.line(
    df,
    x="시간 (시)",
    y=["일조량 (W/m²)", "발전량 (kW)"],
    markers=True,
    title="24시간 발전 프로필 시뮬레이션",
)
st.plotly_chart(fig, use_container_width=True)

# 데이터 테이블 출력
with st.expander("📊 세부 데이터 보기"):
    st.dataframe(df, use_container_width=True)
