import streamlit as st
import pandas as pd
import plotly.express as px
import random
import time

st.set_page_config(page_title="Visual Network Packet Analyzer", layout="wide")

if 'packet_data' not in st.session_state:
    st.session_state.packet_data = []
if 'capturing' not in st.session_state:
    st.session_state.capturing = False

sample_ips = ["192.168.1.1", "192.168.1.15", "10.0.0.4", "172.16.0.1", "8.8.8.8"]
protocols = ["TCP", "UDP", "ICMP", "ARP"]


def generate_simulated_packet():
    return {
        "Timestamp": time.strftime("%H:%M:%S"),
        "Source": random.choice(sample_ips),
        "Destination": random.choice(sample_ips),
        "Protocol": random.choice(protocols),
        "Length": random.randint(64, 1500)
    }


st.title("📡 Visual Network Packet Analyzer & Visualizer")
st.caption("Real-Time OSI Layer & Protocol Sniffer Dashboard")

col_btn1, col_btn2, col_btn3 = st.columns(3)

if col_btn1.button("▶️ Start Live Capture"):
    st.session_state.capturing = True

if col_btn2.button("⏹️ Stop Capture"):
    st.session_state.capturing = False

if col_btn3.button("🗑️ Clear Logs"):
    st.session_state.packet_data = []
    st.rerun()

if st.session_state.capturing:
    for _ in range(random.randint(2, 5)):
        st.session_state.packet_data.append(generate_simulated_packet())
    time.sleep(0.8)
    st.rerun()

if st.session_state.packet_data:
    df = pd.DataFrame(st.session_state.packet_data)

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Packets Captured", len(df))
    m2.metric("Unique Sources", df['Source'].nunique())
    m3.metric("Top Protocol", df['Protocol'].mode()[0] if not df.empty else "N/A")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Protocol Distribution")
        fig_pie = px.pie(df, names='Protocol', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        st.subheader("Packet Size Breakdown")
        fig_bar = px.histogram(df, x="Protocol", y="Length", histfunc="sum", color="Protocol")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("📋 Raw Packet Inspector Table")
    st.dataframe(df.tail(20), use_container_width=True)
else:
    st.info("Click 'Start Live Capture' to begin inspecting network traffic.")