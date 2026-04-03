"""Shared UI helpers for consistent styling across pages."""
import streamlit as st
import plotly.graph_objects as go
from pathlib import Path

# Design tokens
NAVY = "#1E3A5F"
NAVY_LIGHT = "#2D5986"
TEXT_PRIMARY = "#1A1A2E"
TEXT_SECONDARY = "#6B7280"
BORDER = "#E2E5E9"
SURFACE = "#FAFBFC"
GRID = "#F0F0F0"
GREEN = "#059669"
RED = "#DC2626"
GRAY = "#9CA3AF"

CHART_COLORS = [NAVY, "#4A90D9", "#7CB4E8", "#2D8B5C", "#D97B4A", "#8B5CD9"]


def load_css():
    css_path = Path(__file__).parent.parent / "assets" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def apply_chart_style(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="system-ui, -apple-system, sans-serif", size=12, color=TEXT_SECONDARY),
        title=dict(font=dict(size=14, color=TEXT_PRIMARY), x=0, xanchor="left"),
        xaxis=dict(gridcolor=GRID, linecolor=BORDER, showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=GRID, linecolor=BORDER, showgrid=True, zeroline=False),
        margin=dict(l=50, r=20, t=50, b=40),
        hovermode="x unified",
        height=height,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(size=11), bgcolor="rgba(0,0,0,0)",
        ),
    )
    return fig


def show_chart(fig: go.Figure):
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def page_header(title: str, description: str = ""):
    st.title(title)
    if description:
        st.caption(description)
    st.markdown("---")
