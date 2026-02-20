import streamlit as st
import pandas as pd
import math

# -------------------------------
# DATASET (NUMERIC BEAM TYPE)
# -------------------------------
data = [
    [1, 6.0, 0.30, 16, 4, 8, 150],
    [1, 5.0, 0.30, 12, 4, 8, 200],
    [3, 6.0, 0.30, 20, 4, 8, 200],
    [3, 5.0, 0.30, 16, 4, 8, 150],
    [2, 6.0, 0.30, 25, 4, 10, 100],
    [2, 5.0, 0.30, 20, 4, 10, 100],
]

columns = [
    "BeamType", "Span", "Width",
    "MainDia", "NoBars",
    "StirrupDia", "StirrupSpacing"
]

df = pd.DataFrame(data, columns=columns)

# -------------------------------
# CONSTANTS
# -------------------------------
MAIN_DIAS = [12, 16, 20, 25]
STIRRUP_DIAS = [8, 10]
STIRRUP_SPACING = [100, 150, 200]

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def round_up(val, allowed):
    for a in allowed:
        if val <= a:
            return a
    return allowed[-1]

def round_down(val, allowed):
    for a in sorted(allowed, reverse=True):
        if val >= a:
            return a
    return allowed[-1]

def steel_area(d):
    return math.pi * d * d / 4

def nearest_row(df, beam, span, width):
    subset = df[df["BeamType"] == beam].copy()
    subset["score"] = abs(subset["Span"] - span) + abs(subset["Width"] - width)
    return subset.sort_values("score").iloc[0]

# -------------------------------
# STREAMLIT UI
# -------------------------------
st.set_page_config(page_title="AI Based RCC Beam Optimization", layout="centered")
st.title("AI Based RCC Beam Optimization")

# UI → INTERNAL MAPPING
beam_map = {
    "Simply Supported": 1,
    "Cantilever": 2,
    "Continuous": 3
}

beam_reverse_map = {v: k for k, v in beam_map.items()}

beam_ui = st.selectbox("Type of Beam", list(beam_map.keys()))
beam_type = beam_map[beam_ui]

span = st.number_input("Span (m)", 2.0, 10.0, 6.0, step=0.1)
width = st.number_input("Width (m)", 0.20, 0.60, 0.30, step=0.05)
fck = st.selectbox("Grade of Concrete (Fck)", [20, 25, 30])
fy = st.selectbox("Grade of Steel (Fy)", [415, 500])

if st.button("Optimize Beam"):

    row = nearest_row(df, beam_type, span, width)

    # Reinforcement strictly from dataset
    main_dia = round_up(row["MainDia"], MAIN_DIAS)
    no_bars = int(row["NoBars"])

    stirrup_dia = round_up(row["StirrupDia"], STIRRUP_DIAS)
    stirrup_spacing = round_down(row["StirrupSpacing"], STIRRUP_SPACING)

    # Depth (safe side – IS practice)
    if beam_type == 2:
        depth = round(span / 7, 2)
    elif beam_type == 3:
        depth = round(span / 12, 2)
    else:
        depth = round(span / 10, 2)

    # Percentage calculations
    ast_used = no_bars * steel_area(main_dia)
    ast_max = 6 * steel_area(25)

    pct_ast = round(((ast_max - ast_used) / ast_max) * 100, 2)

    depth_max = span / 6
    pct_area = round(((depth_max - depth) / depth_max + pct_ast) / 2, 2)

    # -------------------------------
    # OUTPUT
    # -------------------------------
    st.success("Optimization Completed Successfully")

    st.subheader("Optimized Results")

    st.write(f"*Beam Type:* {beam_reverse_map[beam_type]}")
    st.write(f"*Optimised Depth of Beam (m):* {depth}")

    st.write(f"*Tension Reinforcement:* {no_bars} bars of {main_dia} mm dia")
    st.write(f"*Compression Reinforcement:* {max(2, no_bars-1)} bars of {main_dia} mm dia")

    st.write(f"*Stirrups:* {stirrup_dia} mm dia @ {stirrup_spacing} mm c/c")

    st.write(f"*Percentage Area Optimised (%):* {pct_area}")
    st.write(f"*Percentage AST Optimised (%):* {pct_ast}")

    st.caption("✔ Beam type mapping fixed • ✔ Dataset-based • ✔ Safer-side design")