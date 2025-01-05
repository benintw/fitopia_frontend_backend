"""Reusable UI components"""

import streamlit as st
from typing import Optional


def show_success(message: str):
    st.success(message)


def show_error(message: str):
    st.error(message)


def data_table(data, columns: Optional[list] = None):
    """Reusable data table component with consistent styling"""
    if columns:
        data = data[columns]
    st.dataframe(data, use_container_width=True, hide_index=True)


def confirmation_dialog(message: str) -> bool:
    """Reusable confirmation dialog"""
    return st.warning(message, icon="⚠️")
