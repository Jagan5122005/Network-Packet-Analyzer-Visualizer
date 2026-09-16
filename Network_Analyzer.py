import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import random

st.set_page_config(page_title="Advanced Network Packet Analyzer v2.0", layout="wide")

st.title("🌐 Advanced Network Packet Analyzer & Telemetry Dashboard v2.0")
st.markdown("Real-time Network Traffic Monitoring, Threat Detection, and Protocol Analytics")

# Session State Initialization
if 'packets' not in st.session_state:
    st.session_state.packets = []
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# Sidebar Controls
st.sidebar.header("⚙️ Traffic Controls & Filters")
if st.sidebar.button("▶️ Start Live Monitoring"):
    st.session_state.is_running = True
if st.sidebar.button("⏹️ Stop Monitoring"):
    st.session_state.is_running = False

protocol_filter = st.sidebar.multiselect(
    "Filter by Protocol:",
    options=["TCP", "UDP", "ICMP", "ARP"],
    default=["TCP", "UDP", "ICMP", "ARP"]
)


# Packet Generator Function
def generate_synthetic_packet():
    protocols = ["TCP", "UDP", "ICMP", "ARP"]
    sources = [f"192.168.1.{i}" for i in range(2, 20)] + ["10.0.0.5", "172.16.0.12"]
    destinations = ["192.168.1.1", "8.8.8.8", "1.1.1.1", "142.250.190.46"]

    proto = random.choices(protocols, weights=[0.5, 0.3, 0.1, 0.1])[0]
    src = random.choice(sources)
    dst = random.choice(destinations)
    length = random.randint(64, 1500)

    # Anomaly condition simulation
    is_threat = False
    if proto == "ICMP" and length > 1200:
        is_threat = True
    elif proto == "UDP" and random.random() < 0.05:
        is_threat = True

    return {
        "Timestamp": time.strftime("%H:%M:%S"),
        "Source IP": src,
        "Destination IP": dst,
        "Protocol": proto,
        "Length (Bytes)": length,
        "Threat Alert": "⚠️ Suspicious Activity" if is_threat else "✅ Normal"
    }


# Dashboard Placeholders
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
chart_col1, chart_col2 = st.columns(2)
alert_placeholder = st.empty()
data_placeholder = st.empty()

# Real-time Engine Loop
if st.session_state.is_running:
    new_packet = generate_synthetic_packet()
    st.session_state.packets.append(new_packet)
    if len(st.session_state.packets) > 100:
        st.session_state.packets.pop(0)

# Data Processing
df = pd.DataFrame(st.session_state.packets)

if not df.empty:
    # Filter Data
    filtered_df = df[df["Protocol"].isin(protocol_filter)]

    # Calculate Live Metrics
    total_packets = len(df)
    tcp_count = len(df[df["Protocol"] == "TCP"])
    udp_count = len(df[df["Protocol"] == "UDP"])
    threat_count = len(df[df["Threat Alert"] != "✅ Normal"])

    metric_col1.metric("Total Packets", total_packets)
    metric_col2.metric("TCP Packets", tcp_count)
    metric_col3.metric("UDP Packets", udp_count)
    metric_col4.metric("Security Alerts", threat_count, delta_color="inverse")

    # Threat Alert Box
    if threat_count > 0:
        alert_placeholder.warning(f"🚨 Security System Alert: {threat_count} anomalous network packets detected!")
    else:
        alert_placeholder.success("🛡️ System Secure: Network telemetry operating within normal parameters.")

    # Charts
    with chart_col1:
        st.subheader("Protocol Distribution")
        fig_pie = px.pie(filtered_df, names="Protocol", hole=0.4, title="Protocol Breakdown")
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        st.subheader("Bandwidth Gauge (Bytes/Packet)")
        avg_bandwidth = filtered_df["Length (Bytes)"].mean() if not filtered_df.empty else 0
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_bandwidth,
            title={'text': "Avg Packet Size (Bytes)"},
            gauge={
                'axis': {'range': [0, 1500]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 500], 'color': "lightcyan"},
                    {'range': [500, 1000], 'color': "royalblue"},
                    {'range': [1000, 1500], 'color': "red"}
                ]
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

    # Data Table & CSV Export
    st.subheader("Live Packet Inspection Stream")
    data_placeholder.dataframe(filtered_df.tail(10), use_container_width=True)

    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Export Packet Logs (CSV)",
        data=csv_data,
        file_name="network_packet_logs.csv",
        mime="text/csv"
    )

if st.session_state.is_running:
    time.sleep(1)
    st.rerun()