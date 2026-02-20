import streamlit as st
import pandas as pd
import numpy as np
import math

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="AI Based RCC Beam Optimization",
    layout="centered"
)

st.title("AI Based RCC Beam Optimization")

# -------------------------------
# LOAD DATASET
# -------------------------------
import os
DATA_PATH = os.path.join(os.getcwd(), "data.xlsx")
df = pd.read_excel(DATA_PATH)

# -------------------------------
# CONSTANTS (DATASET RULES)
# -------------------------------
MAIN_DIAS = [12, 16, 20, 25]
STIRRUP_DIAS = [8, 10]
STIRRUP_SPACING = [100, 150, 200]

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def round_up(value, allowed):
    for a in allowed:
        if value <= a:
            return a
    return allowed[-1]

def round_down(value, allowed):
    for a in sorted(allowed, reverse=True):
        if value >= a:
            return a
    return allowed[-1]

def steel_area(dia):
    return math.pi * dia * dia / 4

def nearest_row(df, beam_type, span, width):
    subset = df[df["TYPEOFBEAM"] == beam_type].copy()
    if subset.empty:
        return None
    subset["diff"] = abs(subset["SPAN"] - span) + abs(subset["WIDTH"] - width)
    return subset.sort_values("diff").iloc[0]

# -------------------------------
# INPUTS
# -------------------------------
beam_label = st.selectbox(
    "Type of Beam",
    ["Simply Supported", "Cantilever", "Continuous"]
)

beam_map = {
    "Simply Supported": 1,
    "Cantilever": 2,
    "Continuous": 3
}
beam_type = beam_map[beam_label]

span = st.number_input("Span (m)", min_value=1.0, max_value=10.0, value=6.0, step=0.1)
width = st.number_input("Width (m)", min_value=0.20, max_value=0.60, value=0.30, step=0.01)

# Concrete dropdown
fck_label = st.selectbox(
    "Grade of Concrete (Fck)",
    ["M20", "M30", "M40"]
)
fck = int(fck_label.replace("M", ""))

# Steel dropdown
fy_label = st.selectbox(
    "Grade of Steel (Fy)",
    ["Fe250", "Fe415", "Fe500"]
)
fy = int(fy_label.replace("Fe", ""))

# -------------------------------
# BUTTON
# -------------------------------
if st.button("Optimize Beam"):

    row = nearest_row(df, beam_type, span, width)

    if row is None:
        st.error("No matching row found in dataset")
    else:
        # -------------------------------
        # DEPTH (SAFE-SIDE RULE)
        # -------------------------------
        if beam_type == 1:      # Simply supported
            depth = round(span / 10, 2)
        elif beam_type == 2:    # Cantilever
            depth = round(span / 7, 2)
        else:                   # Continuous
            depth = round(span / 12, 2)

        # -------------------------------
        # REINFORCEMENT (STRICT DATASET)
        # -------------------------------
        tension_bars = int(row["NOOFBARSINTENSION"])
        comp_bars = int(row["NOOFBARSINCOMPRESSION"])

        tension_dia = round_up(row["TENSIONDIA"], MAIN_DIAS)
        comp_dia = round_up(row["COMPRESSIONDIA"], MAIN_DIAS)

        # -------------------------------
        # STIRRUPS (SAFE SIDE)
        # -------------------------------
        stirrup_dia = round_up(row["STIRRUPDIA"], STIRRUP_DIAS)
        stirrup_spacing = round_down(row["STIRRUPSSPACING"], STIRRUP_SPACING)

        # -------------------------------
        # PERCENTAGE CALCULATIONS
        # -------------------------------
        ast_used = tension_bars * steel_area(tension_dia)
        ast_max = 6 * steel_area(25)

        pct_ast = round(((ast_max - ast_used) / ast_max) * 100, 2)

        depth_max = span / 6
        pct_area = round(((depth_max - depth) / depth_max) * 100, 2)

        # -------------------------------
        # OUTPUT
        # -------------------------------
        st.success("Optimization Completed Successfully")

        st.subheader("Optimized Results")
        st.write(f"*Beam Type:* {beam_label}")
        st.write(f"*Optimised Depth of Beam (m):* {depth}")

        st.write(
            f"*Tension Reinforcement:* {tension_bars} bars of {tension_dia} mm dia"
        )
        st.write(
            f"*Compression Reinforcement:* {comp_bars} bars of {comp_dia} mm dia"
        )
        st.write(
            f"*Stirrups:* {stirrup_dia} mm dia @ {stirrup_spacing} mm c/c"
        )

        st.write(f"*Percentage Area Optimised (%):* {pct_area}")
        st.write(f"*Percentage AST Optimised (%):* {pct_ast}")

        st.caption("All values strictly as per dataset & safer-side design rules")

